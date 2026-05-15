import pygame

from core.constants import C, W, H, CURRENT_YEAR, get_required_docs
from core.draw_utils import text
from core import sounds as sfx

_DOC_NAMES = {
    "passport": "Passport",
    "id": "Citizen ID Card",
    "work_permit": "Work Permit",
    "entry_permit": "Entry Permit",
}


class BriefingScreen:

    def __init__(self, day: int, allowed_nations: list,
                 prev_docs: list | None = None,
                 prev_nations: list | None = None):
        self.day = day
        self.allowed_nations = allowed_nations
        self.required_docs = get_required_docs(day)
        self.prev_docs = prev_docs or []
        self.prev_nations = prev_nations or []
        self.new_docs = [d for d in self.required_docs if d not in self.prev_docs]
        self.added_nations = [n for n in allowed_nations if n not in self.prev_nations]
        self.removed_nations = [n for n in self.prev_nations if n not in allowed_nations]
        self.is_first_day = (day == 1)
        self.confirmed = False
        self.btn_rect = pygame.Rect(W // 2 - 170, H - 100, 340, 55)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            sfx.play("click")
            self.confirmed = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_rect.collidepoint(event.pos):
                sfx.play("click")
                self.confirmed = True

    def draw(self, surf: pygame.Surface):
        surf.fill((15, 18, 28))
        for y in range(0, H, 6):
            pygame.draw.line(surf, (20, 23, 35), (0, y), (W, y), 1)

        text(surf, f"DAY {self.day} BRIEFING", "huge", C["gold"],
             W // 2, 40, center=True)
        text(surf, f"Date: {12 + self.day - 1}.11.{CURRENT_YEAR}", "mono", C["text_dim"],
             W // 2, 100, center=True)

        pygame.draw.line(surf, C["border"], (200, 125), (W - 200, 125), 1)

        if self.is_first_day:
            self._draw_first_day(surf)
        else:
            self._draw_changes(surf)

        br = self.btn_rect
        pygame.draw.rect(surf, (30, 100, 55), br, border_radius=8)
        pygame.draw.rect(surf, C["green"], br, 2, border_radius=8)
        text(surf, "BEGIN DAY  [ENTER]", "big", C["cream"],
             br.centerx, br.centery - 10, center=True)

        text(surf, "Glory to Arstotzka.", "mono", C["text_dim"],
             W // 2, H - 30, center=True)

    def _draw_first_day(self, surf):
        y = 145
        text(surf, "Welcome to Arstotzka Border Control.", "mono",
             C["cream"], W // 2, y, center=True)
        y += 30

        text(surf, "PERMITTED NATIONS:", "title", C["cream"], W // 2, y, center=True)
        y += 26
        for nation in self.allowed_nations:
            text(surf, f"  +  {nation}", "mono", C["green"], W // 2, y, center=True)
            y += 22

        y += 16
        text(surf, "REQUIRED DOCUMENTS:", "title", C["cream"], W // 2, y, center=True)
        y += 26
        for doc_id in self.required_docs:
            name = _DOC_NAMES.get(doc_id, doc_id)
            text(surf, f"  {name}", "mono", C["text_light"], W // 2, y, center=True)
            y += 22

        y += 16
        text(surf, "CONTROLS:", "title", C["cream"], W // 2, y, center=True)
        y += 26
        controls = [
            "[A] Approve    [D] Deny    [F] Detain",
            "[SPACE] Investigate    [Q] Interrogate",
            "Click RULEBOOK for full regulations",
        ]
        for line in controls:
            text(surf, line, "mono", C["text_dim"], W // 2, y, center=True)
            y += 20

    def _draw_changes(self, surf):
        y = 145
        has_changes = (self.new_docs or self.added_nations or self.removed_nations)

        if not has_changes:
            text(surf, "No regulation changes today.", "mono",
                 C["text_light"], W // 2, y, center=True)
            y += 36
        else:
            text(surf, "CHANGES FROM PREVIOUS DAY:", "title", (210, 60, 60),
                 W // 2, y, center=True)
            y += 30

            if self.added_nations:
                for nation in self.added_nations:
                    text(surf, f"  + {nation} NOW PERMITTED", "mono",
                         C["green"], W // 2, y, center=True)
                    y += 22
            if self.removed_nations:
                for nation in self.removed_nations:
                    text(surf, f"  - {nation} NO LONGER PERMITTED", "mono",
                         C["red"], W // 2, y, center=True)
                    y += 22
            if self.new_docs:
                for doc_id in self.new_docs:
                    name = _DOC_NAMES.get(doc_id, doc_id)
                    text(surf, f"  + NEW DOCUMENT REQUIRED: {name}", "mono",
                         C["gold"], W // 2, y, center=True)
                    y += 22
            y += 14

        text(surf, "TODAY'S PERMITTED NATIONS:", "title", C["cream"],
             W // 2, y, center=True)
        y += 26
        for nation in self.allowed_nations:
            text(surf, f"  +  {nation}", "mono", C["green"], W // 2, y, center=True)
            y += 22

        y += 14
        text(surf, "REQUIRED DOCUMENTS:", "title", C["cream"],
             W // 2, y, center=True)
        y += 26
        for doc_id in self.required_docs:
            name = _DOC_NAMES.get(doc_id, doc_id)
            is_new = doc_id in self.new_docs
            col = C["gold"] if is_new else C["text_light"]
            suffix = "  ** NEW **" if is_new else ""
            text(surf, f"  {name}{suffix}", "mono", col, W // 2, y, center=True)
            y += 22
