# Composant Quiz

## Partie 1 — Documentation utilisateur

Le composant `Quiz` permet d'intégrer un QCM interactif dans n'importe quelle page MDX.

### Intégration dans une page MDX

```mdx
---
title: Mon quiz
---

import Quiz from '@/components/Quiz.astro';
import quizData from '@/data/quiz/mon-quiz.json';

{/* Quiz complet */}
<Quiz data={quizData} />

{/* Démarrer à la question 5 */}
<Quiz data={quizData} start={5} />

{/* Restreindre aux questions 3 à 7 */}
<Quiz data={quizData} range="3-7" />

{/* Plages multiples : questions 1-2 puis 5-10 */}
<Quiz data={quizData} range="1-2,5-10" />
```

### Props disponibles

| Prop | Type | Défaut | Description |
| --- | --- | --- | --- |
| `data` | `QuizData` | — | **Obligatoire.** Données du quiz (voir format JSON ci-dessous) |
| `range` | `string` | — | Plage(s) de questions. Syntaxe : `"N-M"` ou `"N-M,P-Q,…"` (virgule ou point-virgule). Les plages sont concaténées dans l'ordre. |
| `start` | `number` | `1` | Question de départ (index 1-based). Ignoré si `range` est défini. |

**Priorité :** le hash de l'URL est toujours prioritaire sur les props. Un lien `#3-7` écrasera temporairement le `range` défini dans le MDX.

### Format du fichier de données

Le fichier JSON doit respecter la structure suivante :

```json
{
  "templateVersion": "1.0",
  "quizTitle": "Titre affiché dans l'en-tête du quiz",
  "quizData": [
    {
      "question": "Texte de la question (HTML accepté)",
      "options": [
        "Proposition A",
        "Proposition B",
        "Proposition C",
        "Proposition D"
      ],
      "correct": 2,
      "hint": "Texte de l'indice (HTML accepté)",
      "feedback": "Explication affichée après une bonne réponse (HTML accepté)",
      "wrong_feedbacks": [
        "Pourquoi A est incorrect",
        "Pourquoi B est incorrect",
        "",
        "Pourquoi D est incorrect"
      ]
    }
  ]
}
```

**Notes sur les champs :**

| Champ             | Type       | Description                                                                                                                                               |
| ----------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `templateVersion` | `string`   | Version du format (actuellement `"1.0"`)                                                                                                                  |
| `quizTitle`       | `string`   | Titre affiché dans l'en-tête du composant                                                                                                                 |
| `quizData`        | `array`    | Liste des questions                                                                                                                                       |
| `question`        | `string`   | Énoncé de la question. HTML autorisé (balises `<code>`, `<strong>`, etc.)                                                                                 |
| `options`         | `string[]` | Liste des propositions. HTML autorisé                                                                                                                     |
| `correct`         | `number`   | Index (0-based) de la bonne réponse dans `options`                                                                                                        |
| `hint`            | `string`   | Indice optionnel, visible à la demande avant réponse                                                                                                      |
| `feedback`        | `string`   | Explication affichée après une bonne réponse                                                                                                              |
| `wrong_feedbacks` | `string[]` | Explication par proposition incorrecte. L'index doit correspondre à celui de `options`. La valeur à l'index de la bonne réponse est ignorée (mettre `""`) |

### Sélectionner une plage de questions via l'URL

Le composant lit le hash de l'URL pour démarrer à une question précise ou restreindre la plage active :

| Hash        | Comportement                                                      |
| ----------- | ----------------------------------------------------------------- |
| `/page#5`   | Démarre à la question 5, toutes les questions restent disponibles |
| `/page#3-7` | Restreint le quiz aux questions 3 à 7 (inclus)                    |

Le hash est réactif : changer l'URL sans recharger la page réinitialise le quiz avec la nouvelle plage.

> **Limitation — plusieurs quiz sur la même page :** toutes les instances lisent le même `window.location.hash`. Si la page contient plusieurs `<Quiz>`, le hash s'applique à **tous** simultanément. La navigation par hash n'est donc fiable que lorsqu'une seule instance est présente sur la page.

**Exemple — liens de révision ciblés dans une page MDX :**

```mdx
- [Toutes les questions](/fiches/qcm)
- [Questions 1–5 : Bases du pare-feu](/fiches/qcm#1-5)
- [Questions 6–10 : Règles NAT](/fiches/qcm#6-10)
```

---

## Partie 2 — Documentation développeur

### Fichier source

`src/components/Quiz.astro`

### Architecture générale

Le composant est entièrement auto-contenu : HTML, logique JavaScript et styles CSS sont regroupés dans un seul fichier `.astro`. Aucune dépendance externe.

