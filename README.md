# Template Astro/Starlight — Activités pédagogiques

Ce dépôt est un **starter** prêt à l'emploi pour publier des activités pédagogiques avec **Astro + Starlight**.

- Pages au format **Markdown/MDX** sous `src/content/docs/`
- Section **Activités** auto‑générée depuis `src/content/docs/activities/`
- Script **`npm run new`** pour créer une activité à partir d'un modèle
- Déploiement **GitHub Pages** (workflow fourni)
- Déploiement **SSH/rsync** vers tout hébergeur (script local)

## Prérequis

- Node.js ≥ 18.20.8
- Python ≥ 3.8 (pour les scripts d'organisation d'images)
- npm (ou pnpm/yarn/bun si vous préférez)

## Démarrer

```bash
npm install
npm run dev
```
Ouvrir http://localhost:4321/

## Créer une nouvelle activité

Interactive :
```bash
npm run new -- --slug a01-intro-html --title "A01 · Introduction HTML" --level "BTS SIO 1" --duration "1h30" --tags "html,intro"
```

Depuis un fichier YAML :
```bash
npm run new -- --from blueprints/activity.yml
```

## Structure

```
src/content/docs/
├─ index.mdx                    # Accueil
└─ activities/
   ├─ index.mdx                 # Page d'intro des activités
   └─ example-activity/
      ├─ index.mdx              # Contenu de l'activité
      └─ assets/                # Images/annexes éventuelles
```

---

## Gestion des images

### Principe général

Le workflow d'images se déroule en 3 phases :

| Phase            | Emplacement                               | État                              |
| ---------------- | ----------------------------------------- | --------------------------------- |
| **Rédaction**    | `public/images/_inbox/`                   | Collage rapide, non optimisé      |
| **Organisation** | `public/images/activities/<slug>/<page>/` | Fichiers rangés, liens réécrits   |
| **Optimisation** | Même emplacement + variantes              | AVIF/WebP + miniatures + manifest |

### Scripts npm disponibles

```bash
# Organisation : range les images et réécrit les liens MDX
npm run images:organize

# Optimisation : génère AVIF/WebP + miniatures + manifest
npm run images:build

# Les deux en séquence (recommandé après rédaction)
npm run images:all

# Migration : convertit ![](image.png) en composants
npm run images:migrate            # vers ImageFigure
npm run images:migrate:viewer     # vers ImageFigureViewer

# Mode watch (rebuild auto lors de modifications)
npm run images:watch
```

### Coller une image (VS Code)

**Prérequis** : Extension `mushan.vscode-paste-image` avec raccourci `Ctrl+Alt+V`

Configuration dans `.vscode/settings.json` :
```json
{
  "pasteImage.path": "${projectRoot}/public/images/_inbox",
  "pasteImage.forceUnixStyleSeparator": true,
  "pasteImage.namePrefix": "${currentFileNameWithoutExt}-",
  "pasteImage.insertPattern": "/images/_inbox/${imageFileName}"
}
```

**Procédure** :
1. Enregistrer le fichier `.mdx` (Ctrl+S)
2. Copier l'image (capture écran, presse-papier…)
3. Coller avec `Ctrl+Alt+V`

### Créer une galerie

```mdx
import GalleryRow from "@/components/GalleryRow.astro";

<GalleryRow
  group="ma-galerie"
  images={[
    { src: "/images/_inbox/etape1.png", alt: "Étape 1" },
    { src: "/images/_inbox/etape2.png", alt: "Étape 2" }
  ]}
/>
```

### Créer une image qui s'ouvre dans un nouvel onglet lors du clic 

Utiliser `ImageFigure` pour afficher une image optimisée et ouvrir le fichier original dans un nouvel onglet au clic. Ce composant est idéal pour les captures d’écran et schémas que l’on souhaite consulter en grand format. Les images pointant vers `/images/_inbox/...` restent valides pendant la rédaction.

**Options utiles :**
- `caption` pour afficher une légende
- `maxWidth` pour limiter la largeur (ex. `"640px"`)
- `align` pour l’alignement (`"left" | "center" | "right"`)

```mdx
import ImageFigure from "@/components/ImageFigure.astro";

<ImageFigure
  src="/images/_inbox/2026-02-09-12-27-11.png"
  alt="Écran de démarrage"
  scale={1}
/>
```

### Créer une image qui ouvre Viewer.js pour la visualisation

Utiliser `ImageFigureViewer` quand vous voulez un zoom interactif (Viewer.js) directement dans la page. C’est pratique pour les schémas détaillés ou les captures nécessitant un zoom sans quitter la page.

**Bon à savoir :**
- Le composant accepte les mêmes props que `ImageFigure` (`src`, `alt`, `caption`, `maxWidth`, `scale`, `align`).
- Après la rédaction, lancez `npm run images:all` pour générer les variantes optimisées et miniatures.

```mdx
import ImageFigureViewer from "@/components/ImageFigureViewer.astro";

<ImageFigureViewer
  src="/images/_inbox/2026-02-09-12-27-11.png"
  alt="Écran de démarrage"
  scale={1}
/>
```

### Workflow recommandé

**Pendant la rédaction :**
1. Coller les images (→ `_inbox`)
2. Utiliser les composants Astro avec les chemins `/images/_inbox/...`
3. Continuer à rédiger (le site reste visualisable)

**Après la rédaction :**
```bash
npm run images:all
npm run dev  # vérifier le résultat
```

