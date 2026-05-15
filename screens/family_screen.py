import pygame

from core.constants import (
    C, W, H, FAMILY_FEED_COST, FAMILY_HP_MAX, CURRENT_YEAR,
)
from core.draw_utils import text
from core import sounds as sfx

MEMBERS = ["wife", "daughter", "son"]


class FamilyScreen:

    def __init__(self, credits: int, family_hp: dict):
        self.credits   = credits
        self.family_hp = dict(family_hp)
        self.fed       = {m: False for m in MEMBERS}
        self.confirmed = False
        self.result_hp: dict = {}
        self.spent     = 0
        self.btn_rects: dict = {m: None for m in MEMBERS}
        self.flash_msg   = ""
        self.flash_timer = 0
        self.death_msgs: list = []

    def get_total_cost(self) -> int:
        return sum(FAMILY_FEED_COST[m] for m in MEMBERS if self.fed[m])

    def handle_event(self, event: pygame.event.Event):
        if self.confirmed:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for m, r in self.btn_rects.items():
                if r and r.collidepoint(event.pos):
                    sfx.play("click")
                    self._toggle_feed(m)
            if self._confirm_rect().collidepoint(event.pos):
                sfx.play("click")
                self.confirm()

    def _toggle_feed(self, member: str):
        cost = FAMILY_FEED_COST[member]
        if self.fed[member]:
            self.fed[member] = False
            self.credits += cost
            self.flash_msg   = f"Cancelled feeding {member}  (+{cost} credits)"
            self.flash_timer = 120
        else:
            if self.credits >= cost:
                self.fed[member]  = True
                self.credits     -= cost
                self.flash_msg   = f"Fed {member}  (-{cost} credits)"
                self.flash_timer = 120
            else:
                self.flash_msg   = f"Not enough credits to feed {member}!"
                self.flash_timer = 120

    def confirm(self):
        self.confirmed = True
        self.result_hp  = dict(self.family_hp)
        self.death_msgs = []
        for m in MEMBERS:
            if not self.fed[m]:
                self.result_hp[m] = max(0, self.result_hp[m] - 1)
                if self.result_hp[m] == 0:
                    self.death_msgs.append(f"{m.upper()} HAS DIED OF STARVATION")

    def _confirm_rect(self) -> pygame.Rect:
        return pygame.Rect(W // 2 - 120, H - 100, 240, 50)

    def draw(self, surf: pygame.Surface):
        surf.fill((15, 18, 28))
        for y in range(0, H, 6):
            pygame.draw.line(surf, (20, 23, 35), (0, y), (W, y), 1)

        text(surf, "END OF SHIFT — EVENING", "big",   C["gold"],     W // 2, 30, center=True)
        text(surf, f"12.11.{CURRENT_YEAR}  |  Apartment Block 3  |  Grestin Border",
             "small", C["text_dim"], W // 2, 68, center=True)
        pygame.draw.line(surf, C["border"], (80, 82), (W - 80, 82), 1)

        credits_col = C["timer_ok"] if self.credits >= 10 else C["timer_crit"]
        text(surf, f"AVAILABLE CREDITS:  {self.credits}", "title", credits_col, W // 2, 96,  center=True)
        text(surf, "Feed your family before the night is over.", "mono", C["text_dim"], W // 2, 120, center=True)

        panel_w = 220
        total_w = panel_w * 3 + 40
        start_x = (W - total_w) // 2

        for i, m in enumerate(MEMBERS):
            px   = start_x + i * (panel_w + 20)
            py   = 148
            ph   = 360
            hp   = self.family_hp[m]
            alive = hp > 0
            fed   = self.fed[m]
            cost  = FAMILY_FEED_COST[m]

            bg_col     = (35, 50, 35) if fed else (45, 28, 28) if not alive else (30, 32, 45)
            border_col = C["family_ok"] if fed else C["family_hp"] if alive else (80, 30, 30)

            pygame.draw.rect(surf, bg_col,     (px, py, panel_w, ph), border_radius=8)
            pygame.draw.rect(surf, border_col, (px, py, panel_w, ph), 2, border_radius=8)

            name_col = (200, 200, 200) if alive else (100, 60, 60)
            text(surf, m.upper(), "title", name_col, px + panel_w // 2, py + 14, center=True)

            sil_r   = pygame.Rect(px + panel_w // 2 - 45, py + 38, 90, 100)
            sil_col = (50, 70, 50) if fed else (70, 40, 40) if alive else (40, 25, 25)
            pygame.draw.rect(surf, sil_col,    sil_r, border_radius=6)
            pygame.draw.rect(surf, border_col, sil_r, 1, border_radius=6)

            fc = (160, 140, 110) if alive else (80, 60, 60)
            pygame.draw.circle(surf, fc, (sil_r.centerx, sil_r.top + 28), 18)
            if alive:
                pygame.draw.circle(surf, (30, 25, 20), (sil_r.centerx - 7, sil_r.top + 24), 3)
                pygame.draw.circle(surf, (30, 25, 20), (sil_r.centerx + 7, sil_r.top + 24), 3)
                mouth = (140, 90, 60)
                if fed:
                    pygame.draw.arc(surf, mouth,
                                    pygame.Rect(sil_r.centerx - 8, sil_r.top + 30, 16, 10),
                                    3.14, 0, 2)
                else:
                    pygame.draw.arc(surf, mouth,
                                    pygame.Rect(sil_r.centerx - 8, sil_r.top + 35, 16, 10),
                                    0, 3.14, 2)
            else:
                for dx1, dy1, dx2, dy2 in [
                    (-10, 20, -4, 28), (-10, 28, -4, 20),
                    (4,   20, 10, 28), (4,   28, 10, 20),
                ]:
                    pygame.draw.line(surf, (150, 50, 50),
                                     (sil_r.centerx + dx1, sil_r.top + dy1),
                                     (sil_r.centerx + dx2, sil_r.top + dy2), 2)

            hp_y = py + 148
            text(surf, "HP:", "small", C["text_dim"], px + 14, hp_y)
            for h in range(FAMILY_HP_MAX):
                hx  = px + 48 + h * 26
                col = C["family_hp"] if h < hp else (60, 35, 35)
                pygame.draw.circle(surf, col, (hx + 5,  hp_y + 5), 5)
                pygame.draw.circle(surf, col, (hx + 13, hp_y + 5), 5)
                pts = [(hx, hp_y + 7), (hx + 9, hp_y + 18), (hx + 18, hp_y + 7)]
                pygame.draw.polygon(surf, col, pts)

            cost_col = (C["text_dim"] if not alive
                        else C["family_ok"] if fed else C["gold"])
            text(surf, f"Feed cost: {cost} cr", "small", cost_col,
                 px + panel_w // 2, py + 176, center=True)

            if not alive:
                status, st_col = "DECEASED", (150, 50, 50)
            elif fed:
                status, st_col = "FED", C["family_ok"]
            else:
                status, st_col = "HUNGRY", (200, 140, 40)
            text(surf, status, "title", st_col, px + panel_w // 2, py + 196, center=True)

            if alive:
                btn_r = pygame.Rect(px + 20, py + ph - 64, panel_w - 40, 40)
                self.btn_rects[m] = btn_r
                btn_col  = (30, 80, 40) if not fed else (80, 30, 30)
                btn_text = f"FEED ({cost}cr)" if not fed else "UNFEED (+refund)"
                pygame.draw.rect(surf, btn_col,    btn_r, border_radius=5)
                pygame.draw.rect(surf, border_col, btn_r, 1, border_radius=5)
                text(surf, btn_text, "small", C["cream"],
                     btn_r.centerx, btn_r.centery - 7, center=True)
            else:
                self.btn_rects[m] = None

        if self.flash_timer > 0:
            self.flash_timer -= 1
            alpha = min(255, self.flash_timer * 4)
            from core.fonts import FONTS
            fs = FONTS["mono"].render(self.flash_msg, True, C["gold"])
            fs.set_alpha(alpha)
            surf.blit(fs, fs.get_rect(centerx=W // 2, centery=H - 140))

        if not self.confirmed:
            cr = self._confirm_rect()
            pygame.draw.rect(surf, (30, 100, 55), cr, border_radius=6)
            pygame.draw.rect(surf, C["green"], cr, 2, border_radius=6)
            text(surf, "END OF DAY  [ENTER]", "title", C["cream"],
                 cr.centerx, cr.centery - 9, center=True)
        else:
            if self.death_msgs:
                dy = H - 130
                for msg in self.death_msgs:
                    text(surf, msg, "title", C["family_hp"], W // 2, dy, center=True)
                    dy += 26
                text(surf, "Press ENTER to continue...", "small", C["text_dim"],
                     W // 2, dy + 10, center=True)
            else:
                text(surf, "Family fed. Glory to Arstotzka.", "title", C["family_ok"],
                     W // 2, H - 110, center=True)
                text(surf, "Press ENTER to continue...", "small", C["text_dim"],
                     W // 2, H - 85, center=True)