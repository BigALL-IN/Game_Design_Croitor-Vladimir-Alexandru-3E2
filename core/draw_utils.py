import pygame


def text(surf: pygame.Surface, msg: str, font_key: str, color, x: int, y: int, *, center: bool = False, right: bool = False) -> pygame.Rect:
    import core.fonts as _fonts_mod
    font = _fonts_mod.FONTS[font_key]
    s = font.render(str(msg), True, color)
    r = s.get_rect()
    if center:
        r.centerx = x
        r.top = y
    elif right:
        r.right = x
        r.top = y
    else:
        r.left = x
        r.top = y
    surf.blit(s, r)
    return r


def semi_rect(surf: pygame.Surface, color, rect, alpha: int = 200, border_radius: int = 0):
    ov = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    r, g, b = color[:3]
    ov.fill((r, g, b, alpha))
    surf.blit(ov, rect.topleft)
    if border_radius:
        pygame.draw.rect(surf, color, rect, 1, border_radius=border_radius)