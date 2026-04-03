import pygame

from core.constants import C, W, H, CURRENT_YEAR
import core.fonts as _fonts_mod
from core.draw_utils import text

BOOK_RECT = pygame.Rect(W - 175, 428, 145, 92)


class RuleBook:
    def __init__(self):
        self.open = False

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if BOOK_RECT.collidepoint(event.pos):
                self.open = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.open = False

    def draw_closed(self, surf: pygame.Surface):
        r = BOOK_RECT
        pygame.draw.rect(surf, C["book_bg"], r, border_radius=5)
        pygame.draw.rect(surf, (55, 33, 8), (r.left, r.top, 14, r.height), border_radius=4)
        for i in range(1, 6):
            pygame.draw.line(surf, (70, 42, 15),
                             (r.left + 14, r.top + i * (r.height // 6)),
                             (r.right - 3,  r.top + i * (r.height // 6)), 1)
        text(surf, "RULE",    "small", C["cream"],    r.centerx + 6, r.top + 14, center=True)
        text(surf, "BOOK",    "small", C["cream"],    r.centerx + 6, r.top + 30, center=True)
        text(surf, "1982 ED", "small", (160, 130, 70), r.centerx + 6, r.top + 48, center=True)
        text(surf, "[click]", "small", C["text_dim"], r.centerx + 6, r.top + 66, center=True)
        pygame.draw.rect(surf, (50, 30, 8), r, 2, border_radius=5)

    def draw_overlay(self, surf: pygame.Surface, allowed_nations):
        if not self.open:
            return

        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 170))
        surf.blit(dim, (0, 0))

        bw, bh = 720, 480
        bx = (W - bw) // 2
        by = (H - bh) // 2

        pygame.draw.rect(surf, (222, 212, 182), (bx + bw // 2, by, bw // 2, bh), border_radius=6)
        pygame.draw.rect(surf, C["book_page"],  (bx, by, bw // 2, bh), border_radius=6)
        pygame.draw.rect(surf, (140, 110, 60),  (bx + bw // 2 - 7, by, 14, bh))
        pygame.draw.rect(surf, (90, 65, 30),    (bx, by, bw, bh), 3, border_radius=6)

        lx, ly = bx + 22, by + 22
        text(surf, "BORDER CONTROL REGULATIONS", "book_t", (70, 40, 10), lx, ly)
        text(surf, "Ministry of Admission — Edition 1982", "small", (140, 110, 60), lx, ly + 20)
        pygame.draw.line(surf, (160, 130, 70), (lx, ly + 36), (bx + bw // 2 - 18, ly + 36), 1)

        rules = [
            ("REQUIRED DOCUMENTS",               True),
            ("Every traveler must present:",      False),
            ("  1. A valid Passport",             False),
            ("  2. A Citizen ID Card",            False),
            ("",                                  False),
            ("PASSPORT CHECKS",                   True),
            ("- Must not be expired (>= 1982)",   False),
            ("- Issuing nation must match ID",    False),
            ("- Photo must match the traveler",   False),
            ("",                                  False),
            ("ID CARD CHECKS",                    True),
            ("- Name must match passport",        False),
            ("- Birth date must match passport",  False),
            ("- Photo must match the traveler",   False),
            ("",                                  False),
            ("VERDICTS",                          True),
            ("APPROVE  [A]  — all checks pass",   False),
            ("DENY  [D]  — any check fails",      False),
            ("",                                  False),
            ("INVESTIGATION  [SPACE]",            True),
            ("Press SPACE to enter/exit mode.",   False),
            ("Click any text or photo on the",    False),
            ("documents or traveler panel.",      False),
            ("Select 2 fields to cross-check.",   False),
            ("",                                  False),
            ("Press ESC to close this book",      False),
        ]
        for i, (line, header) in enumerate(rules):
            col  = (80, 45, 10) if header else (35, 30, 20)
            fkey = "book_t" if header else "book"
            text(surf, line, fkey, col, lx, ly + 46 + i * 16)

        rx, ry = bx + bw // 2 + 20, by + 22
        text(surf, "TODAY'S BULLETIN", "book_t", (70, 40, 10), rx, ry)
        text(surf, f"Date: 12.11.{CURRENT_YEAR}", "small", (140, 110, 60), rx, ry + 20)
        pygame.draw.line(surf, (160, 130, 70), (rx, ry + 36), (bx + bw - 18, ry + 36), 1)
        text(surf, "PERMITTED NATIONS:", "book_t", (70, 40, 10), rx, ry + 50)

        for i, nation in enumerate(allowed_nations):
            nr = pygame.Rect(rx + 4, ry + 70 + i * 26, bw // 2 - 44, 22)
            pygame.draw.rect(surf, (160, 200, 140), nr, border_radius=3)
            pygame.draw.rect(surf, (80, 140, 60), nr, 1, border_radius=3)
            text(surf, f"  ✓  {nation}", "book_t", (20, 80, 20), nr.left + 4, nr.top + 3)

        denied_y = ry + 78 + len(allowed_nations) * 26
        pygame.draw.line(surf, (160, 130, 70), (rx, denied_y), (bx + bw - 18, denied_y), 1)
        text(surf, "ALL OTHER NATIONS:", "book_t", (160, 40, 40), rx, denied_y + 8)
        text(surf, "  ✗  Entry Denied",  "book",   (180, 50, 50), rx, denied_y + 26)

        st = _fonts_mod.FONTS["stamp"].render("OFFICIAL", True, (170, 50, 50))
        st.set_alpha(55)
        rot = pygame.transform.rotate(st, -18)
        surf.blit(rot, rot.get_rect(center=(bx + bw * 3 // 4, by + bh - 90)))