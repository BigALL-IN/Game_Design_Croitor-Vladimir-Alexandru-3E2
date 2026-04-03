from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
FACE_DIR   = SCRIPT_DIR / "NPC_Faces"
DOC_DIR    = SCRIPT_DIR / "NPC_Documents"

W, H = 1200, 800
FPS  = 60

DAY_TIMER_SECONDS = 60
CORRECT_REWARD    = 10

PENALTY_SCHEDULE  = [0, 0, 5, 10, 15, 20, 25, 30]

FAMILY_FEED_COST = {"wife": 10, "daughter": 8, "son": 8}
FAMILY_HP_MAX    = 3

CURRENT_YEAR = 1982
NATIONS      = ["Arstotzka", "Kolechnia", "Impor", "Obristan", "Antegria", "Republia"]

C = {
    "bg":          (28,  30,  25),
    "desk":        (55,  50,  38),
    "border":      (90,  85,  65),
    "cream":       (230, 220, 190),
    "stamp_deny":  (180,  40,  40),
    "stamp_appr":  ( 40, 130,  60),
    "red":         (210,  60,  60),
    "green":       ( 70, 180,  90),
    "gold":        (200, 170,  80),
    "text_light":  (200, 195, 170),
    "text_dim":    (120, 115,  90),
    "npc_bg":      ( 70,  90,  70),
    "win":         ( 50, 150,  80),
    "lose":        (150,  50,  50),
    "book_bg":     ( 90,  55,  25),
    "book_page":   (235, 225, 195),
    "placeholder": ( 60,  70,  55),
    "inv_sel1":    (220, 180,  40),
    "inv_sel2":    ( 40, 180, 220),
    "inv_ok":      ( 50, 210,  90),
    "inv_bad":     (210,  55,  55),
    "inv_none":    (140, 130, 180),
    "inv_mode":    ( 30, 200, 100),
    "timer_ok":    ( 80, 200,  80),
    "timer_warn":  (220, 180,  30),
    "timer_crit":  (210,  55,  55),
    "family_hp":   (210,  55,  55),
    "family_ok":   ( 50, 200,  80),
}


def get_penalty(mistake_count: int) -> int:
    idx  = min(mistake_count, len(PENALTY_SCHEDULE) - 1)
    base = PENALTY_SCHEDULE[idx]
    if mistake_count >= len(PENALTY_SCHEDULE):
        extra = mistake_count - len(PENALTY_SCHEDULE) + 1
        base  = PENALTY_SCHEDULE[-1] + extra * 5
    return base