"""Leaf clearance Reel: leaves cover the lawn, a gust sweeps them away, service cards, end card."""
import sys, math, random
sys.path.insert(0, "/tmp/claude-0/-home-user-New-Bloom-Gardens/50fca177-b464-52b5-8e0a-10c4356f2d3e/scratchpad")
from reels import W, H, F, CRIMSON, GREEN, SAGE, INK, LOGO, OUT, render, load, frame_kenburns, shade, text_center, end_card
from PIL import Image, ImageDraw, ImageFilter

S = "/tmp/claude-0/-home-user-New-Bloom-Gardens/50fca177-b464-52b5-8e0a-10c4356f2d3e/scratchpad"
ease = lambda t: 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))
ease_out = lambda t: 1 - (1 - max(0, min(1, t))) ** 3

LAWN = load(S + "/new/2a527dad.jpg")
random.seed(5)

# Leaf sprites: a few shapes x autumn colours, pre-rotated
COLS = [(196, 84, 30), (222, 132, 36), (181, 52, 38), (232, 170, 50), (150, 70, 35), (205, 105, 40)]
def leaf_sprite(col, kind, size=90):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = size / 2
    if kind == 0:   # oval leaf with a point
        pts = [(c + math.cos(a) * size * 0.22 * (1 + 0.9 * max(0, math.sin(a)) ** 6), c + math.sin(a) * size * 0.42) for a in [i * math.pi / 20 for i in range(40)]]
    else:           # lobed (maple-ish) leaf
        pts = []
        for i in range(60):
            a = i * 2 * math.pi / 60
            r = size * (0.26 + 0.16 * abs(math.sin(a * 2.5)) ** 0.7)
            pts.append((c + math.cos(a - math.pi / 2) * r, c + math.sin(a - math.pi / 2) * r))
    d.polygon(pts, fill=col + (255,))
    dark = tuple(max(0, v - 55) for v in col)
    d.line([(c, c - size * 0.38), (c, c + size * 0.45)], fill=dark + (255,), width=3)
    if kind == 1:
        for a in (-0.9, 0.9): d.line([(c, c + 4), (c + math.sin(a) * size * 0.3, c - math.cos(a) * size * 0.25)], fill=dark + (255,), width=2)
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0)); shadow.putalpha(im.getchannel("A").point(lambda v: int(v * 0.35)))
    out = Image.new("RGBA", (size + 8, size + 8), (0, 0, 0, 0)); out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(3)), (6, 7)); out.alpha_composite(im, (2, 2))
    return out
ANGLES = 24
SPRITES = [[leaf_sprite(c, k).rotate(a * 360 / ANGLES, resample=Image.BICUBIC, expand=False) for a in range(ANGLES)] for c in COLS for k in (0, 1)]
_scaled = {}
def sprite(i, rot, scale):
    a = int(rot / 360 * ANGLES) % ANGLES; s = max(14, int(98 * scale))
    key = (i, a, s)
    if key not in _scaled: _scaled[key] = SPRITES[i][a].resize((s, s), Image.BICUBIC)
    return _scaled[key]

# Ground leaves covering the lawn (perspective: smaller further back)
GROUND = []
for _ in range(900):
    y = random.uniform(820, H + 30); depth = (y - 800) / (H - 800)
    GROUND.append(dict(x=random.uniform(-40, W + 40), y=y, sc=0.35 + 0.75 * depth, rot=random.uniform(0, 360),
                       spr=random.randrange(len(SPRITES)), delay=random.uniform(0, 0.55) + (1 - depth) * 0.15,
                       lift=random.uniform(60, 260), spin=random.uniform(-900, 900)))
GROUND.sort(key=lambda g: g["y"])
FALLING = [dict(x=random.uniform(0, W), y=random.uniform(-H, H), sc=random.uniform(0.5, 1.0), v=random.uniform(170, 300),
                sw=random.uniform(30, 80), ph=random.uniform(0, 6.28), spin=random.uniform(-120, 120), spr=random.randrange(len(SPRITES)))
           for _ in range(28)]

