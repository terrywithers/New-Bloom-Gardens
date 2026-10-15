"""Second batch of Reels: before/afters, a stripe montage, and branded graphic reels."""
import sys, math
sys.path.insert(0, "/tmp/claude-0/-home-user-New-Bloom-Gardens/50fca177-b464-52b5-8e0a-10c4356f2d3e/scratchpad")
from reels import *  # W, H, F, colours, load, frame_kenburns, overlay, end_card, render, before_after_reel, text_center, pill, shade
from PIL import Image, ImageDraw, ImageFilter

U = "/root/.claude/uploads/50fca177-b464-52b5-8e0a-10c4356f2d3e/"
P = S + "/new/"
import os; os.makedirs(P, exist_ok=True); os.makedirs(OUT, exist_ok=True)

# Privacy: blur house numbers before anything else touches these photos.
BLUR = {"ae5309c5": (395, 435, 475, 525), "e2274c6e": (865, 710, 940, 800),
        "2d1d28c4": (1370, 95, 1520, 205), "02147620": (1340, 605, 1460, 695)}
def src(code):
    path = P + code + ".jpg"
    if not os.path.exists(path):
        im = load(U + code + "-image.jpg")
        if code in BLUR:
            b = BLUR[code]; region = im.crop(b).filter(ImageFilter.GaussianBlur(18)); im.paste(region, b[:2])
        im.save(path, quality=92)
    return path

ease = lambda t: 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))

def faded_text_layer(draw_fn, alpha, dy):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    draw_fn(d, dy)
    if alpha < 1: layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    return layer

def tip_card(bg, t, num, title, body, tint=(31, 42, 28)):
    fr = frame_kenburns(bg, t, 1.0, 1.08).convert("RGBA")
    fr = Image.alpha_composite(fr, Image.new("RGBA", (W, H), tint + (165,)))
    a = ease(t / 0.18); dy = int(70 * (1 - a))
    def draw(d, dy):
        cy = 560 + dy
        d.ellipse([W / 2 - 95, cy - 95, W / 2 + 95, cy + 95], fill=CRIMSON)
        fn = F(700, 110); tw = d.textlength(str(num), font=fn); d.text((W / 2 - tw / 2, cy - 78), str(num), font=fn, fill=(255, 255, 255))
        y = text_center(d, cy + 160, title, F(700, 76), shadow=False)
        d.rectangle([W / 2 - 50, y + 30, W / 2 + 50, y + 38], fill=(201, 220, 188))
        text_center(d, y + 80, body, F(400, 46), fill=(235, 240, 230), shadow=False, maxw=860)
    return Image.alpha_composite(fr, faded_text_layer(draw, a, dy)).convert("RGB")

