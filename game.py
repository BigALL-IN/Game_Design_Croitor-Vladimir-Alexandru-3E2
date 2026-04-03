from __future__ import annotations

import random
import sys
from typing import Optional

import pygame

from core.constants import (
    C, W, H, FPS, NATIONS,
    DAY_TIMER_SECONDS, CORRECT_REWARD, FAMILY_HP_MAX, get_penalty,
)
from core.fonts import init_fonts
import core.fonts as _fonts_mod
from core.assets import init_assets, ASSETS
from core.draw_utils import text
from core.person import make_person

from documents.base import DocumentWidget
from documents.passport import PassportTemplate, DOC_W
from documents.id_card import IDCardTemplate, ID_DOC_W

from ui.investigation import InvestigationController
from ui.traveler_panel import (
    NPC_PANEL_RECT, make_traveler_fields, draw_traveler_panel,
)
from ui.rulebook import RuleBook

from screens.family_screen import FamilyScreen, MEMBERS


class Game:
    def __init__(self, carry_family_hp: Optional[dict] = None):
        pygame.init()
        pygame.font.init()
        init_fonts()
        init_assets()

        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("PAPERS, PLEASE  —  Arstotzka Border Control")
        self.clock = pygame.time.Clock()

        self.time_left = DAY_TIMER_SECONDS * FPS
        self.timer_paused = False

        self.credits = 0
        self.mistakes = 0
        self.processed = 0
        self.day = 1

        self.family_hp: dict = (
            dict(carry_family_hp)
            if carry_family_hp is not None
            else {m: FAMILY_HP_MAX for m in MEMBERS}
        )

        self.allowed_nations = self._roll_nations()

        self.queue: list = []
        self.person_idx: int = 0
        self._generate_queue(20)

        self.state = "playing"

        self.last_result = ""
        self.result_msg = ""
        self.result_flash_timer = 0
        self.penalty_msg = ""

        self.rulebook = RuleBook()
        self.inv = InvestigationController()
        self.family_screen: Optional[FamilyScreen] = None

        self._load_person()


    def _roll_nations(self) -> list:
        nations = random.sample(NATIONS, k=3)
        if "Arstotzka" not in nations:
            nations[0] = "Arstotzka"
        return nations

    def _generate_queue(self, n: int):
        for _ in range(n):
            self.queue.append(make_person(set(self.allowed_nations)))

    def _load_person(self):
        if self.person_idx >= len(self.queue):
            self._generate_queue(10)
        self.current = self.queue[self.person_idx]

        tray_x, tray_y = 30, H - 215

        self.docs = self._build_documents(self.current, tray_x, tray_y)
        self.traveler_fields = make_traveler_fields(self.current, NPC_PANEL_RECT)
        self.inv.exit()

    def _build_documents(self, person, tray_x: int, tray_y: int) -> list:

        gap = 20
        passport = DocumentWidget(PassportTemplate(), person, (tray_x, tray_y))
        id_card  = DocumentWidget(IDCardTemplate(),   person, (tray_x + DOC_W + gap, tray_y))

        return [id_card, passport]

    def _all_doc_fields(self) -> list:
        return [f for doc in self.docs for f in doc.fields]

    def _verdict(self, approve: bool):
        if self.state != "playing":
            return
        self.inv.exit()
        correct = approve == self.current.should_approve

        if correct:
            self.credits           += CORRECT_REWARD
            self.last_result        = "correct"
            self.result_msg         = f"CORRECT  +{CORRECT_REWARD} credits"
            self.penalty_msg        = ""
        else:
            penalty        = get_penalty(self.mistakes)
            self.mistakes += 1
            self.credits   = max(0, self.credits - penalty)
            self.last_result = "wrong"
            if penalty == 0:
                self.result_msg  = f"WRONG  —  WARNING  (mistake #{self.mistakes})"
                self.penalty_msg = (f"WARNING #{self.mistakes}  —  "
                                    f"{self.current.flaw or 'Wrong decision'}")
            else:
                self.result_msg  = (f"WRONG  —  -{penalty} CREDITS  "
                                    f"(mistake #{self.mistakes})")
                self.penalty_msg = (f"-{penalty} credits  —  "
                                    f"{self.current.flaw or 'Wrong decision'}")

        stamp = "APPROVED" if approve else "DENIED"
        for doc in self.docs:
            doc.set_stamp(stamp)

        self.result_flash_timer = 90
        self._next_person()

    def _next_person(self):
        self.person_idx += 1
        self.processed  += 1
        self._load_person()

    def _trigger_day_end(self):
        self.state         = "day_end"
        self.timer_paused  = True
        self.family_screen = FamilyScreen(self.credits, self.family_hp)

    def _finish_day(self):
        fs = self.family_screen
        self.family_hp = dict(fs.result_hp)
        self.credits   = fs.credits

        if all(hp <= 0 for hp in self.family_hp.values()):
            self.state = "gameover"
            return

        self.day          += 1
        self.mistakes      = 0
        self.time_left     = DAY_TIMER_SECONDS * FPS
        self.timer_paused  = False
        self.state         = "playing"
        self.credits       = 0
        self.processed     = 0

        self.allowed_nations = self._roll_nations()
        self.queue           = []
        self._generate_queue(20)
        self.person_idx      = 0
        self._load_person()
        self.family_screen   = None

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_event(event)
            self._update()
            self._draw()
            pygame.display.flip()

    def _update(self):
        if self.state != "playing":
            return
        if not self.timer_paused:
            self.time_left -= 1
            if self.time_left <= 0:
                self.time_left = 0
                self._trigger_day_end()
                return
        for doc in self.docs:
            doc.update_rects()
        if self.inv.active:
            self.inv.refresh(self._all_doc_fields())
        if self.result_flash_timer > 0:
            self.result_flash_timer -= 1

    def _handle_event(self, event: pygame.event.Event):
        if self.state == "day_end":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.family_screen and self.family_screen.confirmed:
                    self._finish_day()
                    return
                elif self.family_screen:
                    self.family_screen.confirm()
                    return
            if self.family_screen:
                self.family_screen.handle_event(event)
            return

        if self.state in ("gameover", "victory"):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__()
            return

        self.rulebook.handle_event(event)
        if self.rulebook.open:
            return

        if self.state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self._verdict(True)
                elif event.key == pygame.K_d:
                    self._verdict(False)
                elif event.key == pygame.K_SPACE:
                    if self.inv.active:
                        self.inv.exit()
                    else:
                        self.inv.enter(
                            self.current, set(self.allowed_nations),
                            self._all_doc_fields(), self.traveler_fields,
                        )

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.inv.active and self.inv.try_click(event.pos):
                    return
                ar, dr = self._button_rects()
                if ar.collidepoint(event.pos):
                    self._verdict(True);  return
                if dr.collidepoint(event.pos):
                    self._verdict(False); return
                if not self.inv.active:
                    for doc in reversed(self.docs):
                        doc.handle_event(event)

            elif event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if not self.inv.active:
                    for doc in self.docs:
                        doc.handle_event(event)


    def _button_rects(self):
        bw, bh = 160, 50
        bx = (W - bw * 2 - 20) // 2
        return (pygame.Rect(bx,          H - 70, bw, bh),
                pygame.Rect(bx + bw + 20, H - 70, bw, bh))

    def _draw(self):
        s = self.screen
        s.fill(C["bg"])

        if self.state == "day_end" and self.family_screen:
            self.family_screen.draw(s)
            pygame.display.flip()
            return

        if self.state == "gameover":
            self._draw_endscreen(victory=False); return
        if self.state == "victory":
            self._draw_endscreen(victory=True);  return

        self._draw_background(s)
        self._draw_npc_panel(s)
        self._draw_desk(s)
        self._draw_docs(s)
        self._draw_buttons(s)
        self._draw_hud(s)
        self._draw_timer(s)
        self._draw_family_hud(s)
        self.rulebook.draw_closed(s)
        self.inv.draw_result_banner(s)

        if self.result_flash_timer > 0:
            self._draw_result_flash(s)
        self.rulebook.draw_overlay(s, self.allowed_nations)

    def _draw_background(self, s):
        pygame.draw.rect(s, (35, 38, 30), (0, 0, W, 400))
        for y in range(40, 400, 80):
            pygame.draw.line(s, (30, 33, 25), (0, y), (W, y), 1)
        pygame.draw.rect(s, C["desk"],   (0, 400, W, H - 400))
        pygame.draw.rect(s, C["border"], (0, 400, W, 3))

    def _draw_npc_panel(self, s):
        draw_traveler_panel(
            s, self.current,
            self.inv.active, self.inv.selected,
            self.traveler_fields,
        )

    def _draw_desk(self, s):
        pygame.draw.rect(s, (62, 57, 44), (0, 420, W, H - 420))

    def _draw_docs(self, s):
        sel = self.inv.selected if self.inv.active else []
        for doc in self.docs:
            doc.draw(s, self.inv.active, sel)

    def _draw_buttons(self, s):
        ar, dr = self._button_rects()
        pygame.draw.rect(s, C["stamp_appr"], ar, border_radius=6)
        pygame.draw.rect(s, C["green"],      ar, 2, border_radius=6)
        text(s, "APPROVE  [A]", "title", C["cream"], ar.centerx, ar.centery - 9, center=True)
        pygame.draw.rect(s, C["stamp_deny"], dr, border_radius=6)
        pygame.draw.rect(s, C["red"],        dr, 2, border_radius=6)
        text(s, "DENY  [D]",    "title", C["cream"], dr.centerx, dr.centery - 9, center=True)

    def _draw_hud(self, s):
        pygame.draw.rect(s, (20, 22, 17), (0, 0, W, 18))
        items = [
            (f"DAY: {self.day}",           C["gold"]),
            (f"PROCESSED: {self.processed}", C["gold"]),
            (f"CREDITS: {self.credits}",   C["gold"]),
            (f"MISTAKES: {self.mistakes}", C["red"] if self.mistakes > 0 else C["gold"]),
        ]
        for i, (item, col) in enumerate(items):
            text(s, item, "small", col, 20 + i * 220, 3)

    def _draw_timer(self, s):
        secs_left = max(0, self.time_left // FPS)
        frac      = max(0.0, self.time_left / (DAY_TIMER_SECONDS * FPS))

        bar_x, bar_y = W - 340, 20
        bar_w, bar_h = 290, 20
        pygame.draw.rect(s, (30, 30, 25), (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        bar_col = (C["timer_ok"] if frac > 0.5
                   else C["timer_warn"] if frac > 0.2
                   else C["timer_crit"])
        fill_w = int(bar_w * frac)
        if fill_w > 0:
            pygame.draw.rect(s, bar_col, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(s, C["border"], (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
        text(s, f"SHIFT ENDS IN: {secs_left:02d}s", "small", bar_col,
             bar_x + bar_w // 2, bar_y + 3, center=True)

    def _draw_family_hud(self, s):
        fx, fy = W - 335, H - 68
        pygame.draw.rect(s, (25, 20, 20), (fx - 4, fy - 4, 330, 58), border_radius=4)
        pygame.draw.rect(s, (70, 45, 45), (fx - 4, fy - 4, 330, 58), 1, border_radius=4)
        text(s, "FAMILY:", "small", C["text_dim"], fx, fy + 2)
        for i, m in enumerate(MEMBERS):
            hp  = self.family_hp[m]
            mx  = fx + 75 + i * 100
            col = (C["family_ok"] if hp == FAMILY_HP_MAX
                   else C["timer_warn"] if hp > 0
                   else (80, 30, 30))
            text(s, m[:3].upper(), "small", col, mx, fy + 2, center=True)
            for h in range(FAMILY_HP_MAX):
                hx = mx - (FAMILY_HP_MAX * 9) // 2 + h * 18
                pygame.draw.circle(
                    s,
                    C["family_hp"] if h < hp else (55, 35, 35),
                    (hx + 4, fy + 26), 6,
                )

    def _draw_result_flash(self, s):
        alpha   = min(255, self.result_flash_timer * 6)
        correct = self.last_result == "correct"
        ov = pygame.Surface((W, 60), pygame.SRCALPHA)
        ov.fill((40, 120, 60, 60) if correct else (120, 30, 30, 60))
        s.blit(ov, (0, 395))
        col = C["green"] if correct else C["red"]
        msg = _fonts_mod.FONTS["title"].render(self.result_msg, True, col)
        msg.set_alpha(alpha)
        s.blit(msg, msg.get_rect(centerx=W // 2, centery=420))
        if self.penalty_msg:
            pm = _fonts_mod.FONTS["small"].render(self.penalty_msg, True, C["text_light"])
            pm.set_alpha(alpha)
            s.blit(pm, pm.get_rect(centerx=W // 2, centery=438))

    def _draw_endscreen(self, victory: bool):
        s = self.screen
        s.fill(C["win"] if victory else C["lose"])
        for y in range(0, H, 4):
            pygame.draw.line(s, (0, 0, 0), (0, y), (W, y), 1)
        tc = (200, 240, 200) if victory else (240, 200, 200)

        if not victory:
            dead = [m for m, hp in self.family_hp.items() if hp <= 0]
            text(s, "TRAGEDY", "big", tc, W // 2, 160, center=True)
            if dead:
                text(s, f"Your family perished. {', '.join(d.upper() for d in dead)} died.",
                     "mono", C["cream"], W // 2, 210, center=True)
            else:
                text(s, "The shift ended in failure.", "mono", C["cream"], W // 2, 210, center=True)
        else:
            text(s, "SHIFT COMPLETE", "big",  tc,         W // 2, 160, center=True)
            text(s, "Congratulations, Comrade.", "mono", C["cream"], W // 2, 210, center=True)

        stats = [
            f"Days Served       : {self.day}",
            f"Persons Processed : {self.processed}",
            f"Final Credits     : {self.credits}",
            f"Total Mistakes    : {self.mistakes}",
        ]
        for i, line in enumerate(stats):
            text(s, line, "title", C["cream"], W // 2, 290 + i * 36, center=True)

        text(s, "FAMILY STATUS:", "title", C["gold"], W // 2, 450, center=True)
        for i, m in enumerate(MEMBERS):
            hp   = self.family_hp[m]
            col  = C["family_ok"] if hp > 0 else C["family_hp"]
            stat = f"HP {hp}/{FAMILY_HP_MAX}" if hp > 0 else "† DECEASED"
            text(s, f"{m.upper():12s}  {stat}", "mono", col, W // 2, 476 + i * 24, center=True)

        text(s, "Press R to restart", "mono", C["text_dim"], W // 2, H - 80, center=True)
        text(s, "GLORY TO ARSTOTZKA", "big",  (200, 170, 80), W // 2, H - 50, center=True)