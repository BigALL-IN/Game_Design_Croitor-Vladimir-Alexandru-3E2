import re
import random
from pathlib import Path

import pygame

from core.constants import FACE_DIR, DOC_DIR, C

_IMG_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}


def _load_indexed_images(folder: Path, prefix: str) -> dict:
    result  = {}
    if not folder.exists():
        return result
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)$", re.IGNORECASE)
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() not in _IMG_EXTS:
            continue
        m = pattern.match(f.stem)
        if m:
            idx = int(m.group(1))
            try:
                result[idx] = pygame.image.load(str(f))
            except Exception as e:
                print(f"[warn] Could not load {f}: {e}")
    return result


def _make_placeholder(w: int, h: int, label: str) -> pygame.Surface:
    import core.fonts as _fonts_mod
    surf = pygame.Surface((w, h))
    surf.fill(C["placeholder"])
    pygame.draw.rect(surf, C["border"], (0, 0, w, h), 2)
    lines = [label[i:i+12] for i in range(0, len(label), 12)]
    for i, line in enumerate(lines):
        s = _fonts_mod.FONTS["small"].render(line, True, C["text_dim"])
        r = s.get_rect(centerx=w // 2, centery=h // 2 - 8 + i * 14)
        surf.blit(s, r)
    return surf


class AssetLibrary:
    FACE_PREFIX = "NPC"
    DOC_PREFIX  = "NPC_Document"

    def __init__(self):
        self._faces       = _load_indexed_images(FACE_DIR, self.FACE_PREFIX)
        self._docs        = _load_indexed_images(DOC_DIR,  self.DOC_PREFIX)
        self.face_indices = sorted(self._faces.keys())
        self.doc_indices  = sorted(self._docs.keys())
        print(f"[assets] Loaded {len(self._faces)} face(s): {self.face_indices}")
        print(f"[assets] Loaded {len(self._docs)}  document(s): {self.doc_indices}")

    def get_face(self, index: int, size: tuple) -> pygame.Surface:
        if index in self._faces:
            src = self._faces[index]
            try:
                src = src.convert_alpha()
                self._faces[index] = src
            except Exception:
                pass
            return pygame.transform.smoothscale(src, size)
        return _make_placeholder(*size, f"NPC_{index:03d}")

    def get_doc_photo(self, index: int, size: tuple) -> pygame.Surface:
        if index in self._docs:
            src = self._docs[index]
            try:
                src = src.convert_alpha()
                self._docs[index] = src
            except Exception:
                pass
            return pygame.transform.smoothscale(src, size)
        return _make_placeholder(*size, f"DOC_{index:03d}")

    def random_face_index(self) -> int:
        return random.choice(self.face_indices) if self.face_indices else random.randint(1, 999)

    def random_different_doc_index(self, exclude: int) -> int:
        candidates = [i for i in self.doc_indices if i != exclude]
        return random.choice(candidates) if candidates else (exclude % 999) + 1


ASSETS: AssetLibrary = None  # type: ignore


def init_assets() -> AssetLibrary:
    global ASSETS
    ASSETS = AssetLibrary()
    return ASSETS