# Copilot instructions

## Project overview
- Astro + Starlight site for French pedagogical activities (TP/lab). Content lives in src/content/docs/ and activities in src/content/docs/activities/{activitySlug}/.
- Custom content schema is defined in src/content/config.ts with fields like `duration`, `level`, `tags`, `status`.

## Key workflows (common commands)
- Dev server: npm run dev (http://localhost:4321)
- Build/preview/deploy: npm run build | npm run preview | npm run deploy (GitHub Pages)
- New activity: npm run new -- --slug ... --title ... --level ... --duration ... --tags ... or npm run new -- --from blueprints/activity.yml

## Image pipeline (core project-specific flow)
- Draft images go to public/images/_inbox/.
- Run npm run images:organize to move images into public/images/activities/{activitySlug}/{pageStem}/ and rewrite MDX links.
- Run npm run images:build to generate AVIF/WebP + thumbnails and update src/data/images.manifest.json.
- Recommended after writing: npm run images:all (organize + build). For watch mode: npm run images:watch.

## MDX image components (use these patterns)
- Gallery: src/components/GalleryRow.astro (props: `images[]`, `group`, `thumbHeight`, `gap`).
- Single image: src/components/ImageFigure.astro (props: `src`, `alt`, `caption`, `maxWidth`, `scale`, `align`).
- Zoom viewer: src/components/ImageFigureViewer.astro (same props as ImageFigure).
- Components rely on src/utils/images.ts; URLs are prefixed with `import.meta.env.BASE_URL` for subpath deployments.

## Conventions
- Use path alias @/* for imports from src/ (e.g., @/components, @/utils).
- Indentation: MDX uses 3 spaces; JS/Astro uses 2 spaces; default 4 spaces. Use LF and UTF-8.

## Files to reference
- astro.config.mjs (Starlight config + base URL)
- tools/organize_images.py and tools/migrate_markdown_images.py (image link rewriting + component migration)
- tools/build-images.mjs (image optimization, manifest generation)
- scripts/new-activity.mjs (activity scaffolding)
