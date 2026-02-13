#!/usr/bin/env bash
set -euo pipefail

# Configuration
SOURCE_BRANCH="dev"
REMOTE="origin"

# Vérifie qu'on est dans un dépôt git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Pas dans un dépôt git"
    exit 1
fi

echo "⚙️  Configuration des alias locaux..."

git config alias.start "!git checkout $SOURCE_BRANCH && git pull $REMOTE $SOURCE_BRANCH --rebase"
git config alias.stop  "!git add -A && git commit -m \"wip: sauvegarde \$(hostname) \$(date +%H:%M)\" && git push $REMOTE $SOURCE_BRANCH"
git config alias.sync  "!git pull $REMOTE $SOURCE_BRANCH --rebase && git push $REMOTE $SOURCE_BRANCH"
git config alias.wip   "!git add -A && git commit -m \"wip: \$(date +%Y-%m-%d_%H:%M)\""
git config alias.s     "!git status --short --branch"

echo "✅ Alias locaux configurés :"
echo "   git start  → checkout $SOURCE_BRANCH + pull rebase"
echo "   git stop   → commit wip + push"
echo "   git sync   → pull rebase + push"
echo "   git wip    → commit wip horodaté (sans push)"
echo "   git s      → statut court avec nom de branche"
echo ""
echo "💡 Ces alias sont locaux à ce dépôt et écrasent les alias globaux du même nom."
