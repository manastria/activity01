#!/usr/bin/env python3
# tools/migrate_markdown_images.py
#
# Migre les images référencées en Markdown relatif (ex: ![](20260207230513.png))
# vers public/images/activities/<activitySlug>/<pageStem>/, puis remplace la syntaxe
# Markdown par un composant ImageFigure (ou ImageFigureViewer).
#
# - Déduit activitySlug depuis src/content/docs/activities/<slug>/...
# - Déduit pageStem depuis le nom du fichier .mdx (index/reset/...)
# - Option --viewer pour utiliser ImageFigureViewer
# - Ajoute automatiquement l'import dans le .mdx si absent

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from dataclasses import dataclass


FRONTMATTER_RE = re.compile(r"(?s)\A---\s*\n.*?\n---\s*\n")
IMPORT_RE = re.compile(r'(?m)^\s*import\s+(\w+)\s+from\s+["\']([^"\']+)["\']\s*;\s*$')

# Markdown image: ![alt](path "title")
MD_IMG_RE = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<inside>[^)]+)\)')

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif"}


@dataclass
class ReplacePlan:
    mdx: Path
    src_abs: Path
    dst_abs: Path
    dst_web: str
    alt: str
    title: str | None
    original_markdown: str
    replacement: str


def parse_md_inside(inside: str) -> tuple[str, str | None]:
    """
    inside = 'path "title"' or 'path'
    Returns: (path, title|None)
    """
    inside = inside.strip()
    # Split first token as path, optional title in quotes after
    # Handle titles with spaces: "..."
    if '"' in inside:
        # path then title
        parts = inside.split('"')
        path_part = parts[0].strip()
        title = parts[1].strip() if len(parts) > 1 else None
        return path_part, (title or None)
    return inside.split()[0], None


def unique_dest(dst: Path) -> Path:
    if not dst.exists():
        return dst
    stem, suffix = dst.stem, dst.suffix
    for i in range(1, 1000):
        cand = dst.with_name(f"{stem}-{i}{suffix}")
        if not cand.exists():
            return cand
    raise RuntimeError(f"Trop de conflits de nom pour {dst}")


def has_import(text: str, component_name: str, from_path: str) -> bool:
    for m in IMPORT_RE.finditer(text):
        if m.group(1) == component_name and m.group(2) == from_path:
            return True
    return False


def insert_import(text: str, import_line: str) -> str:
    # Insert after frontmatter (if any), otherwise at top.
    fm = FRONTMATTER_RE.match(text)
    if fm:
        pos = fm.end()
        return text[:pos] + import_line + "\n" + text[pos:]
    return import_line + "\n\n" + text


def is_relative_image_ref(p: str) -> bool:
    p = p.strip()
    if not p:
        return False
    # Already in new workflow or external
    if p.startswith(("http://", "https://", "data:", "/images/", "/activity01/")):
        return False
    # MDX absolute root
    if p.startswith("/"):
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=None, help="Racine du projet (défaut: parent de tools/)")
    ap.add_argument("--write", action="store_true", help="Applique les déplacements et réécrit les fichiers")
    ap.add_argument("--viewer", action="store_true", help="Utilise ImageFigureViewer au lieu de ImageFigure")
    args = ap.parse_args()

    root = args.root or Path(__file__).resolve().parents[1]
    activities_dir = root / "src" / "content" / "docs" / "activities"
    public_dir = root / "public"

    if not activities_dir.exists():
        raise SystemExit(f"Introuvable: {activities_dir}")

    component = "ImageFigureViewer" if args.viewer else "ImageFigure"
    component_import = f'import {component} from "@/components/{component}.astro";'

    plans: list[ReplacePlan] = []

    for mdx in sorted(activities_dir.rglob("*.mdx")):
        rel = mdx.relative_to(activities_dir)  # ex: sns/reset.mdx
        if len(rel.parts) < 2:
            continue

        activity_slug = rel.parts[0]
        page_stem = mdx.stem  # reset, index, ...

        text = mdx.read_text(encoding="utf-8")

        for m in MD_IMG_RE.finditer(text):
            alt = (m.group("alt") or "").strip()
            inside = m.group("inside")
            path_part, title = parse_md_inside(inside)

            if not is_relative_image_ref(path_part):
                continue

            # Resolve local file relative to mdx
            src_abs = (mdx.parent / path_part).resolve()
            if src_abs.suffix.lower() not in IMAGE_EXTS:
                continue
            if not src_abs.exists():
                # On ignore si le fichier n'existe pas (cas à traiter manuellement)
                continue

            dest_dir = public_dir / "images" / "activities" / activity_slug / page_stem
            dest_dir.mkdir(parents=True, exist_ok=True)

            dst_abs = unique_dest(dest_dir / src_abs.name)
            dst_web = "/" + str(dst_abs.relative_to(public_dir)).replace("\\", "/")

            # Build replacement component call
            # Use JSON to safely quote strings
            src_js = json.dumps(dst_web, ensure_ascii=False)
            alt_js = json.dumps(alt, ensure_ascii=False) if alt else '""'
            if title:
                cap_js = json.dumps(title, ensure_ascii=False)
                replacement = f"<{component} src={src_js} alt={alt_js} caption={cap_js} />"
            else:
                replacement = f"<{component} src={src_js} alt={alt_js} />"

            plans.append(ReplacePlan(
                mdx=mdx,
                src_abs=src_abs,
                dst_abs=dst_abs,
                dst_web=dst_web,
                alt=alt,
                title=title,
                original_markdown=m.group(0),
                replacement=replacement,
            ))

    if not plans:
        print("Aucune image Markdown relative trouvée à migrer.")
        return 0

    print(f"{len(plans)} image(s) à migrer :")
    for p in plans:
        print(f"- {p.mdx.relative_to(root)} : {p.src_abs.name} -> {p.dst_web}")

    if not args.write:
        print("\nDry-run. Ajoute --write pour appliquer.")
        return 0

    # Group by MDX to minimize reads/writes
    by_mdx: dict[Path, list[ReplacePlan]] = {}
    for p in plans:
        by_mdx.setdefault(p.mdx, []).append(p)

    for mdx, items in by_mdx.items():
        text = mdx.read_text(encoding="utf-8")

        # Ensure import exists
        if not has_import(text, component, f"@/components/{component}.astro"):
            text = insert_import(text, component_import)

        # Move files + rewrite occurrences
        for p in items:
            p.dst_abs.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p.src_abs), str(p.dst_abs))
            text = text.replace(p.original_markdown, p.replacement)

        mdx.write_text(text, encoding="utf-8")

    print("\n✓ Migration terminée.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
