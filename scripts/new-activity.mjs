#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import * as url from 'node:url';
import YAML from 'yaml';

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');
const docsDir = path.join(root, 'src', 'content', 'docs', 'activities');

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = argv[i + 1];
    if (a.startsWith('--')) {
      const key = a.replace(/^--/, '');
      if (next && !next.startsWith('--')) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    }
  }
  return args;
}

function toSlug(s) {
  return s.toLowerCase()
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function readBlueprintMDX() {
  const p = path.join(root, 'blueprints', 'activity.mdx');
  return fs.readFileSync(p, 'utf8');
}

function createFromConfig(cfg) {
  const slug = cfg.slug ?? toSlug(cfg.title ?? 'nouvelle-activite');
  const title = cfg.title ?? slug;
  const description = cfg.description ?? '';
  const level = cfg.level ?? '';
  const duration = cfg.duration ?? '';
  const tags = Array.isArray(cfg.tags) ? cfg.tags : (cfg.tags ? String(cfg.tags).split(',') : []);
  const status = cfg.status ?? 'draft';
  const order = Number.isFinite(cfg.order) ? cfg.order : 100;
  const sidebarLabel = cfg.sidebarLabel ?? title;
  const date = new Date().toISOString().slice(0, 10);

  const targetDir = path.join(docsDir, slug);
  ensureDir(path.join(targetDir, 'assets'));
  const template = readBlueprintMDX();
  const tagsStr = tags.map(t => `"${t.trim()}"`).join(', ');
  const filled = template
    .replaceAll('{TITLE}', title)
    .replaceAll('{DESCRIPTION}', description)
    .replaceAll('{LEVEL}', level)
    .replaceAll('{DURATION}', duration)
    .replaceAll('{TAGS}', tagsStr)
    .replaceAll('{STATUS}', status)
    .replaceAll('{ORDER}', String(order))
    .replaceAll('{SIDEBAR_LABEL}', sidebarLabel)
    .replaceAll('{DATE}', date);

  fs.writeFileSync(path.join(targetDir, 'index.mdx'), filled, 'utf8');
  console.log(`✓ Activité créée → src/content/docs/activities/${slug}/index.mdx`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.from) {
    const y = fs.readFileSync(path.resolve(args.from), 'utf8');
    const cfg = YAML.parse(y);
    createFromConfig(cfg);
    return;
  }
  if (!args.slug && !args.title) {
    console.error('Usage: npm run new -- --slug <slug> --title "<Titre>" [--description "..."] [--level "..."] [--duration "..."] [--tags "a,b"] [--status draft|ready|review] [--order 1]');
    process.exit(1);
  }
  createFromConfig({
    slug: args.slug,
    title: args.title,
    description: args.description,
    level: args.level,
    duration: args.duration,
    tags: args.tags ? String(args.tags).split(',') : [],
    status: args.status,
    order: args.order ? Number(args.order) : undefined,
  });
}

main();