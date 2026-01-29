# Template Astro/Starlight — Activités pédagogiques

Ce dépôt est un **starter** prêt à l'emploi pour publier des activités pédagogiques avec **Astro + Starlight**.

- Pages au format **Markdown/MDX** sous `src/content/docs/`
- Section **Activités** auto‑générée depuis `src/content/docs/activities/`
- Script **`npm run new`** pour créer une activité à partir d’un modèle
- Déploiement **GitHub Pages** (workflow fourni)
- Déploiement **Infomaniak** via SFTP/SSH (workflow fourni, à activer)

## Prérequis

- Node.js ≥ 18.20.8
- npm (ou pnpm/yarn/bun si vous préférez)

## Démarrer

```bash
npm install
npm run dev
```
Ouvrir http://localhost:4321/

## Créer une nouvelle activité

Interactive :
```bash
npm run new -- --slug a01-intro-html --title "A01 · Introduction HTML" --level "BTS SIO 1" --duration "1h30" --tags "html,intro"
```

Depuis un fichier YAML :
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

## Déploiement

### GitHub Pages

1. Paramétrer l’URL dans `astro.config.mjs` :
   - Projet (user.github.io/**repo**): `site` = `https://user.github.io/repo/`, `base` = `/repo/`
   - Domaine racine: `site` = `https://domaine.tld/`, pas de `base`

2. Activer Pages (Settings → Pages → “GitHub Actions”).  
3. Pousser sur `main`. Le workflow `.github/workflows/deploy-gh-pages.yml` fera le reste.

### Infomaniak (SFTP/SSH)

- Créer un utilisateur SSH/SFTP (console Infomaniak) et relever **host**, **user** et le **chemin** cible (`/web/…`).  
- Ajouter les secrets GitHub : `HOST`, `USER`, `SSH_PRIVATE_KEY` (clef au format OpenSSH), `REMOTE_PATH`.  
- Activer (décommenter si besoin) le job `deploy-infomaniak` dans `.github/workflows/deploy-infomaniak.yml`.

## Licence

MIT © 2025