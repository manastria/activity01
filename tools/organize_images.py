#!/usr/bin/env python3
# tools/organize_images.py
# Range les images collées dans public/images/_inbox vers public/images/activities/<activity>/<page>/,
# puis réécrit les liens dans les fichiers .mdx.

from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


INBOX_WEB_PREFIX = "/images/_inbox/"
DEST_WEB_PREFIX = "/images/activities/"


@dataclass
class MovePlan:
    mdx_path: Path
    src_web: str
    src_abs: Path
    dst_web: str
    dst_abs: Path


FRONTMATTER_RE = re.compile(r"(?s)\A---\s*\n(.*?)\n---\s*\n")
SLUG_LINE_RE = re.compile(r"(?m)^\s*slug\s*:\s*(.+?)\s*$")

# Capture des chemins web /images/_inbox/... dans des contextes variés :
# - Markdown: ![](...)
# - attributs/objets: "src": "..."
# - liens simples: (...), "...", etc.
INBOX_PATH_RE = re.compile(r"(?P<p>/images/_inbox/[^\s\"')\]]+)")


def parse_frontmatter_slug(text: str) -> str | None:
    m = FRONTMATTER_RE.search(text)
    if not m:
        return None
    fm = m.group(1)
    s = SLUG_LINE_RE.search(fm)
    if not s:
        return None
    val = s.group(1).strip()
    # retire guillemets simples/doubles
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1].strip()
    return val or None


def unique_dest_path(dst_abs: Path) -> Path:
    if not dst_abs.exists():
        return dst_abs
    stem, suffix = dst_abs.stem, dst_abs.suffix
    for i in range(1, 1000):
        cand = dst_abs.with_name(f"{stem}-{i}{suffix}")
        if not cand.exists():
            return cand
    raise RuntimeError(f"Too many conflicts for {dst_abs}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=None, help="Racine du projet (défaut: parent de tools/)")
    ap.add_argument("--write", action="store_true", help="Applique les déplacements et réécrit les fichiers")
    ap.add_argument("--strict", action="store_true", help="Échoue si un fichier image référencé est introuvable")
    args = ap.parse_args()

    root = args.root or Path(__file__).resolve().parents[1]
    activities_dir = root / "src" / "content" / "docs" / "activities"
    public_dir = root / "public"

    if not activities_dir.exists():
        raise SystemExit(f"Introuvable: {activities_dir}")

    mdx_files = sorted(list(activities_dir.rglob("*.mdx")))
    plans: list[MovePlan] = []
    missing: list[tuple[Path, str]] = []

    for mdx in mdx_files:
        rel = mdx.relative_to(activities_dir)  # ex: sns/reset.mdx
        parts = rel.parts
        if len(parts) < 2:
            # activities/<slug>/index.mdx minimum
            continue

        folder_slug = parts[0]
        page_stem = mdx.stem  # reset, index, ...
        text = mdx.read_text(encoding="utf-8")

        fm_slug = parse_frontmatter_slug(text)
        activity_slug = fm_slug or folder_slug

        # destination = /public/images/activities/<activity>/<page>/
        dest_dir_abs = public_dir / "images" / "activities" / activity_slug / page_stem

        # collecte des occurrences inbox
        found = sorted(set(m.group("p") for m in INBOX_PATH_RE.finditer(text)))
        if not found:
            continue

        for src_web in found:
            src_abs = public_dir / src_web.lstrip("/")
            if not src_abs.exists():
                missing.append((mdx, src_web))
                continue

            dst_abs = dest_dir_abs / src_abs.name
            dst_abs = unique_dest_path(dst_abs)
            dst_web = "/" + str(dst_abs.relative_to(public_dir)).replace("\\", "/")

            plans.append(MovePlan(
                mdx_path=mdx,
                src_web=src_web,
                src_abs=src_abs,
                dst_web=dst_web,
                dst_abs=dst_abs
            ))

    # Rapport
    if plans:
        print(f"{len(plans)} image(s) à déplacer/réécrire :")
        for p in plans:
            print(f"- {p.mdx_path.relative_to(root)}")
            print(f"  {p.src_web}  ->  {p.dst_web}")
    else:
        print("Aucune image INBOX trouvée dans les MDX.")
    if missing:
        print(f"\n{len(missing)} référence(s) image introuvable(s) :")
        for mdx, src_web in missing:
            print(f"- {mdx.relative_to(root)} : {src_web}")
        if args.strict:
            return 2

    if not args.write:
        print("\nDry-run. Ajoute --write pour appliquer.")
        return 0

    # Appliquer : déplacer fichiers + réécrire MDX
    by_mdx: dict[Path, list[MovePlan]] = {}
    for p in plans:
        by_mdx.setdefault(p.mdx_path, []).append(p)

    for mdx, mp in by_mdx.items():
        text = mdx.read_text(encoding="utf-8")

        # déplacer fichiers
        for p in mp:
            p.dst_abs.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p.src_abs), str(p.dst_abs))

        # réécriture liens
        for p in mp:
            text = text.replace(p.src_web, p.dst_web)

        mdx.write_text(text, encoding="utf-8")

    print("\n✓ Organize done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
