import re
import argparse
import os

# Dictionnaire de mappage des emojis Notion vers les types de 'callouts' Starlight
EMOJI_TO_TYPE_MAP = {
    '💡': 'tip', 'ℹ️': 'note', '📝': 'note', '⚠️': 'caution',
    '🔥': 'danger', '❌': 'danger', '✅': 'note', '❓': 'note',
    '👉': 'note', '🎯': 'note',
}

def convert_blockquote_callouts(content):
    """Convertit les encadrés au format blockquote."""
    callout_pattern = re.compile(
        r'^> ([\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\u2600-\u26FF\u2700-\u27BF]+)\s*\*\*(.*?)\*\*\n((?:> .*\n?)*)',
        re.MULTILINE
    )
    def replace_callout(match):
        emoji, title, body = match.groups()
        aside_type = EMOJI_TO_TYPE_MAP.get(emoji, 'note')
        cleaned_body = re.sub(r'^> ', '', body, flags=re.MULTILINE)
        return f'<Aside type="{aside_type}" title="{title.strip()}">\n{cleaned_body.strip()}\n</Aside>'
    return callout_pattern.sub(replace_callout, content)

def convert_aside_tag_callouts(content):
    """Convertit les encadrés au format <aside>."""
    aside_pattern = re.compile(
        r'<aside>\s*([\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\u2600-\u26FF\u2700-\u27BF]+)\s*\n+\s*\*\*(.*?):?\*\*\s*\n(.*?)\s*<\/aside>',
        re.DOTALL
    )
    def replace_aside(match):
        emoji, title, body = match.groups()
        aside_type = EMOJI_TO_TYPE_MAP.get(emoji, 'note')
        return f'<Aside type="{aside_type}" title="{title.strip()}">\n{body.strip()}\n</Aside>'
    return aside_pattern.sub(replace_aside, content)

def convert_toggles(content):
    """Convertit les blocs pliables <details> en <Details>."""
    toggle_pattern = re.compile(r'<details><summary>(.*?)<\/summary>(.*?)<\/details>', re.DOTALL)
    replacement = r'<Details summary="\1">\2</Details>'
    return toggle_pattern.sub(replacement, content)

def main():
    parser = argparse.ArgumentParser(
        description="Convertit un fichier Markdown/MDX de Notion au format Astro Starlight."
    )
    parser.add_argument("input_file", help="Chemin vers le fichier d'entrée.")
    parser.add_argument("output_file", help="Chemin vers le fichier de sortie (ex: page.mdx).")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Erreur : Le fichier d'entrée '{args.input_file}' n'a pas été trouvé.")
        return

    print(f"📖 Lecture de '{args.input_file}'...")
    with open(args.input_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Chaîne de conversion
    content_step1 = convert_blockquote_callouts(original_content)
    content_step2 = convert_aside_tag_callouts(content_step1)
    final_content = convert_toggles(content_step2)

    # --- NOUVELLE PARTIE : Ajout des imports MDX ---
    components_to_import = []
    if '<Aside' in final_content:
        components_to_import.append('Aside')
    if '<Details' in final_content:
        components_to_import.append('Details')

    if components_to_import:
        import_string = ", ".join(components_to_import)
        import_line = f"import {{ {import_string} }} from '@astrojs/starlight/components';\n\n"
        final_content = import_line + final_content
        print(f"✨ Ajout de l'import MDX pour : {import_string}")
    # --- FIN DE LA NOUVELLE PARTIE ---

    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    print(f"💾 Sauvegarde dans '{args.output_file}'...")
    with open(args.output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print("✅ Conversion terminée avec succès !")

if __name__ == "__main__":
    main()