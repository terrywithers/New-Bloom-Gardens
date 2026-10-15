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
ITEMS = [("Gutter clearing & fascia wash", "Clear gutters before the winter rain"),
         ("Hedge cutting & reshaping", "Neat, tidy hedges all winter long"),
         ("Leaf clearance & tidy-ups", "Safe paths and a healthier lawn"),
         ("Moss & driveway treatment", "Slip-free drives and patios"),
         ("Commercial grounds & gritting", "Sites kept safe and presentable")]
PILL_Y0, PILL_H, PILL_GAP = 935, 96, 20
def pill_layer(i, name, _desc):
    def fn(d, L):
        y = PILL_Y0 + i * (PILL_H + PILL_GAP)
        d.rounded_rectangle([110, y, W - 110, y + PILL_H], radius=PILL_H // 2, fill=CRIMSON)
        f = F(600, 42); d.text(((W - d.textlength(name, font=f)) / 2, y + 22), name, font=f, fill=(255, 255, 255))
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

# One card per service: name + short line, no prices or numbering
def wrap(d, txt, font, maxw):
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if d.textlength(test, font=font) <= maxw: cur = test
        else: lines.append(cur); cur = w_
    return lines + [cur]
CARD_BOX = (90, 720, W - 90, 1330)
def card_layer(name, desc):
    def fn(d, L):
        x0, y0, x1, y1 = CARD_BOX
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 22, x1, y1 + 22], 48, fill=(50, 70, 85, 80))
        L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
        d.rounded_rectangle([x0, y0, x1, y1], 48, fill=(255, 255, 255, 242))
        # little snowflake glyph drawn with lines
        cx, cy, r = W / 2, y0 + 105, 38
        for k in range(6):
            ang = k * math.pi / 3; ex, ey = cx + r * math.cos(ang), cy + r * math.sin(ang)
            d.line([cx, cy, ex, ey], fill=(150, 185, 205), width=6)
            for sgn in (-1, 1):
                bx, by = cx + r * 0.6 * math.cos(ang), cy + r * 0.6 * math.sin(ang)
                d.line([bx, by, bx + 16 * math.cos(ang + sgn * 0.8), by + 16 * math.sin(ang + sgn * 0.8)], fill=(150, 185, 205), width=5)
        size = 84
        while len(wrap(d, name, F(700, size), x1 - x0 - 120)) > 2: size -= 2
        f = F(700, size); lines = wrap(d, name, f, x1 - x0 - 120)
        y = y0 + 190 + (2 - len(lines)) * 45
        for ln in lines: centered(d, y, ln, f, CRIMSON); y += int(size * 1.2)
        d.rectangle([W / 2 - 50, y + 26, W / 2 + 50, y + 34], fill=(201, 220, 188))
        fd = F(400, 42)
        for j, ln in enumerate(wrap(d, desc, fd, x1 - x0 - 140)): centered(d, y + 70 + j * 58, ln, fd, (70, 84, 64))
    return layer(fn)
CARDS = [card_layer(n, ds) for n, ds in ITEMS]
SMALL_LOGO = layer(lambda d, L: (lambda lg: L.paste(lg, ((W - lg.width) // 2, 230), lg))(LOGO.resize((300, int(LOGO.height * 300 / LOGO.width)))))
def _wsmall(d, L):
    f = F(700, 92); txt = "WINTER"; x = (W - d.textlength(txt, font=f)) / 2
    d.text((x + 4, 470 + 4), txt, font=f, fill=(255, 255, 255)); d.text((x, 470), txt, font=f, fill=CRIMSON)
WINTER_SMALL = layer(_wsmall)
def text_mask(size, y):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m); f = F(700, size)
    d.text(((W - d.textlength("WINTER", font=f)) / 2, y), "WINTER", font=f, fill=255); return m
MASK_BIG, MASK_SMALL = text_mask(210, 488), text_mask(92, 470)

# Effect: frosted edges
frost = Image.new("L", (W, H), 255); ImageDraw.Draw(frost).rounded_rectangle([60, 60, W - 60, H - 60], 120, fill=0)
frost = frost.filter(ImageFilter.GaussianBlur(70)).point(lambda v: int(v * 0.55))
FROST = Image.new("RGBA", (W, H), (255, 255, 255, 0)); FROST.putalpha(frost)

# Effect: shimmer sweep masked to WINTER
def shimmer(fr, mask, p):
    if p <= 0 or p >= 1: return fr
    band = Image.new("L", (W, H), 0); bd = ImageDraw.Draw(band)
    cx = -300 + p * (W + 600)
    bd.polygon([(cx - 60, 0), (cx + 60, 0), (cx + 60 - 500, H), (cx - 60 - 500, H)], fill=200)
    band = band.filter(ImageFilter.GaussianBlur(25))
    from PIL import ImageChops
    a = ImageChops.multiply(band, mask)
    lay = Image.new("RGBA", (W, H), (255, 255, 255, 0)); lay.putalpha(a)
    return Image.alpha_composite(fr, lay)

# Effect: twinkling sparkles
random.seed(11)
SPARKS = [dict(x=random.uniform(60, W - 60), y=random.uniform(120, H - 300), s=random.uniform(14, 30), ph=random.uniform(0, 6.28), f=random.uniform(1.2, 2.4)) for _ in range(26)]
def sparkles(t):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for sp in SPARKS:
        a = max(0.0, math.sin(sp["ph"] + sp["f"] * t)) ** 6
        if a < 0.05: continue
        s = sp["s"] * (0.6 + 0.4 * a); x, y = sp["x"], sp["y"]; al = int(255 * a)
        d.polygon([(x, y - s), (x + s * 0.18, y), (x, y + s), (x - s * 0.18, y)], fill=(255, 255, 255, al))
        d.polygon([(x - s, y), (x, y - s * 0.18), (x + s, y), (x, y + s * 0.18)], fill=(255, 255, 255, al))
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255, al))
    return L.filter(ImageFilter.GaussianBlur(0.8))

# Effect: wind gusts at each card change push the snow sideways
INTRO, EACH, OUTRO = 3.0, 2.4, 4.8
GUSTS = [INTRO + EACH * k for k in range(len(ITEMS) + 1)]
def gust(t): return sum(160 / (1 + math.exp(-(t - g) * 5)) for g in GUSTS)
def snow_w(flakes, t, depth, blur=0):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); gx = gust(t) * depth
    for f in flakes:
        y = (f["y"] + f["v"] * t) % (H + 60) - 30
        x = (f["x"] + f["sw"] * math.sin(f["ph"] + f["f"] * t * 2) + gx) % (W + 40) - 20
        d.ellipse([x - f["r"], y - f["r"], x + f["r"], y + f["r"]], fill=(255, 255, 255, f["a"]))
    return L.filter(ImageFilter.GaussianBlur(blur)) if blur else L

