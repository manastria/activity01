// tools/build-images.mjs (ESM)
import fg from 'fast-glob';
import path from 'node:path';
import fs from 'node:fs/promises';
import sharp from 'sharp';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const PUBLIC_IMAGES_DIR = path.resolve(ROOT, 'public', 'images');
const MANIFEST_DST = path.resolve(ROOT, 'src', 'data', 'images.manifest.json');

// Options
const THUMB_HEIGHT = Number(process.env.THUMB_HEIGHT || 120);
const QUALITY_WEBP = Number(process.env.QUALITY_WEBP || 82);
const QUALITY_AVIF = Number(process.env.QUALITY_AVIF || 45);
const SIZE_WIN_THRESHOLD = 0.90; // garder AVIF/WebP seulement si < 90% de l'original

const pattern = `${PUBLIC_IMAGES_DIR.replaceAll('\\','/')}/**/*.{jpg,jpeg,png}`;

function relFromPublic(p) {
  return '/' + path.relative(path.resolve(ROOT, 'public'), p).replaceAll('\\', '/');
}

async function fileSize(p) {
  return (await fs.stat(p)).size;
}

async function ensureDir(d) {
  await fs.mkdir(d, { recursive: true });
}

async function generateFullVariants(absPath) {
  // Retourne { bestOf: { avif?, webp?, fallback }, created: { avif?, webp? } }
  const dir = path.dirname(absPath);
  const base = path.basename(absPath);
  const stem = base.replace(/\.[^.]+$/, '');

  const outAvif = path.join(dir, `${stem}.avif`);
  const outWebp = path.join(dir, `${stem}.webp`);

  const origSize = (await fs.stat(absPath)).size;

  const created = { avif: null, webp: null };
  let keepAvif = false, keepWebp = false;

  // AVIF
  try {
    const avifBuf = await sharp(absPath).avif({ quality: QUALITY_AVIF }).toBuffer();
    if (avifBuf.byteLength < origSize * SIZE_WIN_THRESHOLD) {
      await fs.writeFile(outAvif, avifBuf);
      keepAvif = true;
      created.avif = outAvif;
    } else {
      try { await fs.unlink(outAvif); } catch {}
    }
  } catch (e) {
    console.warn(`AVIF failed for ${absPath}: ${e.message}`);
  }

  // WebP
  try {
    const webpBuf = await sharp(absPath).webp({ quality: QUALITY_WEBP }).toBuffer();
    if (webpBuf.byteLength < origSize * SIZE_WIN_THRESHOLD) {
      await fs.writeFile(outWebp, webpBuf);
      keepWebp = true;
      created.webp = outWebp;
    } else {
      try { await fs.unlink(outWebp); } catch {}
    }
  } catch (e) {
    console.warn(`WebP failed for ${absPath}: ${e.message}`);
  }

  return {
    bestOf: {
      avif: keepAvif ? relFromPublic(outAvif) : null,
      webp: keepWebp ? relFromPublic(outWebp) : null,
      fallback: relFromPublic(absPath)
    },
    created
  };
}

async function generateThumbs(absPath) {
  // Toujours produire thumbs AVIF & WebP (petites, donc utiles)
  const dir = path.dirname(absPath);
  const base = path.basename(absPath);
  const stem = base.replace(/\.[^.]+$/, '');
  const outThumbAvif = path.join(dir, `${stem}.thumb.avif`);
  const outThumbWebp = path.join(dir, `${stem}.thumb.webp`);

  try {
    await sharp(absPath)
      .resize({ height: THUMB_HEIGHT, withoutEnlargement: true })
      .avif({ quality: QUALITY_AVIF })
      .toFile(outThumbAvif);
  } catch (e) {
    console.warn(`Thumb AVIF failed for ${absPath}: ${e.message}`);
  }

  try {
    await sharp(absPath)
      .resize({ height: THUMB_HEIGHT, withoutEnlargement: true })
      .webp({ quality: QUALITY_WEBP })
      .toFile(outThumbWebp);
  } catch (e) {
    console.warn(`Thumb WebP failed for ${absPath}: ${e.message}`);
  }

  const thumb = {
    avif: (await exists(outThumbAvif)) ? relFromPublic(outThumbAvif) : null,
    webp: (await exists(outThumbWebp)) ? relFromPublic(outThumbWebp) : null
  };
  return thumb;
}

async function exists(p) {
  try { await fs.access(p); return true; } catch { return false; }
}

async function buildOnce() {
  await ensureDir(path.dirname(MANIFEST_DST));

  const files = await fg(pattern, {
    dot: false,
    ignore: ['**/_inbox/**']
  });

  const manifest = {}; // key: original (web path, ex: /images/win/etape1.png)

  for (const absPath of files) {
    const originalWeb = relFromPublic(absPath);

    // Full variants
    const full = await generateFullVariants(absPath);

    // Thumbs
    const thumb = await generateThumbs(absPath);

    manifest[originalWeb] = {
      full: {
        avif: full.bestOf.avif,
        webp: full.bestOf.webp,
        fallback: full.bestOf.fallback
      },
      thumb: {
        avif: thumb.avif,
        webp: thumb.webp,
        // Fallback thumb : si aucune n’a été générée, on s’appuie sur CSS côté composant
        fallback: null
      }
    };
  }

  await fs.writeFile(MANIFEST_DST, JSON.stringify(manifest, null, 2));
  console.log(`✓ Images build done. Manifest: ${path.relative(ROOT, MANIFEST_DST)}`);
}

async function main() {
  if (!(await exists(PUBLIC_IMAGES_DIR))) {
    console.error(`No directory ${PUBLIC_IMAGES_DIR}. Create public/images and add JPG/PNG.`);
    process.exit(1);
  }

  if (process.argv.includes('--watch')) {
    const { watch } = await import('node:fs');
    await buildOnce();
    console.log('Watching images...');
    const watcher = watch(PUBLIC_IMAGES_DIR, { recursive: true });
    watcher.on('change', async () => {
      // petit debounce
      setTimeout(() => buildOnce().catch(console.error), 120);
    });
  } else {
    await buildOnce();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