Le rendu HTML est statique (généré côté serveur par Astro). Les données sont sérialisées dans un attribut `data-quiz` sur l'élément racine, puis lues par le script client au démarrage.

```
[Astro SSR]  →  data-quiz="{JSON}" sur .quiz-root
[Script]     →  initQuiz(root) lit le JSON et pilote le DOM
```

### Interfaces TypeScript

```ts
interface QuizQuestion {
  question: string;
  options: string[];
  correct: number;
  hint: string;
  feedback: string;
  wrong_feedbacks: string[];
}

interface QuizData {
  templateVersion: string;
  quizTitle: string;
  quizData: QuizQuestion[];
}

interface Props {
  data: QuizData;
  range?: string;  // ex: "3-7" ou "1-2,5-10"
  start?: number;  // index 1-based ; ignoré si range est défini
}
```

### Éléments DOM (`data-el`)

Le script accède aux nœuds via `root.querySelector('[data-el="…"]')`. Tableau des identifiants :

| `data-el`          | Rôle                                                           |
| ------------------ | -------------------------------------------------------------- |
| `quiz-container`   | Conteneur principal (masqué quand les résultats sont affichés) |
| `quiz-main-title`  | Titre du quiz dans l'en-tête                                   |
| `progress`         | Badge "N / Total"                                              |
| `question`         | Énoncé de la question courante                                 |
| `options`          | Grille des boutons de proposition (générés dynamiquement)      |
| `hint-area`        | Bloc entier de l'indice (masqué après une réponse)             |
| `hint-btn`         | Bouton "Voir l'indice"                                         |
| `hint-container`   | Boîte de l'indice (animée via `.visible`)                      |
| `hint-text`        | Texte de l'indice                                              |
| `feedback-wrapper` | Bloc feedback (animé via `.visible`)                           |
| `feedback-title`   | "Bonne réponse !" ou "Mauvaise réponse."                       |
| `feedback`         | Corps du feedback (HTML injecté par JS)                        |
| `navigation`       | Barre de navigation (barre de progression + bouton Suivant)    |
| `progress-bar`     | Remplissage de la barre de progression                         |
| `next-btn`         | Bouton "Suivant" / "Voir les résultats"                        |
| `result-container` | Écran de fin (masqué pendant le quiz)                          |
| `score`            | Score final affiché ("X / Total")                              |
| `restart-btn`      | Bouton "Recommencer le quiz"                                   |

### Cycle de vie d'une question

```
loadQuestion()
  ├── Injecte question.innerHTML et génère les boutons options
  ├── Met à jour le badge progress et la barre de progression
  ├── Réinitialise feedback (retire .visible) et hint-area (display: '')
  └── Désactive next-btn

  [clic option]  →  selectAnswer()
    ├── Ajoute .correct / .incorrect sur les boutons
    ├── Injecte le feedback HTML
    ├── Affiche feedback-wrapper (.visible)
    ├── Masque hint-area (display: 'none')
    ├── Désactive tous les boutons option
    └── Active next-btn

  [clic next-btn]
    ├── Si questions restantes  →  currentQuestionIndex++  →  loadQuestion()
    └── Si dernière question   →  showResults()
```

### Gestion des paramètres de plage

`parseSegments(raw)` découpe une chaîne de plages (`"1-2,5-10"`) en tableau de paires d'indices `[start, end]` (0-based). Les séparateurs acceptés sont la virgule et le point-virgule.

`applySettings()` détermine `questions` et `initialQuestionIndex` selon la priorité suivante :

1. **Hash URL** (`window.location.hash`) — prioritaire sur tout
2. **Prop `range`** (`root.dataset.quizRange`) — plage(s) fixes définies dans le MDX
3. **Prop `start`** (`root.dataset.quizStart`) — question de départ, quiz complet
4. **Défaut** — quiz complet depuis la question 1

Quand plusieurs plages sont actives, `questions` est construit par `flatMap` des tranches correspondantes, dans l'ordre déclaré.

L'événement `hashchange` déclenche `applySettings()` + `resetQuizState()`, ce qui permet de naviguer entre les plages sans rechargement de page.

### Animation des éléments collapsibles

`.quiz-feedback-wrapper` et `.quiz-hint-box` sont animés par transition CSS sur `max-height`, `opacity` et `transform`. Le JavaScript ajoute ou retire la classe `.visible` :

```css
/* état fermé (défaut) */
max-height: 0; opacity: 0; transform: translateY(-8px);

/* état ouvert */
max-height: 1000px; opacity: 1; transform: translateY(0);
```

### Support multi-instances

La fonction `initQuiz` est appelée sur chaque `.quiz-root[data-quiz]` présent dans la page, ce qui permet d'inclure plusieurs `<Quiz>` dans une même page sans conflit.

