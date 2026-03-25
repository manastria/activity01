# Diagrammes draw.io

## Vue d'ensemble

Les diagrammes draw.io suivent une convention simple :

- **Sources** (`.drawio`) versionnées dans `src/diagrams/{type}/{slug}/`
- **Exports** (`.svg`) dans `public/images/{type}/{slug}/`

Le script `tools/diagram.mjs` gère la création et l'export. Le CLI `drawio` doit être installé sur la machine (`/usr/bin/drawio`).

---

## Commandes npm

```bash
# Créer un nouveau diagramme lié à un fichier MDX
npm run diagram:new -- <mdx-file> <diagram-name>

# Ré-exporter les diagrammes d'un fichier MDX
npm run diagram:export -- <mdx-file>

# Ré-exporter tous les diagrammes du projet
npm run diagram:export
```

---

## Workflow type

### 1. Créer le diagramme

**Depuis le terminal :**

```bash
npm run diagram:new -- src/content/docs/fiches/sns-ordonnancement-filtrage-nat.mdx topologie
```

**Depuis VSCode** (fichier MDX ouvert dans l'éditeur) :

`Ctrl+Shift+P` → **Tasks: Run Task** → **Diagram: nouveau diagramme pour ce fichier**

VSCode injecte automatiquement le chemin du fichier courant et demande le nom via une boîte de saisie.

Le script :

1. Crée `src/diagrams/fiches/sns-ordonnancement-filtrage-nat/topologie.drawio` (template vide)
2. Exporte immédiatement `public/images/fiches/sns-ordonnancement-filtrage-nat/topologie.svg`
3. Affiche le snippet `<ImageFigureViewer>` prêt à coller

### 2. Éditer le diagramme

```bash
drawio src/diagrams/fiches/sns-ordonnancement-filtrage-nat/topologie.drawio
```

### 3. Ré-exporter après modification

**Depuis le terminal :**

```bash
npm run diagram:export -- src/content/docs/fiches/sns-ordonnancement-filtrage-nat.mdx
```

**Depuis VSCode** (fichier MDX ouvert dans l'éditeur) :

`Ctrl+Shift+P` → **Tasks: Run Task** → **Diagram: ré-exporter pour ce fichier**

### 4. Intégrer dans le MDX

```mdx
import ImageFigureViewer from "@/components/ImageFigureViewer.astro";

<ImageFigureViewer
  src="/images/fiches/sns-ordonnancement-filtrage-nat/topologie.svg"
  alt="Description du schéma"
  caption="Topologie réseau"
/>
```

---

## Convention de chemins

Le script dérive automatiquement les chemins à partir du fichier MDX passé en argument.

| Type de contenu | Fichier MDX | Dossier sources | Dossier images |
| --------------- | ----------- | --------------- | -------------- |
| Fiche | `src/content/docs/fiches/{slug}.mdx` | `src/diagrams/fiches/{slug}/` | `public/images/fiches/{slug}/` |
| Activité | `src/content/docs/activities/{slug}/index.mdx` | `src/diagrams/activities/{slug}/` | `public/images/activities/{slug}/` |

---

## Pourquoi SVG et non PNG/AVIF ?

Le pipeline `images:build` (sharp) traite uniquement les `.jpg/.jpeg/.png`. Les SVG sont ignorés volontairement : ils sont déjà vectoriels et compacts, et le composant `ImageFigureViewer` les sert directement via le fallback de `resolveImage`.

---

## Raccourci clavier VSCode (optionnel)

Pour déclencher la création d'un diagramme sans passer par la palette de commandes, ajouter dans `keybindings.json` (`Ctrl+Shift+P` → **Open Keyboard Shortcuts (JSON)**) :

```json
{
  "key": "ctrl+shift+d",
  "command": "workbench.action.tasks.runTask",
  "args": "Diagram: nouveau diagramme pour ce fichier"
}
```

---

## Fichiers concernés

| Fichier | Rôle |
| ------- | ---- |
| `tools/diagram.mjs` | Script de création et d'export |
| `.vscode/tasks.json` | Tâches VSCode (fichier courant injecté via `${relativeFile}`) |
| `src/diagrams/` | Sources draw.io versionnées |
| `public/images/` | SVG exportés (servis statiquement) |
