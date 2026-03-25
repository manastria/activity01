# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Astro + Starlight educational content platform for publishing pedagogical activities (TP/lab exercises) in French. Topics include SNS firewall configuration, VPN setup, and network supervision.

## Contexte
Ces fichiers sont des cours pour BTS SIO SISR 1ère année.
Public : étudiants avec peu de bagage réseau.

## Style attendu
- Phrases courtes, vocabulaire accessible
- Conserver les termes techniques mais les expliquer
- Garder les exemples concrets (analogies objets du quotidien)

## Convention TODO
Les commentaires `<!-- TODO: ... -->` ou `> **TODO Claude** : ...` dans les .md sont des instructions de révision.
Traite-les un par un et supprime-les après modification.

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

# Diagrams (draw.io)
npm run diagram:new -- <mdx-file> <name>   # Create .drawio + export SVG
npm run diagram:export -- <mdx-file>       # Re-export SVGs for one MDX file
npm run diagram:export                     # Re-export all diagrams
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

### Other Components

- **SectionLinks.astro**: Renders a list of `LinkCard` (Starlight) for all docs whose `id` starts with a given `prefix`, sorted by `order` field then alphabetically. Props: `prefix: string`.

  ```mdx
  import SectionLinks from '@/components/SectionLinks.astro';
  <SectionLinks prefix="activities/my-activity/" />
  ```

- **TaskLevel.astro**: Collapsible `<details>` block scoped to a difficulty level (1 = green, 2 = blue, 3 = purple). Level 1 is open by default; levels 2 and 3 are collapsed. The heading (`###`, `####`) must remain a Markdown heading for the Starlight TOC; this component wraps only the body content.

  Props: `level: 1 | 2 | 3`, `summary?: string`, `open?: boolean`

  ```mdx
  import TaskLevel from '@/components/TaskLevel.astro';

  ### ⭐ Tâche 1 : Titre

  <TaskLevel level={1}>
    Contenu de la tâche...
  </TaskLevel>

  #### ⭐⭐⭐ Tâche 1.1 : Avancé

  <TaskLevel level={3} summary="Voir les consignes avancées">
    Contenu avancé...
  </TaskLevel>
  ```

### Icons (astro-icon + Iconify)

The project uses [`astro-icon`](https://github.com/natemoo-re/astro-icon) with the following Iconify JSON sets installed:

| Prefix | Set |
| ------ | --- |
| `mdi:` | Material Design Icons |
| `lucide:` | Lucide |
| `tabler:` | Tabler Icons |
| `devicon:` | Devicon (tech logos) |
| `skill-icons:` | Skill Icons |

**Usage in MDX/Astro**:

```mdx
import { Icon } from 'astro-icon/components';

<Icon name="mdi:server" />
<Icon name="lucide:shield" size={24} />
<Icon name="tabler:network" class="my-class" />
```

Browse available icons at [icones.js.org](https://icones.js.org) and filter by set prefix.

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
| ---- | ------- |
| `astro.config.mjs` | Starlight theme, sidebar, base URL |
| `src/content/config.ts` | Zod schema for activity metadata |
| `src/utils/images.ts` | Shared image utilities (withBase, loadManifest) |
| `tools/build-images.mjs` | Image optimization (env: THUMB_HEIGHT, QUALITY_WEBP, QUALITY_AVIF) |
| `tools/organize_images.py` | Image organization + MDX link rewriting |
| `tools/migrate_markdown_images.py` | Convert Markdown images to Astro components |
| `scripts/new-activity.mjs` | Activity scaffolding CLI |
| `src/components/Quiz.astro` | Self-contained interactive QCM widget |
| `tools/diagram.mjs` | draw.io creation + SVG export (see `docs/drawio.md`) |

## Quiz Component

`src/components/Quiz.astro` — self-contained interactive QCM widget.

**Props**: `data: QuizData`

```ts
interface QuizData {
  templateVersion: string;
  quizTitle: string;
  quizData: QuizQuestion[];
}

interface QuizQuestion {
  question: string;
  options: string[];
  correct: number;           // 0-based index of the correct option
  hint: string;
  feedback: string;          // explanation shown after a correct answer
  wrong_feedbacks: string[]; // per-option explanation shown after a wrong answer
}
```

**URL hash navigation** (useful for linking to a subset of questions):

- `#5` — start at question 5
- `#3-7` — restrict quiz to questions 3 through 7

**Usage in MDX**:

```mdx
import Quiz from '@/components/Quiz.astro';
import quizData from '@/data/quiz/my-quiz.json';

<Quiz data={quizData} />
```

## Style rédactionnel (à appliquer systématiquement)

1. **Typographie :** Guillemets français « » exclusivement pour les citations et mises en avant.
2. **Terminologie :** Tout terme technique anglais en italique. À sa première apparition dans le document, développer l'acronyme entre parenthèses — ex : *RFC* (*Request For Comment*).

## Convention de nommage (noms courts)

À appliquer dès qu'un nom court est nécessaire : objets SNS, noms de
machines, interfaces réseau, variables dans les scripts, labels dans
les schémas, noms de fichiers.

Ne pas appliquer au texte courant, aux titres, ni aux noms propres.

Séparateur : `_` (underscore) — jamais de tiret.
Casse : tout en minuscules.

| Catégorie        | Préfixe      | Format                  | Exemples                          |
|------------------|-------------|-------------------------|-----------------------------------|
| Réseau           | `net_`      | `net_<zone>`            | `net_lan`, `net_dmz`              |
| Machine          | `host_`     | `host_<nom>`            | `host_glpi_web01`, `host_dns01`   |
| Passerelle       | `gw_`       | `gw_<zone_ou_isp>`      | `gw_out`, `gw_labo`               |
| Pare-feu         | `fw_`       | `fw_<nom_site>`         | `fw_crash`                        |
| Service          | `svc_`      | `svc_<proto>_<desc>`    | `svc_tcp_https`, `svc_udp_dns`    |
| Groupe services  | `grp_svc_`  | `grp_svc_<usage>`       | `grp_svc_web`, `grp_svc_admin`    |
| Groupe machines  | `grp_host_` | `grp_host_<rôle>`       | `grp_host_srv_dmz`                |
| Groupe réseaux   | `grp_net_`  | `grp_net_<desc>`        | `grp_net_prive`                   |
| VPN              | `vpn_`      | `vpn_<site>`            | `vpn_site_distant`                |
| Règle filtrage   | —           | `[ZONE→ZONE] desc`      | `[LAN→DMZ] Admin GLPI`            |

Numérotation : suffixe `01`, `02`… pour les objets de même type.
Zones : `lan`, `dmz`, `out` — cohérent avec les interfaces SNS natives.
