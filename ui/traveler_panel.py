import pygame

from core.constants import C, W
import core.assets as _assets
from core.draw_utils import text
from documents.base import ClickableField

NPC_PANEL_RECT = pygame.Rect(W - 340, 20, 320, 360)


def make_traveler_fields(person, panel_rect: pygame.Rect) -> list:
    face_rect = pygame.Rect(panel_rect.centerx - 90, panel_rect.top + 50, 180, 180)
    name_rect = pygame.Rect(panel_rect.left + 10, panel_rect.bottom - 74,
                            panel_rect.width - 20, 18)
    nation_rect = pygame.Rect(panel_rect.left + 10, panel_rect.bottom - 54,
                              panel_rect.width - 20, 18)
    fields = [
        ClickableField("tr_face",   "TRAVELER › FACE",
                       f"face#{person.face_index:03d}", "photo", "traveler", face_rect),
        ClickableField("tr_name",   "TRAVELER › NAME",
                       person.full_name, "name", "traveler", name_rect),
        ClickableField("tr_nation", "TRAVELER › NATION",
                       person.nation, "nation", "traveler", nation_rect),
    ]
    for f in fields:
        f.screen_rect = pygame.Rect(f.local_rect)
    return fields


def draw_traveler_panel(surf: pygame.Surface, person, inv_active: bool,
                        selected_keys: list, traveler_fields: list,
                        interrog_active: bool = False):
    wr = NPC_PANEL_RECT
    pygame.draw.rect(surf, C["npc_bg"], wr, border_radius=6)
    pygame.draw.rect(surf, C["border"], wr, 3, border_radius=6)
    text(surf, "TRAVELER", "title", C["gold"], wr.centerx, 28, center=True)

    face_img = _assets.ASSETS.get_face(person.face_index, (180, 180))
    sx, sy = wr.centerx - 90, wr.top + 50
    surf.blit(face_img, (sx, sy))
    pygame.draw.rect(surf, C["border"], (sx - 2, sy - 2, 184, 184), 2)

    nt = pygame.Rect(wr.left + 10, wr.bottom - 80, wr.width - 20, 70)
    pygame.draw.rect(surf, (30, 50, 30), nt, border_radius=4)
    pygame.draw.rect(surf, C["border"], nt, 1, border_radius=4)
    text(surf, person.full_name,           "title", C["cream"],      nt.centerx, nt.top + 6,  center=True)
    text(surf, f"From: {person.nation}",   "mono",  C["text_light"], nt.centerx, nt.top + 26, center=True)
    text(surf, f"Occupation: {person.occupation}", "small", C["text_dim"], nt.centerx, nt.top + 44, center=True)

    if interrog_active:
        hint = "[Q] Exit Interrogation"
        hint_col = C["inv_mode"]
    elif inv_active:
        hint = "[SPACE] Exit Investigate"
        hint_col = C["inv_mode"]
    else:
        hint = "[SPACE] Investigate  [Q] Interrogate"
        hint_col = C["text_dim"]
    text(surf, hint, "small", hint_col, wr.centerx, wr.bottom + 8, center=True)

    if inv_active or interrog_active:
        for f in traveler_fields:
            if f.screen_rect is None:
                continue
            sel = selected_keys
            if len(sel) > 0 and f.key == sel[0]:
                col, th = C["inv_sel1"], 2
            elif len(sel) > 1 and f.key == sel[1]:
                col, th = C["inv_sel2"], 2
            else:
                col, th = (80, 160, 80), 1
            hl = pygame.Surface((f.screen_rect.w, f.screen_rect.h), pygame.SRCALPHA)
            hl.fill((col[0], col[1], col[2], 35))
            surf.blit(hl, f.screen_rect.topleft)
            pygame.draw.rect(surf, col, f.screen_rect, th, border_radius=2)