---

## Outils Python

Les scripts Python se trouvent dans `tools/` et gèrent l'organisation et la migration des images.

### organize_images.py

Range les images depuis `_inbox` vers leur emplacement final et réécrit les liens dans les fichiers MDX.

```bash
# Aperçu (dry-run, ne modifie rien)
python tools/organize_images.py

# Appliquer les modifications
python tools/organize_images.py --write

# Mode strict (échoue si une image référencée est introuvable)
python tools/organize_images.py --write --strict
```

**Ce que fait le script :**
- Scanne `src/content/docs/activities/**/*.mdx`
- Cherche les références `/images/_inbox/...`
- Déplace les fichiers vers `public/images/activities/<activitySlug>/<pageStem>/`
- Réécrit les liens dans les fichiers MDX

**Options :**
| Option        | Description                                              |
| ------------- | -------------------------------------------------------- |
| `--write`     | Applique les modifications (sans cette option = dry-run) |
| `--strict`    | Échoue si une image référencée n'existe pas              |
| `--root PATH` | Spécifie la racine du projet                             |

### migrate_markdown_images.py

Convertit la syntaxe Markdown `![alt](image.png)` en composants Astro et déplace les images locales.

```bash
# Aperçu (dry-run)
python tools/migrate_markdown_images.py

# Migrer vers ImageFigure
python tools/migrate_markdown_images.py --write

# Migrer vers ImageFigureViewer (avec zoom interactif)
python tools/migrate_markdown_images.py --viewer --write
```

**Ce que fait le script :**
- Scanne les fichiers MDX pour trouver `![alt](chemin-relatif.png)`
- Déplace les images vers `public/images/activities/<activitySlug>/<pageStem>/`
- Remplace par `<ImageFigure src="..." alt="..." />` ou `<ImageFigureViewer ... />`
- Ajoute l'import du composant si absent

**Options :**
| Option        | Description                                              |
| ------------- | -------------------------------------------------------- |
| `--write`     | Applique les modifications (sans cette option = dry-run) |
| `--viewer`    | Utilise ImageFigureViewer au lieu de ImageFigure         |
| `--root PATH` | Spécifie la racine du projet                             |

**Exemple de transformation :**
```markdown
<!-- Avant -->
![Schéma réseau](schema.png "Cliquez pour agrandir")

<!-- Après -->
<ImageFigure src="/images/activities/sns/reset/schema.png" alt="Schéma réseau" caption="Cliquez pour agrandir" />
```

### build-images.mjs

Script Node.js qui génère les variantes optimisées des images.

```bash
# Build unique
node tools/build-images.mjs

# Mode watch
node tools/build-images.mjs --watch
```

**Ce que fait le script :**
- Scanne `public/images/` (ignore `_inbox/`)
- Génère des variantes AVIF et WebP (si gain > 10%)
- Génère des miniatures (hauteur 120px par défaut)
- Écrit le manifest dans `src/data/images.manifest.json`

**Variables d'environnement :**
| Variable       | Défaut | Description                      |
| -------------- | ------ | -------------------------------- |
| `THUMB_HEIGHT` | 120    | Hauteur des miniatures en pixels |
| `QUALITY_WEBP` | 82     | Qualité WebP (0-100)             |
| `QUALITY_AVIF` | 45     | Qualité AVIF (0-100)             |

---

## Déploiement

### GitHub Pages

1. Paramétrer l'URL dans `astro.config.mjs` :
   - Projet (user.github.io/**repo**): `site` = `https://user.github.io/repo/`, `base` = `/repo/`
   - Domaine racine: `site` = `https://domaine.tld/`, pas de `base`

2. Activer Pages (Settings → Pages → "GitHub Actions").
3. Pousser sur `main`. Le workflow `.github/workflows/deploy-gh-pages.yml` fera le reste.

### Hébergeur SSH (rsync)

Déploiement local vers n'importe quel hébergeur accessible en SSH (Infomaniak, OVH, VPS…).
Le site est déployé dans le même sous-chemin `/activity01/` que GitHub Pages, un seul build suffit.

1. Copier `.env.example` vers `.env` et adapter :
   ```bash
   cp .env.example .env
   ```
   ```env
   DEPLOY_HOST=user@host.example.com
   DEPLOY_PATH=/web/activity01
   ```

2. Lancer le déploiement :
   ```bash
   npm run deploy:ssh
   ```
   Le script build le site puis synchronise `dist/` via rsync.

**Sous Windows** : le script utilise `bash` et `rsync`. Deux options :
- **WSL** (recommandé) : `wsl npm run deploy:ssh`
- **Git Bash** : exécuter depuis le terminal Git Bash

---

## Dépannage

### L'image se colle au mauvais endroit
- Vérifier que le raccourci appelle bien l'extension **Paste Image** (mushan)
- Vérifier que le fichier `.mdx` est enregistré (Ctrl+S)
- Vérifier la config dans `.vscode/settings.json`

### La galerie affiche l'image sans miniatures / AVIF / WebP
Normal si :
- L'image est encore dans `_inbox`
- `npm run images:build` n'a pas été relancé après le rangement

Solution :
```bash
npm run images:all
```

### Erreur "image référencée introuvable"
Le script `organize_images.py` signale les images manquantes. Vérifier que :
- Le fichier existe dans `public/images/_inbox/`
- Le chemin dans le MDX correspond exactement au nom du fichier

---

## Licence

MIT © 2025
