"""Render vertical Reels (1080x1920) from still photos: Ken Burns motion, before/after wipe, branded end card."""
import subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

S = "/tmp/claude-0/-home-user-New-Bloom-Gardens/50fca177-b464-52b5-8e0a-10c4356f2d3e/scratchpad"
U = "/root/.claude/uploads/50fca177-b464-52b5-8e0a-10c4356f2d3e/"
OUT = "/home/user/New-Bloom-Gardens/marketing/reels/"
W, H, FPS = 1080, 1920, 30
CRIMSON, GREEN, SAGE, INK = (184, 53, 85), (98, 128, 82), (238, 242, 232), (31, 42, 28)
F = lambda w, s: ImageFont.truetype(f"{S}/font/package/files/poppins-latin-{w}-normal.woff", s)

LOGO = Image.open("/home/user/New-Bloom-Gardens/website/img/logo.png").convert("RGBA")

def load(path):
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")

def cover_scale(img):
    return max(W / img.width, H / img.height)

def frame_kenburns(img, t, z0, z1, px0=0.5, px1=0.5, py0=0.5, py1=0.5):
    """t in [0,1]. Zoom z (1 = cover). Pan centre (px,py) as fractions of the free space."""
    e = 0.5 - 0.5 * math.cos(math.pi * t)  # ease in-out
    z = z0 + (z1 - z0) * e
    s = cover_scale(img) * z
    vw, vh = W / s, H / s  # visible window in source pixels
    px = px0 + (px1 - px0) * e; py = py0 + (py1 - py0) * e
    x0 = (img.width - vw) * px; y0 = (img.height - vh) * py
    return img.transform((W, H), Image.AFFINE, (1 / s, 0, x0, 0, 1 / s, y0), resample=Image.BICUBIC)

_SHADE = {}
def shade(fr, top=True, bottom=True):
    key = (top, bottom)
    if key in _SHADE: return Image.alpha_composite(fr.convert("RGBA"), _SHADE[key])
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i in range(620):
        a = int(190 * (1 - i / 620) ** 1.6)
        if top: d.line([(0, i), (W, i)], fill=(0, 0, 0, a))
        if bottom: d.line([(0, H - 1 - i), (W, H - 1 - i)], fill=(0, 0, 0, a))
    _SHADE[key] = ov
    return Image.alpha_composite(fr.convert("RGBA"), ov)

def text_center(d, y, txt, font, fill=(255, 255, 255), shadow=True, maxw=940):
    # wrap
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if d.textlength(test, font=font) <= maxw: cur = test
        else: lines.append(cur); cur = w_
    lines.append(cur)
    lh = font.size * 1.18
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=font); x = (W - tw) / 2; yy = y + i * lh
        if shadow: d.text((x + 3, yy + 3), ln, font=font, fill=(0, 0, 0, 140))
        d.text((x, yy), ln, font=font, fill=fill)
    return y + len(lines) * lh

