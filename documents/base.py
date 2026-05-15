from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Optional

import pygame

from core.constants import C
import core.fonts as _fonts_mod

PAD_X = 5
PAD_Y = 2


@dataclass
class ClickableField:

    key:        str
    label:      str
    value:      str
    group:      str
    source:     str
    local_rect: pygame.Rect
    screen_rect: Optional[pygame.Rect] = field(default=None, repr=False)

    def update_screen_rect(self, doc_topleft: tuple):
        ox, oy = doc_topleft
        self.screen_rect = pygame.Rect(
            self.local_rect.x + ox,
            self.local_rect.y + oy,
            self.local_rect.w,
            self.local_rect.h,
        )


class DocumentTemplate(abc.ABC):
    @property
    @abc.abstractmethod
    def source_id(self) -> str:
        pass

    @abc.abstractmethod
    def build(self, person) -> tuple:
       pass

    @staticmethod
    def _text(surf: pygame.Surface, msg: str, font_key: str, color,
              x: int, y: int, *, center: bool = False, right: bool = False) -> pygame.Rect:
        import core.fonts as _fonts_mod
        font = _fonts_mod.FONTS[font_key]
        s = font.render(str(msg), True, color)
        r = s.get_rect()
        if center:
            r.centerx = x; r.top = y
        elif right:
            r.right = x;   r.top = y
        else:
            r.left = x;    r.top = y
        surf.blit(s, r)
        return r

    @staticmethod
    def _field(surf: pygame.Surface, key: str, source: str, group: str,
               label: str, value: str, font_key: str, label_color, value_color,
               label_x: int, value_x: int, y: int) -> ClickableField:

        DocumentTemplate._text(surf, label + ":", font_key, label_color, label_x, y)
        r = DocumentTemplate._text(surf, value, font_key, value_color, value_x, y)
        local = pygame.Rect(r.left - PAD_X, r.top - PAD_Y,
                            r.width + PAD_X * 2, r.height + PAD_Y * 2)
        return ClickableField(key, f"{source.upper()} › {label}", value, group, source, local)

    @staticmethod
    def _photo_field(key: str, source: str, doc_index: int,
                     photo_rect: pygame.Rect) -> ClickableField:
        local = pygame.Rect(
            photo_rect.x - PAD_X, photo_rect.y - PAD_Y,
            photo_rect.w + PAD_X * 2, photo_rect.h + PAD_Y * 2,
        )
        return ClickableField(
            key, f"{source.upper()} › PHOTO",
            f"doc#{doc_index:03d}", "photo", source, local,
        )



class DocumentWidget:
    def __init__(self, template: DocumentTemplate, person, start_pos: tuple):
        self.template = template
        surf, fields  = template.build(person)
        self.surf:   pygame.Surface        = surf
        self.fields: list[ClickableField]  = fields
        self.rect    = pygame.Rect(start_pos[0], start_pos[1],
                                   surf.get_width(), surf.get_height())
        self.dragging   = False
        self.drag_off   = (0, 0)
        self.stamp:       Optional[str] = None
        self.stamp_alpha: int           = 0

    def update_rects(self):
        for f in self.fields:
            f.update_screen_rect(self.rect.topleft)

    def set_stamp(self, text: str):
        self.stamp       = text
        self.stamp_alpha = 50

    def draw(self, surf: pygame.Surface, inv_active: bool, selected_keys: list):
        surf.blit(self.surf, self.rect)

        if inv_active:
            for f in self.fields:
                if f.screen_rect is None:
                    continue
                if len(selected_keys) > 0 and f.key == selected_keys[0]:
                    col, th = C["inv_sel1"], 2
                elif len(selected_keys) > 1 and f.key == selected_keys[1]:
                    col, th = C["inv_sel2"], 2
                else:
                    col, th = (80, 160, 80), 1
                hl = pygame.Surface((f.screen_rect.w, f.screen_rect.h), pygame.SRCALPHA)
                hl.fill((col[0], col[1], col[2], 35))
                surf.blit(hl, f.screen_rect.topleft)
                pygame.draw.rect(surf, col, f.screen_rect, th, border_radius=2)

        if self.stamp and self.stamp_alpha > 0:
            if self.stamp == "APPROVED":
                stamp_col = C["stamp_appr"]
            elif self.stamp == "DETAINED":
                stamp_col = (200, 120, 30)
            else:
                stamp_col = C["stamp_deny"]
            stamp_s = _fonts_mod.FONTS["stamp"].render(
                self.stamp, True, stamp_col,
            )
            stamp_s.set_alpha(min(255, self.stamp_alpha))
            rotated = pygame.transform.rotate(stamp_s, -20)
            rr = rotated.get_rect(center=self.rect.center)
            surf.blit(rotated, rr)
            if self.stamp_alpha < 255:
                self.stamp_alpha += 12

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_off = (event.pos[0] - self.rect.x,
                                 event.pos[1] - self.rect.y)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] - self.drag_off[0]
                self.rect.y = event.pos[1] - self.drag_off[1]