def title_card(t, eyebrow, title, bg=CRIMSON):
    card = Image.new("RGBA", (W, H), bg + (255,))
    lg = LOGO.copy(); lg.thumbnail((300, 300))
    chip = Image.new("RGBA", (lg.width + 60, lg.height + 40), (255, 255, 255, 255))
    m = Image.new("L", chip.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, chip.width, chip.height], 28, fill=255)
    card.paste(chip, ((W - chip.width) // 2, 300), m); card.paste(lg, ((W - lg.width) // 2, 320), lg)
    a = ease(t / 0.3); dy = int(80 * (1 - a))
    def draw(d, dy):
        f = F(600, 44); tw = d.textlength(eyebrow.upper(), font=f)
        d.text(((W - tw) / 2, 760 + dy), eyebrow.upper(), font=f, fill=(255, 225, 232))
        text_center(d, 850 + dy, title.upper(), F(700, 104), shadow=False, maxw=900)
    return Image.alpha_composite(card, faded_text_layer(draw, a, dy)).convert("RGB")

def graphic_reel(name, eyebrow, title, tips, end):
    card = end_card(end)
    segs = [{"dur": 2.2, "fn": lambda t: title_card(t, eyebrow, title)}]
    for i, (img, ttl, body) in enumerate(tips, 1):
        bg = load(img)
        segs.append({"dur": 2.8, "fn": (lambda bg, i, ttl, body: lambda t: tip_card(bg, t, i, ttl, body))(bg, i, ttl, body)})
    last = segs[-1]["fn"]
    segs += [{"dur": 0.5, "fn": lambda t: Image.blend(last(1), card, t)}, {"dur": 2.5, "fn": lambda t: card}]
    render(name, segs)

def montage_reel(name, imgs, hook, caption, end, each=1.7, xf=0.35):
    I = [load(p) for p in imgs]; card = end_card(end)
    total = len(I) * each
    def frame(gt):
        i = min(int(gt / each), len(I) - 1); lt = (gt - i * each) / each
        f = frame_kenburns(I[i], lt, 1.0 if i % 2 else 1.1, 1.1 if i % 2 else 1.0, 0.4, 0.6)
        if i + 1 < len(I) and gt > (i + 1) * each - xf:
            nxt = frame_kenburns(I[i + 1], 0, 1.0 if (i + 1) % 2 else 1.1, 1.1 if (i + 1) % 2 else 1.0, 0.4, 0.6)
            f = Image.blend(f, nxt, (gt - ((i + 1) * each - xf)) / xf)
        return overlay(f, None, hook, caption if gt > total * 0.35 else None)
    render(name, [{"dur": total, "fn": lambda t: frame(t * total)},
                  {"dur": 0.5, "fn": lambda t: Image.blend(frame(total), card, t)},
                  {"dur": 2.5, "fn": lambda t: card}])

if __name__ == "__main__":
    which = sys.argv[1:] or [str(i) for i in range(5, 13)]
    END_HOME = ["Free quotes", "Chelmsford, Essex & East London"]
    if "5" in which:
        before_after_reel("05-patio-weeds.mp4", src("46a0d663"), src("dfded527"),
                          "Weeds through every slab", "Sorted",
                          "Patio weeded · lawn cut · all waste taken away", END_HOME)
    if "6" in which:
        before_after_reel("06-front-garden-kerb-appeal.mp4", src("ae5309c5"), src("e2274c6e"),
                          "Front garden got away from them", "Kerb appeal: restored",
                          "Overgrowth cleared back to the slate", ["Selling or letting?", "Pre-sale and end-of-tenancy garden tidy-ups"])
    if "7" in which:
        before_after_reel("07-driveway-weeds.mp4", src("2d1d28c4"), src("02147620"),
                          "Weeds taking over the drive?", "Cleared and swept",
                          "Weeds pulled from the paving and borders", END_HOME)
    if "8" in which:
        before_after_reel("08-hedge-path.mp4", src("3774e6c3"), src("605ed594"),
                          "Could barely get the ladder through", "Path opened back up",
                          "Hedges and shrubs cut back from the path", END_HOME)
    if "9" in which:
        before_after_reel("09-barn-lawn-stripes.mp4", src("40d43ba9"), src("34ea0b0e"),
                          "From this...", "...to this",
                          "Regular mowing brings the stripes back", ["Book your regular visits", "Weekly, fortnightly or monthly"])
    if "10" in which:
        montage_reel("10-stripe-season.mp4", [src("11a6dc9c"), src("7f56d03b"), src("2a527dad"), f"{S}/img/br-000.png", src("34ea0b0e")],
                     "Who doesn't love a striped lawn?", "Regular mowing rounds across Chelmsford",
                     ["Book your regular visits", "Weekly, fortnightly or monthly"])
    if "11" in which:
        graphic_reel("11-winter-garden-checklist.mp4", "4 jobs before winter", "Get your garden winter-ready", [
            (src("2a527dad"), "Clear fallen leaves", "Leaves left on the lawn block the light and leave yellow patches by spring."),
            (src("7f56d03b"), "Give the lawn a last cut", "Raise the mower blades and cut on a dry day until the grass stops growing."),
            (src("3774e6c3"), "Cut back hedges", "Autumn and winter are ideal for bigger cuts, outside bird nesting season."),
            (src("02147620"), "Clear the gutters", "Blocked gutters overflow in winter rain and can damage walls and fascias."),
        ], ["Short on time?", "Leaf clearance from £60 · gutters from £80"])
    if "12" in which:
        graphic_reel("12-why-new-bloom.mp4", "Why customers choose us", "Kept grounds. Kept promises.", [
            (src("11a6dc9c"), "Same team every visit", "People who know your garden, not a different face each time."),
            (src("46a0d663"), "Fixed price first", "An itemised quote before we start. No surprises on the invoice."),
            (src("dfded527"), "Photo report every job", "Before and after photos sent when we finish, so you know it's done."),
            (src("605ed594"), "Insured and licensed", "Fully insured. Upper Tier waste carrier. Every bit of waste taken away."),
        ], ["Free quotes", "Homes, landlords and managed properties"])
