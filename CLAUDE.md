# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Astro + Starlight educational content platform for publishing pedagogical activities (TP/lab exercises) in French. Topics include SNS firewall configuration, VPN setup, and network supervision.

## Key Commands

```bash
# Development
npm run dev              # Start dev server on localhost:4321

# Build & Deploy
npm run build            # Build static site
npm run preview          # Preview built site
npm run deploy           # Build + deploy to GitHub Pages

# Activity Creation
npm run new -- --slug a01-intro --title "A01 · Intro" --level "BTS SIO 1" --duration "1h30" --tags "html,intro"
npm run new -- --from blueprints/activity.yml

# Image Management
npm run images:organize       # Move images from inbox to final locations, update MDX refs
npm run images:build          # Generate AVIF/WebP variants + thumbnails + manifest
npm run images:all            # Run organize + build (recommended after writing)
npm run images:watch          # Watch and rebuild on changes
npm run images:migrate        # Convert ![](img.png) to ImageFigure components
npm run images:migrate:viewer # Convert to ImageFigureViewer components
```

## Architecture

### Content Model

Activities live in `src/content/docs/activities/{activitySlug}/`. Content schema (`src/content/config.ts`) extends Starlight with custom fields:
- `duration`, `level`, `tags`, `status` (draft|ready|review)

### Image Pipeline

1. **Inbox**: Paste images to `public/images/_inbox/` during writing
2. **Organize**: `images:organize` moves to `public/images/activities/{activitySlug}/{pageStem}/` and updates MDX
3. **Build**: `images:build` creates AVIF/WebP variants and generates `src/data/images.manifest.json`

### Image Components

All components use shared utilities from `src/utils/images.ts` (`withBase`, `loadManifest`, `resolveImage`).

- **GalleryRow.astro**: Image gallery with GLightbox (props: `images[]`, `group`, `thumbHeight`, `gap`)
- **ImageFigure.astro**: Single optimized image (props: `src`, `alt`, `caption`, `maxWidth`, `scale`, `align`)
- **ImageFigureViewer.astro**: Image with ViewerJS zoom (same props as ImageFigure)

Components auto-prefix URLs with `import.meta.env.BASE_URL` for subpath deployments.

### Path Alias

Use `@/*` for imports from `src/` (e.g., `@/components`, `@/utils`).

## Code Style

- **Markdown/MDX**: 3 spaces indentation
- **JavaScript/Astro**: 2 spaces indentation
- **Default**: 4 spaces, LF line endings, UTF-8

## Deployment

GitHub Pages via `.github/workflows/deploy-gh-pages.yml` on push to `main` branch. Site deploys to `https://manastria.github.io/activity01/`.

## Key Files

| File | Purpose |
|------|---------|
| `astro.config.mjs` | Starlight theme, sidebar, base URL |
| `src/content/config.ts` | Zod schema for activity metadata |
| `src/utils/images.ts` | Shared image utilities (withBase, loadManifest) |
| `tools/build-images.mjs` | Image optimization (env: THUMB_HEIGHT, QUALITY_WEBP, QUALITY_AVIF) |
| `tools/organize_images.py` | Image organization + MDX link rewriting |
| `tools/migrate_markdown_images.py` | Convert Markdown images to Astro components |
| `scripts/new-activity.mjs` | Activity scaffolding CLI |
