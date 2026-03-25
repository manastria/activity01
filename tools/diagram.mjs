#!/usr/bin/env node
/**
 * tools/diagram.mjs
 *
 * Gestion des diagrammes draw.io liés aux fichiers MDX.
 *
 * Usage:
 *   node tools/diagram.mjs new <mdx-file> <diagram-name>
 *   node tools/diagram.mjs export [<mdx-file>]
 *
 * Exemples:
 *   node tools/diagram.mjs new src/content/docs/fiches/sns-ordonnancement-filtrage-nat.mdx topologie
 *   node tools/diagram.mjs export src/content/docs/fiches/sns-ordonnancement-filtrage-nat.mdx
 *   node tools/diagram.mjs export   # exporte tous les diagrammes
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// Template draw.io minimal
const DRAWIO_TEMPLATE = `<mxfile host="app.diagrams.net">
  <diagram name="Page-1">
    <mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
`;

/**
 * Dérive les chemins depuis un fichier MDX.
 * src/content/docs/fiches/mon-slug.mdx
 *   → diagrams : src/diagrams/fiches/mon-slug/
 *   → images   : public/images/fiches/mon-slug/
 *
 * src/content/docs/activities/mon-slug/index.mdx
 *   → diagrams : src/diagrams/activities/mon-slug/
 *   → images   : public/images/activities/mon-slug/
 */
function resolvePaths(mdxFile) {
  const rel = path.relative(ROOT, path.resolve(mdxFile));
  // Normalise en segments POSIX
  const parts = rel.split(path.sep);

  // parts: ['src','content','docs', <type>, <slug>, ...]
  // type peut être 'fiches', 'activities', etc.
  const docsIdx = parts.indexOf('docs');
  if (docsIdx === -1) throw new Error(`Chemin MDX inattendu : ${rel}`);

  const type = parts[docsIdx + 1];                    // ex: 'fiches' ou 'activities'
  const rawSlug = parts[docsIdx + 2];
  const slug = path.basename(rawSlug, path.extname(rawSlug)); // retire .mdx si c'est un fichier

  return {
    type,
    slug,
    diagramsDir: path.join(ROOT, 'src', 'diagrams', type, slug),
    imagesDir:   path.join(ROOT, 'public', 'images', type, slug),
    // Chemin web utilisable dans le MDX (sans BASE_URL)
    webBase: `/images/${type}/${slug}`,
  };
}

// ─── Commande : new ───────────────────────────────────────────────────────────

function cmdNew(mdxFile, diagramName) {
  if (!mdxFile || !diagramName) {
    console.error('Usage: diagram.mjs new <mdx-file> <diagram-name>');
    process.exit(1);
  }

  const { diagramsDir, imagesDir, webBase } = resolvePaths(mdxFile);

  const drawioPath = path.join(diagramsDir, `${diagramName}.drawio`);
  const svgPath    = path.join(imagesDir,   `${diagramName}.svg`);

  // Crée les répertoires si besoin
  fs.mkdirSync(diagramsDir, { recursive: true });
  fs.mkdirSync(imagesDir,   { recursive: true });

  // Crée le fichier .drawio s'il n'existe pas
  if (fs.existsSync(drawioPath)) {
    console.log(`⚠  Fichier existant : ${path.relative(ROOT, drawioPath)}`);
  } else {
    fs.writeFileSync(drawioPath, DRAWIO_TEMPLATE, 'utf-8');
    console.log(`✓  Créé : ${path.relative(ROOT, drawioPath)}`);
  }

  // Export SVG immédiat (produit un fichier vide mais utilisable)
  exportOne(drawioPath, svgPath);

  console.log(`\nPour utiliser dans le MDX :`);
  console.log(`  <ImageFigureViewer`);
  console.log(`    src="${webBase}/${diagramName}.svg"`);
  console.log(`    alt=""`);
  console.log(`  />`);
  console.log(`\nPour ré-exporter après modification :`);
  console.log(`  npm run diagram:export -- ${mdxFile}`);
}

// ─── Commande : export ────────────────────────────────────────────────────────

function cmdExport(mdxFile) {
  if (mdxFile) {
    // Export des diagrammes liés à un MDX spécifique
    const { diagramsDir, imagesDir } = resolvePaths(mdxFile);
    exportDir(diagramsDir, imagesDir);
  } else {
    // Export de tous les diagrammes sous src/diagrams/
    const diagramsRoot = path.join(ROOT, 'src', 'diagrams');
    if (!fs.existsSync(diagramsRoot)) {
      console.log('Aucun diagramme trouvé dans src/diagrams/');
      return;
    }
    // Parcourt récursivement src/diagrams/{type}/{slug}/
    for (const type of fs.readdirSync(diagramsRoot)) {
      const typeDir = path.join(diagramsRoot, type);
      if (!fs.statSync(typeDir).isDirectory()) continue;
      for (const slug of fs.readdirSync(typeDir)) {
        const diagramsDir = path.join(typeDir, slug);
        if (!fs.statSync(diagramsDir).isDirectory()) continue;
        const imagesDir = path.join(ROOT, 'public', 'images', type, slug);
        exportDir(diagramsDir, imagesDir);
      }
    }
  }
}

function exportDir(diagramsDir, imagesDir) {
  if (!fs.existsSync(diagramsDir)) {
    console.log(`Aucun diagramme dans ${path.relative(ROOT, diagramsDir)}`);
    return;
  }
  fs.mkdirSync(imagesDir, { recursive: true });
  const files = fs.readdirSync(diagramsDir).filter(f => f.endsWith('.drawio'));
  if (files.length === 0) {
    console.log(`Aucun .drawio dans ${path.relative(ROOT, diagramsDir)}`);
    return;
  }
  for (const file of files) {
    const stem      = path.basename(file, '.drawio');
    const drawioPath = path.join(diagramsDir, file);
    const svgPath    = path.join(imagesDir, `${stem}.svg`);
    exportOne(drawioPath, svgPath);
  }
}

function exportOne(drawioPath, svgPath) {
  const rel = path.relative(ROOT, drawioPath);
  const out  = path.relative(ROOT, svgPath);
  try {
    execSync(
      `drawio --export --format svg --output "${svgPath}" "${drawioPath}"`,
      { stdio: 'pipe' }
    );
    console.log(`✓  Exporté : ${out}`);
  } catch (err) {
    console.error(`✗  Erreur export ${rel} :`, err.stderr?.toString().trim() ?? err.message);
  }
}

// ─── Entrée principale ────────────────────────────────────────────────────────

const [,, cmd, ...args] = process.argv;

switch (cmd) {
  case 'new':    cmdNew(args[0], args[1]); break;
  case 'export': cmdExport(args[0]); break;
  default:
    console.log(`Usage:
  node tools/diagram.mjs new    <mdx-file> <diagram-name>
  node tools/diagram.mjs export [<mdx-file>]`);
    process.exit(1);
}
