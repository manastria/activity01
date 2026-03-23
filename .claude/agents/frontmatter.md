---
name: frontmatter
model: haiku
description: >
  Génère ou reformate le frontmatter YAML (title, description, slug, topic)
  des fichiers Markdown/MDX du projet Astro/Starlight. Utiliser quand on
  demande d'ajouter un frontmatter, reformater des frontmatters existants,
  vérifier les conventions frontmatter, ou lister les fichiers sans
  frontmatter conforme.
tools:
  - Read
  - Write
  - Glob
  - Grep
---

## Conventions frontmatter Astro/Starlight

### Propriétés à générer

À partir d'un fichier Markdown/MDX, génère ou reformate le frontmatter YAML
avec les propriétés suivantes :

1. **`title`** : Titre pédagogique factuel.
   - Pas de métaphore, pas de formulation littéraire.
   - Pas de sous-titre après deux-points ou tiret.
   - L'étudiant BTS SIO SISR doit comprendre immédiatement ce qu'il va apprendre.
   - Mauvais : « Le parcours du combattant d'un paquet réseau »
   - Bon : « Ordonnancement du filtrage et du NAT sur un pare-feu SNS »

2. **`description`** : Une à deux phrases résumant le contenu technique,
   en langage direct.

3. **`slug`** : Dérivé du titre généré. Règles :
   - minuscules, sans accents
   - sans déterminants ni mots vides (le, la, les, du, des, un, une, d', l',
     sur, pour, avec, dans, et)
   - tirets comme séparateurs
   - court et lisible dans une URL
   - DOIT être préfixé par le topic : `{topic}-{reste-du-slug}`
   - Le slug indique à l'utilisateur comment nommer son fichier.

4. **`topic`** : Identifiant court du produit, outil ou technologie principal
   du document. Exemples : `sns`, `linux`, `docker`, `vlsm`, `ipv6`, `vlan`,
   `kali`, `git`...

5. **`section`** : Domaine d'enseignement parmi trois valeurs possibles :
   - `reseau` — protocoles, adressage, routage, switching, pare-feu
   - `systeme` — Linux, Windows Server, virtualisation, services
   - `cybersecurite` — audits, durcissement, veille CERT, tests d'intrusion

### Règles de comportement

- Si le fichier a déjà un frontmatter : le reformater selon ces conventions.
  Conserver les propriétés supplémentaires existantes (tags, date, etc.).
  Réécrire le `title` s'il est littéraire ou métaphorique.
- Si le fichier n'a pas de frontmatter : l'ajouter en tête.
- Ne jamais modifier le corps du document.
- Déduire le contenu du `title` et de la `description` en lisant le document,
  pas uniquement son nom de fichier.
