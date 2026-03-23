#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correcteur de typographie française pour fichiers Markdown
Gère les espaces insécables (U+00A0) et insécables fines (U+202F)
Applique les corrections par défaut ; utiliser --dry-run pour prévisualiser sans écrire
"""

import re
import sys
import argparse
from pathlib import Path
from difflib import unified_diff

# Caractères spéciaux
NBSP = '\u00A0'      # Espace insécable (no-break space)
NNBSP = '\u202F'     # Espace insécable fine (narrow no-break space)

# Codes couleur ANSI
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BG_YELLOW = '\033[43m'
    BG_CYAN = '\033[46m'

# Symboles pour rendre les espaces visibles
NBSP_SYMBOL = '␣'      # U+2423 Open box
NNBSP_SYMBOL = '·'     # U+00B7 Middle dot

class MarkdownTypoCorrector:
    def __init__(self):
        self.code_blocks = []

    def extract_code_blocks(self, text):
        """Extrait et remplace les blocs de code ET commentaires HTML par des placeholders"""
        self.code_blocks = []

        # Commentaires HTML (à extraire EN PREMIER)
        def replace_html_comment(match):
            placeholder = f"___HTML_COMMENT_{len(self.code_blocks)}___"
            self.code_blocks.append(match.group(0))
            return placeholder

        text = re.sub(r'<!--.*?-->', replace_html_comment, text, flags=re.DOTALL)

        # Blocs de code avec triple backticks
        def replace_fenced_code(match):
            placeholder = f"___CODE_BLOCK_{len(self.code_blocks)}___"
            self.code_blocks.append(match.group(0))
            return placeholder

        text = re.sub(r'```.*?```', replace_fenced_code, text, flags=re.DOTALL)

        # Code inline avec simple backtick
        def replace_inline_code(match):
            placeholder = f"___INLINE_CODE_{len(self.code_blocks)}___"
            self.code_blocks.append(match.group(0))
            return placeholder

        text = re.sub(r'`[^`\n]+?`', replace_inline_code, text)

        return text

    def restore_code_blocks(self, text):
        """Restaure les blocs de code et commentaires HTML depuis les placeholders"""
        for i, code_block in enumerate(self.code_blocks):
            text = text.replace(f"___HTML_COMMENT_{i}___", code_block)
            text = text.replace(f"___CODE_BLOCK_{i}___", code_block)
            text = text.replace(f"___INLINE_CODE_{i}___", code_block)
        return text

    def fix_punctuation(self, text):
        """Corrige les espaces autour de la ponctuation"""

        # Corrige une abération
        text = re.sub(r',\.', r'.', text)

        # Ponctuation double : ; ! ? → espace insécable fine avant
        # Supprimer les espaces existantes avant
        text = re.sub(r'\s*([;:!?])', r'\1', text)
        # Ajouter espace insécable avant
        text = re.sub(r'([;:!?])', rf'{NBSP}\1', text)

        # Ponctuation simple . , → pas d'espace avant, espace après
        # Virgule → pas d'espace avant, espace après
        text = re.sub(r'\s*,\s*', r', ', text)

        # Point → pas d'espace avant, espace après
        # SAUF si suivi de :
        #   - lettre minuscule (Question A3.a)
        #   - chiffre (3.14, v2.5)
        #   - fin de ligne
        # Point → traitement en plusieurs étapes
        # Étape 1 : enlever les espaces avant le point
        text = re.sub(r' +\.', r'.', text)

        # Étape 2 : gérer les cas où le point ne doit PAS avoir d'espace après
        # Point en fin de ligne (garder le \n intact)
        text = re.sub(r'\. *\n', r'.\n', text)
        # Point avant minuscule ou chiffre (A3.a, 3.14, v2.5)
        text = re.sub(r'\. *([a-z\d])', r'.\1', text)

        # Étape 3 : ajouter une espace après le point SEULEMENT s'il est suivi d'une lettre MAJUSCULE
        # (évite de toucher aux cas déjà traités où le point est collé à une minuscule/chiffre)
        text = re.sub(r'\.([A-Z])', r'. \1', text)

        return text

    def fix_guillemets(self, text):
        """Convertit les guillemets anglais en français avec espaces insécables fines"""

        # Remplacer les guillemets doubles droits par des guillemets français
        # Détection des guillemets ouvrants et fermants
        parts = text.split('"')
        result = []
        is_opening = True

        for i, part in enumerate(parts):
            result.append(part)
            if i < len(parts) - 1:  # Pas après le dernier élément
                if is_opening:
                    result.append(f'«{NNBSP}')
                else:
                    result.append(f'{NNBSP}»')
                is_opening = not is_opening

        text = ''.join(result)

        # Corriger les guillemets français déjà présents mais mal espacés
        # Supprimer les espaces incorrectes
        text = re.sub(r'«\s*', f'«{NNBSP}', text)
        text = re.sub(r'\s*»', f'{NNBSP}»', text)

        return text

    def fix_numbers(self, text):
        """Corrige les espaces dans les grands nombres (milliers)"""

        # Nombres de 4 chiffres ou plus
        # Ajouter une espace insécable fine tous les 3 chiffres
        def format_number(match):
            number = match.group(0)
            # Enlever les espaces existantes
            number = number.replace(' ', '').replace(NBSP, '').replace(NNBSP, '')

            # Séparer par groupes de 3 depuis la droite
            if len(number) >= 4:
                formatted = ''
                for i, digit in enumerate(reversed(number)):
                    if i > 0 and i % 3 == 0:
                        formatted = NNBSP + formatted
                    formatted = digit + formatted
                return formatted
            return number

        # Chercher les nombres de 4 chiffres ou plus
        text = re.sub(r'\b\d{4,}\b', format_number, text)

        return text

    def fix_parentheses(self, text):
        """Corrige les espaces autour des parenthèses et crochets"""

        # Espace avant l'ouverture (si pas en début de ligne)
        text = re.sub(r'(\S)\s*([(\[])', r'\1 \2', text)

        # Espace après la fermeture (si pas suivi de ponctuation)
        text = re.sub(r'([)\]])\s*(\w)', r'\1 \2', text)

        # Pas d'espace à l'intérieur
        text = re.sub(r'([(\[])\s+', r'\1', text)
        text = re.sub(r'\s+([)\]])', r'\1', text)

        return text

    def correct(self, text):
        """Applique toutes les corrections typographiques"""

        # Extraire les blocs de code
        text = self.extract_code_blocks(text)

        # Appliquer les corrections
        text = self.fix_guillemets(text)
        text = self.fix_apostrophes(text)
        text = self.fix_punctuation(text)
        text = self.fix_numbers(text)
        text = self.fix_parentheses(text)

        # Restaurer les blocs de code
        text = self.restore_code_blocks(text)

        return text
    def fix_apostrophes(self, text):
        """Remplace les apostrophes droites par des apostrophes typographiques"""

        # Apostrophe typographique française
        APOSTROPHE = '\u2019'  # ' (U+2019)

        # Remplacer les apostrophes droites par des apostrophes typographiques
        # Mais SEULEMENT entre deux lettres (pour éviter les cas de code, mesures, etc.)
        text = re.sub(r"([a-zàâäéèêëïîôùûüÿæœçA-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÆŒÇ])'([a-zàâäéèêëïîôùûüÿæœç])",
                    rf"\1{APOSTROPHE}\2", text)

        return text


def make_spaces_visible(text, use_color=True):
    """Rend les espaces spéciales visibles avec des symboles colorés"""
    if use_color:
        # NNBSP en cyan avec fond
        text = text.replace(NNBSP, f'{Colors.BG_CYAN}{Colors.BOLD}{NNBSP_SYMBOL}{Colors.RESET}')
        # NBSP en jaune avec fond
        text = text.replace(NBSP, f'{Colors.BG_YELLOW}{Colors.BOLD}{NBSP_SYMBOL}{Colors.RESET}')
    else:
        # Version sans couleur pour export
        text = text.replace(NNBSP, f'[{NNBSP_SYMBOL}]')
        text = text.replace(NBSP, f'[{NBSP_SYMBOL}]')

    return text


def show_diff(original, corrected, filename, use_color=True):
    """Affiche un diff unifié entre l'original et le texte corrigé"""

    original_lines = original.splitlines(keepends=True)
    corrected_lines = corrected.splitlines(keepends=True)

    diff = unified_diff(
        original_lines,
        corrected_lines,
        fromfile=f"{filename} (original)",
        tofile=f"{filename} (corrigé)",
        lineterm=''
    )

    has_changes = False
    for line in diff:
        has_changes = True

        # Rendre les espaces spéciales visibles
        visible_line = make_spaces_visible(line, use_color)

        if use_color:  # ← SUPPRIMER le test sys.stdout.isatty()
            if line.startswith('---') or line.startswith('+++'):
                print(f"{Colors.BOLD}{visible_line}{Colors.RESET}")
            elif line.startswith('@@'):
                print(f"{Colors.CYAN}{visible_line}{Colors.RESET}")
            elif line.startswith('-'):
                print(f"{Colors.RED}{visible_line}{Colors.RESET}")
            elif line.startswith('+'):
                print(f"{Colors.GREEN}{visible_line}{Colors.RESET}")
            else:
                print(visible_line)
        else:
            print(visible_line)

    return has_changes


