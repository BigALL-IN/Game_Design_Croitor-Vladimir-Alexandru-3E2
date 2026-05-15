import array
import math

import pygame

SOUNDS: dict = {}
_initialized = False

SAMPLE_RATE = 44100


def _mkbuf(samples: list[int]) -> bytes:
    return array.array("h", samples).tobytes()


def _sine(freq: float, duration: float, volume: float = 0.3,
          fade_out: float = 0.0) -> list[int]:
    n = int(SAMPLE_RATE * duration)
    fade_n = int(SAMPLE_RATE * fade_out) if fade_out else 0
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = volume
        if fade_n and i > n - fade_n:
            env *= (n - i) / fade_n
        if i < 80:
            env *= i / 80
        val = int(env * 32767 * math.sin(2 * math.pi * freq * t))
        out.append(max(-32767, min(32767, val)))
    return out


def _square(freq: float, duration: float, volume: float = 0.15,
            fade_out: float = 0.0) -> list[int]:
    n = int(SAMPLE_RATE * duration)
    fade_n = int(SAMPLE_RATE * fade_out) if fade_out else 0
    period = SAMPLE_RATE / freq if freq else n
    out = []
    for i in range(n):
        env = volume
        if fade_n and i > n - fade_n:
            env *= (n - i) / fade_n
        if i < 80:
            env *= i / 80
        val = int(env * 32767 * (1 if (i % int(period)) < int(period / 2) else -1))
        out.append(max(-32767, min(32767, val)))
    return out


def _noise(duration: float, volume: float = 0.1) -> list[int]:
    import random
    n = int(SAMPLE_RATE * duration)
    out = []
    for i in range(n):
        env = volume
        if i < 60:
            env *= i / 60
        if i > n - 200:
            env *= (n - i) / 200
        val = int(env * 32767 * (random.random() * 2 - 1))
        out.append(max(-32767, min(32767, val)))
    return out


def _mix(buffers: list[list[int]]) -> list[int]:
    length = max(len(b) for b in buffers)
    out = [0] * length
    for b in buffers:
        for i, v in enumerate(b):
            out[i] = max(-32767, min(32767, out[i] + v))
    return out


def _pad(samples: list[int], total_samples: int) -> list[int]:
    if len(samples) >= total_samples:
        return samples[:total_samples]
    return samples + [0] * (total_samples - len(samples))


def _make_stamp() -> pygame.mixer.Sound:
    thud = _sine(80, 0.08, volume=0.5, fade_out=0.06)
    click = _noise(0.03, volume=0.25)
    click = _pad(click, len(thud))
    return pygame.mixer.Sound(buffer=_mkbuf(_mix([thud, click])))


def _make_paper() -> pygame.mixer.Sound:
    s1 = _noise(0.12, volume=0.08)
    s2 = _noise(0.08, volume=0.05)
    gap = [0] * int(SAMPLE_RATE * 0.05)
    return pygame.mixer.Sound(buffer=_mkbuf(s1 + gap + s2))


def _make_correct() -> pygame.mixer.Sound:
    t1 = _sine(520, 0.1, volume=0.2, fade_out=0.04)
    t2 = _sine(700, 0.15, volume=0.2, fade_out=0.08)
    gap = [0] * int(SAMPLE_RATE * 0.03)
    return pygame.mixer.Sound(buffer=_mkbuf(t1 + gap + t2))


def _make_wrong() -> pygame.mixer.Sound:
    t1 = _sine(250, 0.15, volume=0.25, fade_out=0.05)
    t2 = _sine(180, 0.25, volume=0.25, fade_out=0.15)
    return pygame.mixer.Sound(buffer=_mkbuf(t1 + t2))


def _make_detain() -> pygame.mixer.Sound:
    t1 = _square(200, 0.1, volume=0.2)
    t2 = _square(150, 0.1, volume=0.2)
    t3 = _square(200, 0.1, volume=0.2)
    gap = [0] * int(SAMPLE_RATE * 0.04)
    return pygame.mixer.Sound(buffer=_mkbuf(t1 + gap + t2 + gap + t3))


def _make_tick() -> pygame.mixer.Sound:
    return pygame.mixer.Sound(buffer=_mkbuf(_sine(900, 0.03, volume=0.1)))


def _make_click() -> pygame.mixer.Sound:
    return pygame.mixer.Sound(buffer=_mkbuf(
        _sine(600, 0.04, volume=0.15, fade_out=0.03)))


def _make_day_end() -> pygame.mixer.Sound:
    t1 = _sine(400, 0.2, volume=0.2, fade_out=0.1)
    t2 = _sine(350, 0.2, volume=0.2, fade_out=0.1)
    t3 = _sine(300, 0.4, volume=0.25, fade_out=0.3)
    gap = [0] * int(SAMPLE_RATE * 0.05)
    return pygame.mixer.Sound(buffer=_mkbuf(t1 + gap + t2 + gap + t3))



def init_sounds():
    global SOUNDS, _initialized
    try:
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=1024)
    except Exception:
        return

    SOUNDS["stamp"] = _make_stamp()
    SOUNDS["paper"] = _make_paper()
    SOUNDS["correct"] = _make_correct()
    SOUNDS["wrong"] = _make_wrong()
    SOUNDS["detain"] = _make_detain()
    SOUNDS["tick"] = _make_tick()
    SOUNDS["click"] = _make_click()
    SOUNDS["day_end"] = _make_day_end()
    _initialized = True


def play(name: str):
    if not _initialized:
        return
    snd = SOUNDS.get(name)
    if snd:
        snd.play()