GUST_T, GUST_LEN = 3.0, 1.6
def draw_ground(fr, t):
    for g in GROUND:
        p = (t - GUST_T - g["delay"]) / GUST_LEN
        if p <= 0:
            x, y, rot = g["x"], g["y"], g["rot"]
        else:
            if p >= 1.4: continue
            x = g["x"] + (p ** 2) * 2600; y = g["y"] - math.sin(min(p, 1) * math.pi * 0.8) * g["lift"]; rot = g["rot"] + g["spin"] * p
            if x > W + 80: continue
        sp = sprite(g["spr"], rot, g["sc"]); fr.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
def draw_falling(fr, t, density=1.0, wind=0.0):
    for i, f in enumerate(FALLING):
        if i >= len(FALLING) * density: break
        y = (f["y"] + f["v"] * t) % (H + 200) - 100
        x = (f["x"] + f["sw"] * math.sin(f["ph"] + t * 1.6) + wind) % (W + 200) - 100
        sp = sprite(f["spr"], f["spin"] * t + f["ph"] * 50, f["sc"]); fr.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
def gust_wind(t): return 1800 * ease((t - GUST_T) / (GUST_LEN + 0.6))

def headline(fr, txt, alpha, y=300, size=78):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    text_center(d, y, txt, F(700, size))
    if alpha < 1: L.putalpha(L.getchannel("A").point(lambda v: int(v * alpha)))
    fr.alpha_composite(L)

def card(fr, title, sub, a_in, a_out):
    if a_in <= 0 or a_out >= 1: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    x0, y0, x1, y1 = 80, 1260, W - 80, 1560
    d.rounded_rectangle([x0, y0, x1, y1], 40, fill=(255, 255, 255, 238))
    d.rounded_rectangle([x0, y0, x0 + 18, y1], 9, fill=CRIMSON)
    text_center(d, y0 + 60, title, F(700, 62), fill=CRIMSON, shadow=False, maxw=820)
    text_center(d, y0 + 175, sub, F(400, 40), fill=(70, 84, 64), shadow=False, maxw=820)
    alpha = min(1, a_in) * (1 - a_out); dx = int(W * (1 - ease_out(a_in)) - W * ease(a_out))
    if alpha < 1: L.putalpha(L.getchannel("A").point(lambda v: int(v * alpha)))
    M = Image.new("RGBA", (W, H), (0, 0, 0, 0)); M.paste(L, (dx, 0)); fr.alpha_composite(M)

CARDS = [("Lawns, beds & borders", "Leaves raked and blown out of every corner"),
         ("Paths & patios", "No more slippery leaf mush underfoot"),
         ("All taken away", "Bagged and removed from site, nothing left behind")]
END = end_card(["Leaf clearance", "Free quotes across Chelmsford"])

T_CARDS = 5.2; EACH = 1.9; T_END = T_CARDS + EACH * len(CARDS); DUR = T_END + 3.2
def frame(t):
    fr = frame_kenburns(LAWN, t / DUR, 1.12, 1.0, 0.5, 0.5, 0.55, 0.5).convert("RGBA")
    fr = shade(fr, top=True, bottom=False)
    draw_ground(fr, t)
    draw_falling(fr, t, 1.0 if t < T_CARDS else 0.35, gust_wind(t))
    if t < GUST_T + 0.4: headline(fr, "Leaves piling up?", ease_out((t - 0.3) / 0.5) * (1 - ease((t - GUST_T) / 0.4)))
    if GUST_T + 0.9 < t < T_CARDS + 0.3: headline(fr, "We'll clear them.", ease_out((t - GUST_T - 0.9) / 0.5) * (1 - ease((t - T_CARDS) / 0.3)))
    if T_CARDS <= t < T_END:
        k = int((t - T_CARDS) / EACH); lt = t - T_CARDS - k * EACH
        headline(fr, "Leaf clearance", 1.0, y=300, size=84)
        card(fr, *CARDS[k], lt / 0.4, (lt - (EACH - 0.3)) / 0.3)
    if t >= T_END:
        a = ease((t - T_END) / 0.6)
        fr = Image.blend(fr, END.convert("RGBA"), a)
        draw_falling(fr, t, 0.3)
    return fr.convert("RGB")

render("14-leaf-clearance.mp4", [{"dur": DUR, "fn": lambda u: frame(u * DUR)}])
