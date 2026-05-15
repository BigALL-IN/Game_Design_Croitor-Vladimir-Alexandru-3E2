from __future__ import annotations

from typing import Optional

import pygame

from core.constants import C, W, H, CURRENT_YEAR
import core.fonts as _fonts_mod
from documents.base import ClickableField


def _F(key):
    return _fonts_mod.FONTS[key]


_SOURCE_LABEL = {
    "passport": "PASSPORT",
    "id": "ID CARD",
    "work_permit": "WORK PERMIT",
    "entry_permit": "ENTRY PERMIT",
    "traveler": "TRAVELER",
}


def _src(f: ClickableField) -> str:
    return _SOURCE_LABEL.get(f.source, f.source.upper())


def evaluate_cross_check(f1: ClickableField, f2: ClickableField,
                         person, allowed_nations: set | None = None) -> tuple:

    if f1.key == f2.key:
        return False, None, "SELECT TWO DIFFERENT FIELDS"

    g1, g2 = f1.group, f2.group
    tag = f"{_src(f1)} vs {_src(f2)}"

    if "expiry" in (g1, g2):
        exp = f1 if g1 == "expiry" else f2
        try:
            year = int(exp.value.split(".")[-1])
        except ValueError:
            return True, False, f"{_src(exp)}  —  UNREADABLE EXPIRY DATE"
        if year < CURRENT_YEAR:
            return True, False, f"{_src(exp)}  —  DOCUMENT EXPIRED ({year} < {CURRENT_YEAR})"
        return True, True, f"{_src(exp)}  —  DOCUMENT VALID UNTIL {year}"

    if g1 == g2 and g1 != "":
        if g1 == "name":
            ok = f1.value.strip().upper() == f2.value.strip().upper()
            return True, ok, (
                f"{tag}  —  NAMES MATCH"
                if ok else f"{tag}  —  NAME MISMATCH"
            )
        if g1 == "birth":
            ok = f1.value.strip() == f2.value.strip()
            return True, ok, (
                f"{tag}  —  BIRTH DATES MATCH"
                if ok else f"{tag}  —  BIRTH DATE MISMATCH"
            )
        if g1 == "nation":
            ok = f1.value.strip().upper() == f2.value.strip().upper()
            if ok and allowed_nations is not None:
                nation_val = f1.value.strip()
                if nation_val not in allowed_nations:
                    return True, False, f"{tag}  —  {nation_val} NOT PERMITTED TODAY"
            return True, ok, (
                f"{tag}  —  NATIONS MATCH  [{f1.value}]"
                if ok else
                f"{tag}  —  NATION MISMATCH  [{f1.value} vs {f2.value}]"
            )
        if g1 == "sex":
            ok = f1.value.strip().upper() == f2.value.strip().upper()
            return True, ok, (
                f"{tag}  —  SEX FIELDS MATCH"
                if ok else f"{tag}  —  SEX FIELD MISMATCH"
            )
        if g1 == "photo":
            ok = person.doc_index == person.face_index
            return True, ok, (
                f"{tag}  —  PHOTO MATCHES TRAVELER"
                if ok else f"{tag}  —  PHOTO DOES NOT MATCH TRAVELER"
            )

    return False, None, "NO CORRELATION  —  THESE FIELDS ARE UNRELATED"


class InvestigationController:
    def __init__(self):
        self.active = False
        self.selected: list  = []
        self.all_fields: list = []
        self.result_msg = ""
        self.result_ok: Optional[bool] = None
        self.result_timer = 0
        self._person = None
        self._allowed: set = set()
        self._traveler_fields: list = []

    def enter(self, person, allowed: set, doc_fields: list, traveler_fields: list):
        self.active = True
        self._person = person
        self._allowed = allowed
        self._traveler_fields = traveler_fields
        self.selected = []
        self.result_msg = ""
        self.result_ok = None
        self.result_timer = 0
        self.all_fields = doc_fields + traveler_fields

    def refresh(self, doc_fields: list):
        self.all_fields = doc_fields + self._traveler_fields

    def exit(self):
        self.active   = False
        self.selected = []

    def try_click(self, pos) -> bool:
        if not self.active:
            return False
        for f in self.all_fields:
            if f.screen_rect and f.screen_rect.collidepoint(pos):
                self._select(f)
                return True
        return False

    def _select(self, f: ClickableField):
        if f.key in self.selected:
            self.selected.remove(f.key)
            return
        self.selected.append(f.key)
        if len(self.selected) > 2:
            self.selected = self.selected[-2:]
        if len(self.selected) == 2:
            self._evaluate()

    def _evaluate(self):
        key_map = {f.key: f for f in self.all_fields}
        f1 = key_map.get(self.selected[0])
        f2 = key_map.get(self.selected[1])
        if f1 and f2:
            _, ok, msg = evaluate_cross_check(f1, f2, self._person, self._allowed)
            self.result_ok    = ok
            self.result_msg   = msg
            self.result_timer = 220

    def draw_result_banner(self, surf: pygame.Surface):
        if not self.active:
            return

        bar = pygame.Surface((W, 20), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 140))
        surf.blit(bar, (0, 400))
        font = _F("small")
        msg  = ("[ INVESTIGATION ]  Click any field on the documents or traveler"
                "  |  SPACE to exit")
        s = font.render(msg, True, C["inv_mode"])
        surf.blit(s, s.get_rect(centerx=W // 2, centery=404))

        if not (self.result_msg and self.result_timer > 0):
            return
        self.result_timer -= 1
        alpha = min(255, self.result_timer * 2)

        if self.result_ok is True:
            bg_col, txt_col, icon = (15, 60, 25),  C["inv_ok"],   "✓"
        elif self.result_ok is False:
            bg_col, txt_col, icon = (70, 12, 12),  C["inv_bad"],  "✗"
        else:
            bg_col, txt_col, icon = (25, 25, 55),  C["inv_none"], "?"

        bw, bh = 720, 52
        bx = (W - bw) // 2
        by = H - bh - 85

        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        r, g, b = bg_col
        bg.fill((r, g, b, min(220, alpha)))
        surf.blit(bg, (bx, by))
        pygame.draw.rect(surf, txt_col, (bx, by, bw, bh), 2, border_radius=5)

        s = _F("title").render(f"[{icon}]  {self.result_msg}", True, txt_col)
        s.set_alpha(alpha)
        surf.blit(s, s.get_rect(centerx=W // 2, centery=by + bh // 2))

        if len(self.selected) == 2:
            key_map = {f.key: f for f in self.all_fields if f.screen_rect}
            rf1 = key_map.get(self.selected[0])
            rf2 = key_map.get(self.selected[1])
            if rf1 and rf2:
                c1, c2 = rf1.screen_rect.center, rf2.screen_rect.center
                ls = pygame.Surface((W, H), pygame.SRCALPHA)
                lc = (*txt_col, min(150, alpha))
                pygame.draw.line(ls, lc, c1, c2, 2)
                pygame.draw.circle(ls, lc, c1, 5)
                pygame.draw.circle(ls, lc, c2, 5)
                surf.blit(ls, (0, 0))