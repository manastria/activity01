/**
 * Utilitaires partagés pour les composants d'images
 */

export interface ManifestEntry {
  full: { avif: string | null; webp: string | null; fallback: string };
  thumb: { avif: string | null; webp: string | null; fallback: string | null };
}

export type ImageManifest = Record<string, ManifestEntry>;

/**
 * Préfixe base (ex: "/activity01/") aux chemins "public"
 */
export function withBase(path: string | null): string | null {
  if (!path) return null;
  const base = import.meta.env.BASE_URL ?? "/";
  return base.replace(/\/$/, "") + "/" + String(path).replace(/^\/+/, "");
}

/**
 * Charge le manifest d'images optimisées
 */
export async function loadManifest(): Promise<ImageManifest> {
  try {
    return (await import("../data/images.manifest.json")).default;
  } catch {
    return {};
  }
}

/**
 * Résout les chemins d'une image depuis le manifest
 */
export function resolveImage(manifest: ImageManifest, src: string) {
  const entry = manifest[src];
  return entry?.full ?? { avif: null, webp: null, fallback: src };
}
