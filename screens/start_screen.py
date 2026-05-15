import math

import pygame

from core.constants import C, W, H
from core.draw_utils import text
from core import sounds as sfx
import core.fonts as _fonts_mod


class StartScreen:

    def __init__(self):
        self.started = False
        self.frame = 0

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            sfx.play("click")
            self.started = True

    def draw(self, surf: pygame.Surface):
        self.frame += 1

        surf.fill((18, 20, 15))
        for y in range(0, H, 4):
            pygame.draw.line(surf, (14, 16, 11), (0, y), (W, y), 1)

        pygame.draw.line(surf, C["border"], (100, 180), (W - 100, 180), 2)
        pygame.draw.line(surf, C["border"], (100, 420), (W - 100, 420), 2)

        text(surf, "MINISTRY OF ADMISSION", "title", C["text_dim"],
             W // 2, 200, center=True)
        text(surf, "ARSTOTZKA BORDER CONTROL", "mono", C["text_dim"],
             W // 2, 230, center=True)

        text(surf, "PAPERS, THANKS", "huge", C["gold"],
             W // 2, 300, center=True)

        alpha = int(128 + 127 * math.sin(self.frame * 0.05))
        font = _fonts_mod.FONTS["title"]
        prompt = font.render("PRESS ENTER TO BEGIN", True, C["cream"])
        prompt.set_alpha(alpha)
        surf.blit(prompt, prompt.get_rect(centerx=W // 2, centery=500))

        text(surf, "Approve. Deny. Detain.", "mono", C["text_dim"],
             W // 2, 560, center=True)

        text(surf, "GLORY TO ARSTOTZKA", "big", (200, 170, 80),
             W // 2, H - 50, center=True)
