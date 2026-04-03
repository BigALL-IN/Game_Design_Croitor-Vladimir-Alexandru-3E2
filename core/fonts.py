import pygame

def _make(name: str, size: int, bold: bool = False):
    try:
        return pygame.font.SysFont(name, size, bold=bold)
    except Exception:
        return pygame.font.SysFont(name, size, bold=bold)


FONTS: dict = {}


def init_fonts():
    global FONTS
    FONTS = {
        "mono":    _make("couriernew", 14),
        "title":   _make("couriernew", 18, bold=True),
        "big":     _make("couriernew", 28, bold=True),
        "stamp":   _make("couriernew", 36, bold=True),
        "small":   _make("couriernew", 12),
        "book":    _make("couriernew", 13),
        "book_t":  _make("couriernew", 16, bold=True),
        "huge":    _make("couriernew", 48, bold=True),
        "med":     _make("couriernew", 22, bold=True),
    }
    return FONTS