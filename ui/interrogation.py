from __future__ import annotations

import random
from typing import Optional

import pygame

from core.constants import C, W, H
from core.draw_utils import text, semi_rect
from documents.base import ClickableField

_RESPONSES_INNOCENT = [
    "That is correct, yes.",
    "As you can see on the document.",
    "Everything is in order, officer.",
    "I have nothing to hide.",
    "Please, check it again if you must.",
    "All my papers are legitimate.",
]

_RESPONSES_BY_FLAW = {
    "expired": [
        "I... I thought it was still valid.",
        "Please, I did not notice the date.",
        "I will renew it, I swear.",
        "The office was closed when I tried to renew.",
    ],
    "wrong_nation": [
        "I have dual citizenship.",
        "That is... a complicated matter.",
        "I moved recently, the papers have not caught up.",
        "There must be an error in the system.",
    ],
    "name_mismatch": [
        "There must be a clerical error.",
        "I recently changed my name.",
        "The clerk spelled it wrong.",
        "It is a common mistake with our names.",
    ],
    "birth_mismatch": [
        "One of the documents has a typo.",
        "The old system used a different calendar.",
        "I have reported this error many times.",
    ],
    "photo_mismatch": [
        "I had surgery recently.",
        "That photo is old.",
        "The lighting was bad at the office.",
        "I have aged, that is all.",
    ],
    "wp_name_mismatch": [
        "My employer filed the paperwork wrong.",
        "There was a mistake at the labor office.",
        "I go by a different name at work.",
    ],
    "wp_expired": [
        "My employer was supposed to renew it.",
        "I was told it was still valid.",
        "The renewal office had a long queue.",
    ],
    "ep_nation_mismatch": [
        "I applied from a different country.",
        "My residency changed after I applied.",
        "The permit office made an error.",
    ],
    "ep_expired": [
        "I did not realize it had expired.",
        "I thought I had more time.",
        "The border was closed when I tried to enter.",
    ],
}

_FIELD_TO_FLAW_GROUP = {
    "expiry": ["expired", "wp_expired", "ep_expired"],
    "name":   ["name_mismatch", "wp_name_mismatch"],
    "nation": ["wrong_nation", "ep_nation_mismatch"],
    "photo":  ["photo_mismatch"],
    "birth":  ["birth_mismatch"],
}


def _generate_response(field: ClickableField, person) -> str:
    if not person.flaw:
        return random.choice(_RESPONSES_INNOCENT)

    for group_key, flaw_list in _FIELD_TO_FLAW_GROUP.items():
        if field.group == group_key:
            for flaw_id in flaw_list:
                if flaw_id in person.flaw.lower().replace(" ", "_"):
                    responses = _RESPONSES_BY_FLAW.get(flaw_id, _RESPONSES_INNOCENT)
                    return random.choice(responses)

    return random.choice(_RESPONSES_INNOCENT)


TRANSCRIPT_RECT = pygame.Rect(W - 340, 400, 320, 150)
MAX_LINES = 5


class InterrogationController:

    def __init__(self):
        self.active = False
        self.transcript: list[tuple[str, str]] = []
        self._person = None
        self._allowed: set = set()

    def enter(self, person, allowed_nations: set):
        self.active = True
        self._person = person
        self._allowed = allowed_nations
        self.transcript = []

    def exit(self):
        self.active = False

    def question_field(self, field: ClickableField):
        if not self._person:
            return
        q = f"Your {field.label} says '{field.value}'?"
        self.transcript.append(("YOU", q))
        response = _generate_response(field, self._person)
        self.transcript.append((self._person.first.upper(), response))

    def try_click(self, pos, all_fields: list) -> bool:
        if not self.active:
            return False
        for f in all_fields:
            if f.screen_rect and f.screen_rect.collidepoint(pos):
                self.question_field(f)
                return True
        return False

    def draw(self, surf: pygame.Surface):
        if not self.active:
            return

        r = TRANSCRIPT_RECT
        semi_rect(surf, (20, 22, 18), r, alpha=210, border_radius=6)
        pygame.draw.rect(surf, C["border"], r, 1, border_radius=6)

        text(surf, "INTERROGATION", "small", C["gold"], r.centerx, r.top + 4, center=True)

        visible = self.transcript[-(MAX_LINES):]
        y = r.top + 22
        for speaker, msg in visible:
            if speaker == "YOU":
                col = C["gold"]
            else:
                col = C["cream"]
            label = f"{speaker}: "
            text(surf, label, "small", col, r.left + 8, y)
            max_w = r.width - 16
            font_key = "small"
            import core.fonts as _fm
            font = _fm.FONTS[font_key]
            full = label + msg
            if font.size(full)[0] > max_w:
                msg = msg[:max_w // 7 - len(label)] + "..."
            text(surf, msg, font_key, C["text_light"], r.left + 8 + font.size(label)[0], y)
            y += 16

        hint_y = r.bottom + 4
        text(surf, "[Q] Exit | Click field to question", "small",
             C["inv_mode"], r.centerx, hint_y, center=True)
