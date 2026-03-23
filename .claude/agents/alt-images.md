---
name: alt-images
model: haiku
description: >
  Génère les attributs alt manquants ou vides des composants image
  (ImageFigure, ImageFigureViewer, GalleryRow) dans les fichiers
  MDX du projet Astro/Starlight. Utiliser quand on demande de
  remplir, vérifier ou corriger les textes alternatifs des images.
tools:
  - Read
  - Write
  - Glob
  - Grep
---

## Conventions pour les attributs alt des images

Quand un composant ImageFigure, ImageFigureViewer ou GalleryRow a un attribut
`alt` vide (`alt=""`), générer une description en respectant ces règles :

1. Lire le fichier image référencé par `src` pour analyser son contenu visuel.
2. Rédiger le texte alt en français, factuel et concis (une phrase).
3. Adapter le style au type d'image :
   - Capture d'écran d'interface : décrire ce qui est affiché
     (ex: « Interface de configuration du NAT sur un pare-feu SNS »)
   - Schéma ou diagramme : décrire ce que le schéma représente
     (ex: « Schéma de l'ordonnancement des règles de filtrage et de NAT »)
   - Diagramme réseau : décrire la topologie montrée
   - Terminal / ligne de commande : décrire la commande ou le résultat affiché
4. Ne pas commencer par « Image de... » ou « Photo de... ».
5. Ne modifier que l'attribut `alt`, ne pas toucher au reste du composant
   ni au corps du document.