def pill(d, cx, y, txt, bg=CRIMSON):
    f = F(700, 44); tw = d.textlength(txt, font=f)
    pad_x, h = 34, 78
    d.rounded_rectangle([cx - tw / 2 - pad_x, y, cx + tw / 2 + pad_x, y + h], radius=h // 2, fill=bg)
    d.text((cx - tw / 2, y + 12), txt, font=f, fill=(255, 255, 255))

def overlay(fr, label=None, hook=None, caption=None, alpha=1.0):
    fr = shade(fr, top=True, bottom=bool(caption))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    if label: pill(d, W / 2, 250, label)
    if hook: text_center(d, 370, hook, F(700, 66))
    if caption: text_center(d, 1330, caption, F(600, 44))
    if alpha < 1: layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    return Image.alpha_composite(fr, layer).convert("RGB")

def end_card(lines):
    card = Image.new("RGB", (W, H), SAGE); d = ImageDraw.Draw(card)
    lg = LOGO.copy(); lg.thumbnail((560, 560)); card.paste(lg, ((W - lg.width) // 2, 330), lg)
    y = 330 + lg.height + 90
    y = text_center(d, y, lines[0], F(700, 76), fill=INK, shadow=False)
    y = text_center(d, y + 20, lines[1], F(400, 44), fill=(86, 98, 79), shadow=False)
    f = F(700, 92); ph = "07504 548304"; tw = d.textlength(ph, font=f)
    d.text(((W - tw) / 2, y + 60), ph, font=f, fill=CRIMSON)
    d.text(((W - d.textlength("Call or WhatsApp", font=F(600, 40))) / 2, y + 190), "Call or WhatsApp", font=F(600, 40), fill=GREEN)
    site = "newbloomgardens.co.uk"; fs = F(600, 46)
    d.text(((W - d.textlength(site, font=fs)) / 2, y + 290), site, font=fs, fill=INK)
    return card

def render(name, segments):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                          "-c:a", "aac", "-b:a", "96k", OUT + name], stdin=subprocess.PIPE)
    n = 0
    for seg in segments:
        frames = int(seg["dur"] * FPS)
        for i in range(frames):
            p.stdin.write(seg["fn"](i / max(frames - 1, 1)).tobytes()); n += 1
    p.stdin.close(); p.wait()
    print(name, n / FPS, "s")

def before_after_reel(name, before, after, hook_b, hook_a, caption, end, kb_b=(1.0, 1.12), kb_a=(1.12, 1.0)):
    B, A = load(before), load(after)
    card = end_card(end)
    fb = lambda t: overlay(frame_kenburns(B, t, *kb_b), "BEFORE", hook_b)
    fa = lambda t: overlay(frame_kenburns(A, t, *kb_a), "AFTER", hook_a, caption)
    def wipe(t):
        e = 0.5 - 0.5 * math.cos(math.pi * t)
        b = frame_kenburns(B, 1, *kb_b); a = frame_kenburns(A, 0, *kb_a)
        x = int(W * e); out = b.copy(); out.paste(a.crop((0, 0, x, H)), (0, 0))
        d = ImageDraw.Draw(out); d.rectangle([x - 4, 0, x + 4, H], fill=(255, 255, 255))
        return out
    def fade(t):
        return Image.blend(fa(1), card, t)
    render(name, [
        {"dur": 3.0, "fn": fb},
        {"dur": 0.9, "fn": wipe},
        {"dur": 3.6, "fn": fa},
        {"dur": 0.5, "fn": fade},
        {"dur": 2.5, "fn": lambda t: card},
    ])

def pan_reel(name, img_path, hook, caption, end):
    I = load(img_path); card = end_card(end)
    f = lambda t: overlay(frame_kenburns(I, t, 1.02, 1.02, 0.0, 1.0), None, hook if t < 0.55 else None, caption if t >= 0.45 else None)
    render(name, [
        {"dur": 6.5, "fn": f},
        {"dur": 0.5, "fn": lambda t: Image.blend(f(1), card, t)},
        {"dur": 2.5, "fn": lambda t: card},
    ])

if __name__ == "__main__":
    import os; os.makedirs(OUT, exist_ok=True)
    which = sys.argv[1:] or ["1", "2", "3", "4"]
    END_HOME = ["Free quotes", "Chelmsford, Essex & East London"]
    if "1" in which:
        before_after_reel("01-back-garden-rescue.mp4", U + "9c573e1b-image.jpg", U + "f05a9baa-image.jpg",
                          "This garden hadn't been touched all summer", "One day later",
                          "Cut back, cleared and ready for an autumn lawn rescue", END_HOME)
    if "2" in which:
        before_after_reel("02-rear-garden-tidy.mp4", f"{S}/img/pw-004.png", f"{S}/img/pw-005.png",
                          "Can you spot the path?", "There it is",
                          "Full garden tidy · all waste taken away", END_HOME)
    if "3" in which:
        before_after_reel("03-side-path-clearance.mp4", f"{S}/img/ck-007.png", f"{S}/img/ck-008.png",
                          "Couldn't get down the side of the house", "Now you can",
                          "Shrubs cut back · path weeded and swept", END_HOME)
    if "4" in which:
        pan_reel("04-lawn-stripes.mp4", f"{S}/img/br-000.png",
                 "The lawns are back in town", "Regular garden maintenance · same team every visit",
                 ["Book your regular visits", "Weekly, fortnightly or monthly"])