def transform_layer(L, box, scale=1.0, angle=0.0, alpha=1.0, dx=0, dy=0, blur=0):
    x0, y0, x1, y1 = box; pad = 60
    crop = L.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad))
    if scale != 1.0: crop = crop.resize((max(1, int(crop.width * scale)), max(1, int(crop.height * scale))), Image.BICUBIC)
    if angle: crop = crop.rotate(angle, resample=Image.BICUBIC, expand=True)
    if blur: crop = crop.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1: crop.putalpha(crop.getchannel("A").point(lambda v: int(v * alpha)))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy = (x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy
    out.paste(crop, (int(cx - crop.width / 2), int(cy - crop.height / 2)), crop); return out

PHONE_GLOW = layer(lambda d, L: centered(d, 1520, "07504 548304", F(700, 112), (255, 255, 255))).filter(ImageFilter.GaussianBlur(22))
DUR = INTRO + EACH * len(CARDS) + OUTRO
def base(t):
    fr = Image.alpha_composite(bg, snow_w(FAR, t, 0.5, 0.8)); return Image.alpha_composite(fr, snow_w(MID, t, 1.0))
def frame(t):
    fr = base(t)
    if t < INTRO:
        a = ease_out((t - 0.2) / 0.8); fr = place(fr, LOGO_L, a, dy=-40 * (1 - a))
        a = back_out((t - 0.8) / 0.7); fr = place(fr, WINTER_L, max(0, min(1, (t - 0.8) / 0.3)), dy=-120 * (1 - a))
        fr = shimmer(fr, MASK_BIG, (t - 1.5) / 0.9)
        a = ease_out((t - 1.7) / 0.6); fr = place(fr, SUB_L, a, dy=30 * (1 - a))
        out = ease_out((t - (INTRO - 0.35)) / 0.35)
        if out > 0: fr = Image.blend(fr, base(t), out)
    elif t < INTRO + EACH * len(CARDS):
        k = int((t - INTRO) / EACH); lt = t - INTRO - k * EACH
        hdr = ease_out((t - INTRO) / 0.4)
        fr = place(fr, SMALL_LOGO, hdr); fr = place(fr, WINTER_SMALL, hdr)
        fr = shimmer(fr, MASK_SMALL, (lt - 0.5) / 0.8)
        a_in = back_out(lt / 0.55); swing = math.exp(-lt * 4) * math.sin(lt * 14) * 5
        a_out = ease_out((lt - (EACH - 0.3)) / 0.3)
        if a_out <= 0:
            fr = Image.alpha_composite(fr, transform_layer(CARDS[k], CARD_BOX, scale=0.85 + 0.15 * a_in, angle=swing,
                                                          alpha=min(1, lt / 0.2), dy=-500 * (1 - min(1, a_in))))
        else:
            fr = Image.alpha_composite(fr, transform_layer(CARDS[k], CARD_BOX, scale=1 + 0.08 * a_out, alpha=1 - a_out,
                                                          dx=260 * a_out, dy=60 * a_out, blur=6 * a_out))
    else:
        lt = t - INTRO - EACH * len(CARDS)
        a = ease_out(lt / 0.6); fr = place(fr, LOGO_L, a)
        a = back_out((lt - 0.1) / 0.6); fr = place(fr, WINTER_L, min(1, lt / 0.3), dy=-80 * (1 - a))
        fr = shimmer(fr, MASK_BIG, (lt - 2.4) / 0.9)
        fr = place(fr, SUB_L, ease_out((lt - 0.4) / 0.5))
        for i, P in enumerate(PILLS):
            y = PILL_Y0 + i * (PILL_H + PILL_GAP); pt = (lt - 0.6 - i * 0.18) / 0.45
            if pt <= 0: continue
            fr = Image.alpha_composite(fr, transform_layer(P, (110, y, W - 110, y + PILL_H), scale=0.6 + 0.4 * back_out(pt), alpha=min(1, pt * 2)))
        pa = ease_out((lt - 1.7) / 0.5)
        if pa > 0:
            glow = 0.35 + 0.35 * (0.5 + 0.5 * math.sin((lt - 1.7) * 4))
            fr = place(fr, PHONE_GLOW, pa * glow); fr = place(fr, PHONE_L, pa, dy=40 * (1 - pa))
    fr = Image.alpha_composite(fr, sparkles(t))
    fr = Image.alpha_composite(fr, snow_w(NEAR, t, 2.0, 2.5))
    fr = Image.alpha_composite(fr, FROST)
    return fr.convert("RGB")

render("13-winter-services-snow.mp4", [{"dur": DUR, "fn": lambda u: frame(u * DUR)}])
