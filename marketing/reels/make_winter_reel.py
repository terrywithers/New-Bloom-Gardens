"""Animated Winter offer Reel with falling snow (1080x1920)."""
import sys, math, random
sys.path.insert(0, "/tmp/claude-0/-home-user-New-Bloom-Gardens/50fca177-b464-52b5-8e0a-10c4356f2d3e/scratchpad")
from reels import W, H, FPS, F, CRIMSON, GREEN, LOGO, OUT, render
from PIL import Image, ImageDraw, ImageFilter

ease_out = lambda t: 1 - (1 - max(0, min(1, t))) ** 3
def back_out(t, s=1.4):
    t = max(0, min(1, t)) - 1
    return t * t * ((s + 1) * t + s) + 1

# Background: icy gradient with a soft snow drift at the bottom.
bg = Image.new("RGB", (W, H))
top, bot = (168, 196, 212), (238, 244, 247)
d = ImageDraw.Draw(bg)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * k) for i in range(3)))
drift = Image.new("RGBA", (W, H), (255, 255, 255, 0)); dd = ImageDraw.Draw(drift)
for x0, r in [(-100, 260), (220, 210), (520, 280), (820, 230), (1100, 260)]:
    dd.ellipse([x0 - r, H - 170 - r * 0.35, x0 + r, H - 170 + r * 1.6], fill=(255, 255, 255, 235))
drift = drift.filter(ImageFilter.GaussianBlur(14))
bg = Image.alpha_composite(bg.convert("RGBA"), drift)

def layer(draw_fn):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(L), L); return L

def centered(d, y, txt, font, fill, spacing=0):
    if spacing:
        widths = [d.textlength(c, font=font) for c in txt]; total = sum(widths) + spacing * (len(txt) - 1)
        x = (W - total) / 2
        for c, w in zip(txt, widths): d.text((x, y), c, font=font, fill=fill); x += w + spacing
    else:
        d.text(((W - d.textlength(txt, font=font)) / 2, y), txt, font=font, fill=fill)

# Content layers
def _logo(d, L):
    lg = LOGO.copy(); lg.thumbnail((430, 430)); L.paste(lg, ((W - lg.width) // 2, 190), lg)
LOGO_L = layer(_logo)
def _winter(d, L):
    f = F(700, 210); txt = "WINTER"; x = (W - d.textlength(txt, font=f)) / 2
    d.text((x + 7, 488 + 7), txt, font=f, fill=(255, 255, 255)); d.text((x, 488), txt, font=f, fill=CRIMSON)
WINTER_L = layer(_winter)
def _sub(d, L):
    centered(d, 760, "SEASONAL PROPERTY CARE", F(600, 46), GREEN, spacing=6)
    centered(d, 828, "Your outdoor space, our expert care", F(400, 44), CRIMSON)
SUB_L = layer(_sub)
ITEMS = [("Gutter clearing & fascia wash", "from £80"), ("Hedge cutting & reshaping", "free quote"),
         ("Leaf clearance & tidy-ups", "from £60"), ("Moss & driveway treatment", "free quote"),
         ("Commercial grounds & gritting", "contracts")]
PILL_Y0, PILL_H, PILL_GAP = 935, 96, 20
def pill_layer(i, name, price):
    def fn(d, L):
        y = PILL_Y0 + i * (PILL_H + PILL_GAP)
        d.rounded_rectangle([70, y, W - 70, y + PILL_H], radius=PILL_H // 2, fill=CRIMSON)
        fp = F(700, 40); pw = d.textlength(price, font=fp)
        size = 40
        while d.textlength(name, font=F(600, size)) > (W - 240 - pw - 40): size -= 1
        d.text((115, y + 48 - size * 0.62), name, font=F(600, size), fill=(255, 255, 255))
        d.text((W - 115 - pw, y + 22), price, font=fp, fill=(255, 214, 224))
    return layer(fn)
PILLS = [pill_layer(i, n, p) for i, (n, p) in enumerate(ITEMS)]
def _phone(d, L):
    centered(d, 1520, "07504 548304", F(700, 112), CRIMSON)
    centered(d, 1665, "CALL OR WHATSAPP  •  FULLY INSURED", F(600, 32), GREEN, spacing=3)
    centered(d, 1712, "Chelmsford & surrounding villages", F(400, 34), (70, 84, 64))
PHONE_L = layer(_phone)

# Snow: three depth layers. Far/mid behind the content, near (bigger, blurrier) in front.
random.seed(7)
def make_flakes(n, rmin, rmax, vmin, vmax, amin, amax):
    return [dict(x=random.uniform(0, W), y=random.uniform(-H, H), r=random.uniform(rmin, rmax), v=random.uniform(vmin, vmax),
                 sw=random.uniform(10, 40), ph=random.uniform(0, 6.28), f=random.uniform(0.3, 0.9), a=random.randint(amin, amax)) for _ in range(n)]
FAR, MID, NEAR = make_flakes(140, 2, 4, 60, 110, 150, 220), make_flakes(70, 4, 7, 120, 190, 200, 245), make_flakes(14, 9, 15, 230, 320, 170, 220)
def snow(flakes, t, blur=0):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for f in flakes:
        y = (f["y"] + f["v"] * t) % (H + 60) - 30
        x = f["x"] + f["sw"] * math.sin(f["ph"] + f["f"] * t * 2)
        d.ellipse([x - f["r"], y - f["r"], x + f["r"], y + f["r"]], fill=(255, 255, 255, f["a"]))
    return L.filter(ImageFilter.GaussianBlur(blur)) if blur else L

def place(base, L, alpha=1.0, dx=0, dy=0, scale=1.0):
    if alpha <= 0: return base
    if scale != 1.0:
        Ls = L.resize((int(W * scale), int(H * scale)), Image.BICUBIC)
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); L.paste(Ls, ((W - Ls.width) // 2, (H - Ls.height) // 2))
    if dx or dy:
        M = Image.new("RGBA", (W, H), (0, 0, 0, 0)); M.paste(L, (int(dx), int(dy))); L = M
    if alpha < 1: L = L.copy(); L.putalpha(L.getchannel("A").point(lambda v: int(v * alpha)))
    return Image.alpha_composite(base, L)

DUR = 13.0
def frame(t):
    fr = Image.alpha_composite(bg, snow(FAR, t, 0.8)); fr = Image.alpha_composite(fr, snow(MID, t))
    a = ease_out((t - 0.2) / 0.8); fr = place(fr, LOGO_L, a, dy=-40 * (1 - a))
    a = back_out((t - 0.8) / 0.7); fr = place(fr, WINTER_L, max(0, min(1, (t - 0.8) / 0.3)), dy=-120 * (1 - a))
    a = ease_out((t - 1.6) / 0.6); fr = place(fr, SUB_L, a, dy=30 * (1 - a))
    for i, P in enumerate(PILLS):
        a = ease_out((t - 2.3 - i * 0.4) / 0.55); fr = place(fr, P, a, dx=-W * 0.6 * (1 - a))
    a = ease_out((t - 4.6) / 0.6)
    fr = place(fr, PHONE_L, a, dy=40 * (1 - a))
    fr = Image.alpha_composite(fr, snow(NEAR, t, 2.5))
    return fr.convert("RGB")

render("13-winter-services-snow.mp4", [{"dur": DUR, "fn": lambda u: frame(u * DUR)}])