def show_char_legend(use_color=True):
    """Affiche la légende des caractères spéciaux"""
    print(f"\n{Colors.BOLD if use_color else ''}Légende des espaces :{Colors.RESET if use_color else ''}")

    if use_color:
        print(f"  • Espace insécable fine (NNBSP) : {Colors.BG_CYAN}{Colors.BOLD}{NNBSP_SYMBOL}{Colors.RESET} (U+202F) - avant :;!? et « »")
        print(f"  • Espace insécable (NBSP)       : {Colors.BG_YELLOW}{Colors.BOLD}{NBSP_SYMBOL}{Colors.RESET} (U+00A0)")
        print(f"  • Espace normale                : [espace simple]")
    else:
        print(f"  • Espace insécable fine (NNBSP) : [{NNBSP_SYMBOL}] (U+202F)")
        print(f"  • Espace insécable (NBSP)       : [{NBSP_SYMBOL}] (U+00A0)")
        print(f"  • Espace normale                : [espace simple]")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Correcteur de typographie française pour fichiers Markdown',
        epilog='Par défaut, les corrections sont appliquées. Utilisez --dry-run pour prévisualiser sans modifier les fichiers.'
    )
    parser.add_argument(
        'files',
        nargs='+',
        type=Path,
        help='Fichier(s) Markdown à corriger'
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Prévisualiser les corrections sans modifier les fichiers'
    )
    parser.add_argument(
        '--color',
        choices=['auto', 'always', 'never'],
        default='auto',
        help='Contrôle de la colorisation : auto (défaut), always, never'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Mode silencieux (pas de diff, juste le résumé)'
    )

    args = parser.parse_args()

    # Gérer la colorisation
    if args.color == 'never':
        use_color = False
    elif args.color == 'always':
        use_color = True
    else:  # auto
        use_color = sys.stdout.isatty()

    corrector = MarkdownTypoCorrector()

    total_files = 0
    modified_files = 0

    for input_file in args.files:
        if not input_file.exists():
            color_prefix = Colors.RED if use_color else ''
            color_suffix = Colors.RESET if use_color else ''
            print(f"{color_prefix}✗ Erreur : Le fichier {input_file} n'existe pas{color_suffix}")
            continue

        total_files += 1

        # Lire le contenu
        with open(input_file, 'r', encoding='utf-8') as f:
            original = f.read()

        # Appliquer les corrections
        corrected = corrector.correct(original)

        # Vérifier s'il y a des modifications
        if original == corrected:
            if not args.quiet:
                color_prefix = Colors.GREEN if use_color else ''
                color_suffix = Colors.RESET if use_color else ''
                print(f"{color_prefix}✓ {input_file} : Aucune correction nécessaire{color_suffix}\n")
            continue

        modified_files += 1

        # Afficher le header
        separator = '=' * 70
        if use_color:
            print(f"\n{Colors.BOLD}{separator}{Colors.RESET}")
            print(f"{Colors.BOLD}Fichier : {input_file}{Colors.RESET}")
            print(f"{Colors.BOLD}{separator}{Colors.RESET}\n")
        else:
            print(f"\n{separator}")
            print(f"Fichier : {input_file}")
            print(f"{separator}\n")

        # Afficher le diff en mode dry-run ou si demandé
        if not args.quiet:
            has_changes = show_diff(original, corrected, str(input_file), use_color)
            if has_changes:
                show_char_legend(use_color)

        # Appliquer les modifications sauf en dry-run
        if not args.dry_run:
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(corrected)
            color_prefix = Colors.GREEN if use_color else ''
            color_suffix = Colors.RESET if use_color else ''
            print(f"{color_prefix}✓ Modifications appliquées{color_suffix}\n")
        else:
            color_prefix = Colors.YELLOW if use_color else ''
            color_suffix = Colors.RESET if use_color else ''
            print(f"{color_prefix}ℹ Mode dry-run : aucune modification apportée au fichier{color_suffix}\n")

    # Résumé final
    separator = '=' * 70
    if use_color:
        print(f"{Colors.BOLD}{separator}{Colors.RESET}")
        print(f"{Colors.BOLD}Résumé :{Colors.RESET}")
    else:
        print(separator)
        print("Résumé :")

    print(f"  • Fichiers analysés : {total_files}")
    print(f"  • Fichiers à modifier : {modified_files}")

    if not args.dry_run and modified_files > 0:
        color_prefix = Colors.GREEN if use_color else ''
        color_suffix = Colors.RESET if use_color else ''
        print(f"  {color_prefix}• Modifications appliquées ✓{color_suffix}")
    elif modified_files > 0:
        color_prefix = Colors.YELLOW if use_color else ''
        color_suffix = Colors.RESET if use_color else ''
        print(f"  {color_prefix}• Mode dry-run (les fichiers n'ont pas été modifiés){color_suffix}")

    if use_color:
        print(f"{Colors.BOLD}{separator}{Colors.RESET}")
    else:
        print(separator)


if __name__ == "__main__":
    main()
