#!/usr/bin/env python3
"""Render the 30-second UpOn 2.1 product film.

The film uses only UpOn's real application captures, deterministic typography,
and an original synthesized sound bed. Run with --preview before a full encode.
"""

from __future__ import annotations

import argparse
import math
import subprocess
import textwrap
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


W, H = 1920, 1080
FPS = 24
DURATION = 30.0

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT.parent / "upon-macos"
SHOTS = APP / "tmp" / "screenshots"
ICON_PATH = APP / "Resources" / "UpOnIcon.iconset" / "icon_512x512.png"
WORK = ROOT / "motion" / "work"
OUT = ROOT / "dist" / "assets" / "upon-2.1-30s.mp4"
POSTER = ROOT / "dist" / "assets" / "upon-motion-poster.jpg"
TEMP_VIDEO = WORK / "upon-motion-video.mp4"
AUDIO = WORK / "upon-motion-original.wav"

FONT = Path("/System/Library/Fonts/SFNS.ttf")
MONO = Path("/System/Library/Fonts/SFNSMono.ttf")
if not MONO.exists():
    MONO = FONT

WHITE = (246, 249, 253)
MUTED = (154, 168, 186)
BLUE = (0, 120, 255)
BLUE_BRIGHT = (41, 151, 255)
BLACK = (5, 8, 13)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT), size=size)


def mono(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(MONO), size=size)


F_LABEL = mono(18)
F_META = mono(15)
F_TITLE = font(96)
F_TITLE_SMALL = font(76)
F_BODY = font(32)
F_CHIP = font(23)
F_HERO = font(132)
F_BRAND = font(74)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease_out(value: float) -> float:
    value = clamp(value)
    return 1 - (1 - value) ** 3


def ease_in_out(value: float) -> float:
    value = clamp(value)
    return value * value * (3 - 2 * value)


def active_opacity(t: float, start: float, end: float, fade: float = 0.55) -> float:
    return clamp((t - start) / fade) * clamp((end - t) / fade)


def draw_tracking(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                  typeface: ImageFont.FreeTypeFont, fill: tuple[int, ...], spacing: int = 3) -> None:
    x, y = xy
    for character in text:
        draw.text((x, y), character, font=typeface, fill=fill)
        bbox = draw.textbbox((x, y), character, font=typeface)
        x += bbox[2] - bbox[0] + spacing


def crop_black_margin(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
    difference = ImageChops.difference(rgb, background)
    bbox = difference.getbbox()
    if not bbox:
        return rgb
    left, top, right, bottom = bbox
    pad = 8
    return rgb.crop((max(0, left - pad), max(0, top - pad), min(rgb.width, right + pad), min(rgb.height, bottom + pad)))


def make_screen_card(source: Path, maximum: tuple[int, int], radius: int = 30) -> Image.Image:
    screenshot = crop_black_margin(Image.open(source))
    screenshot = ImageOps.contain(screenshot, maximum, Image.Resampling.LANCZOS)
    mask = Image.new("L", screenshot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, screenshot.width, screenshot.height), radius=radius, fill=255)
    shot = screenshot.convert("RGBA")
    shot.putalpha(mask)

    pad = 34
    shadow_margin = 60
    size = (shot.width + pad * 2 + shadow_margin * 2, shot.height + pad * 2 + shadow_margin * 2)
    card = Image.new("RGBA", size, (0, 0, 0, 0))
    bounds = (shadow_margin, shadow_margin, size[0] - shadow_margin, size[1] - shadow_margin)

    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(bounds, radius=radius + 16, fill=(0, 0, 0, 190))
    shadow = shadow.filter(ImageFilter.GaussianBlur(34))
    card.alpha_composite(shadow)

    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle(bounds, radius=radius + 16, fill=(14, 20, 30, 245), outline=(255, 255, 255, 42), width=2)
    card.alpha_composite(shot, (shadow_margin + pad, shadow_margin + pad))
    return card


def resize_icon(size: int) -> Image.Image:
    icon = Image.open(ICON_PATH).convert("RGBA")
    return icon.resize((size, size), Image.Resampling.LANCZOS)


SCREENS = {
    "import": make_screen_card(SHOTS / "upon-1.8-import-final.png", (1030, 840)),
    "verify": make_screen_card(SHOTS / "upon-1.7-biomarkers.png", (1040, 850)),
    "timeline": make_screen_card(SHOTS / "upon-1.7-timeline.png", (1040, 850)),
    "plan": make_screen_card(SHOTS / "upon-1.7-plan.png", (1040, 850)),
    "ask": make_screen_card(SHOTS / "upon-1.4-quick-chat.png", (1060, 820)),
}
ICON_180 = resize_icon(180)
ICON_108 = resize_icon(108)


def make_base() -> Image.Image:
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    top = np.array([7, 13, 23], dtype=np.float32)[None, None, :]
    bottom = np.array([3, 6, 11], dtype=np.float32)[None, None, :]
    gradient = top * (1 - y) + bottom * y
    gradient = np.repeat(gradient, W, axis=1)
    return Image.fromarray(gradient.astype(np.uint8)).convert("RGBA")


BASE = make_base()


def paste_opacity(canvas: Image.Image, item: Image.Image, xy: tuple[int, int], opacity: float) -> None:
    if opacity <= 0:
        return
    item = item.copy()
    alpha = item.getchannel("A").point(lambda value: int(value * clamp(opacity)))
    item.putalpha(alpha)
    canvas.alpha_composite(item, xy)


def ambient_background(t: float) -> Image.Image:
    frame = BASE.copy()
    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(light)

    x = int(W * (.71 + .08 * math.sin(t * .19)))
    y = int(H * (.24 + .06 * math.cos(t * .17)))
    draw.ellipse((x - 420, y - 420, x + 420, y + 420), fill=(0, 120, 255, 72))
    x2 = int(W * (.25 + .05 * math.cos(t * .14)))
    y2 = int(H * (.82 + .04 * math.sin(t * .23)))
    draw.ellipse((x2 - 330, y2 - 330, x2 + 330, y2 + 330), fill=(35, 62, 112, 34))
    light = light.filter(ImageFilter.GaussianBlur(135))
    frame.alpha_composite(light)

    draw = ImageDraw.Draw(frame)
    grid = (255, 255, 255, 12)
    for gx in range(80, W, 160):
        draw.line((gx, 0, gx, H), fill=grid, width=1)
    for gy in range(60, H, 120):
        draw.line((0, gy, W, gy), fill=(255, 255, 255, 8), width=1)

    arc_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    arcs = ImageDraw.Draw(arc_layer)
    rotation = (t * 13) % 360
    for idx, diameter in enumerate((640, 780, 930)):
        bounds = (W - diameter // 2 - 80, -diameter // 2 + 70, W + diameter // 2 - 80, diameter // 2 + 70)
        arcs.arc(bounds, start=rotation + idx * 34, end=rotation + 88 + idx * 34, fill=(0, 120, 255, 45 - idx * 8), width=2)
    frame.alpha_composite(arc_layer)

    draw_tracking(draw, (76, 54), "UPON / PRIVATE HEALTH INTELLIGENCE", F_META, (154, 168, 186, 155), 2)
    draw_tracking(draw, (1612, 54), f"00:{t:05.2f}", F_META, (154, 168, 186, 130), 2)
    return frame


def text_block(label: str, title: str, body: str, width: int = 600, small: bool = False) -> Image.Image:
    layer = Image.new("RGBA", (width, 680), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw_tracking(draw, (0, 0), label.upper(), F_LABEL, (*BLUE_BRIGHT, 255), 3)
    title_font = F_TITLE_SMALL if small else F_TITLE
    draw.multiline_text((0, 70), title, font=title_font, fill=(*WHITE, 255), spacing=2)
    title_box = draw.multiline_textbbox((0, 70), title, font=title_font, spacing=2)
    wrapped = textwrap.fill(body, width=38 if width < 640 else 43)
    draw.multiline_text((0, title_box[3] + 44), wrapped, font=F_BODY, fill=(*MUTED, 255), spacing=14)
    return layer


def scene_intro(t: float) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    local = clamp(t / 3.2)
    appear = ease_out(clamp(local / .42))
    icon_y = int(180 + 34 * (1 - appear))
    paste_opacity(layer, ICON_180, (150, icon_y), appear)
    draw = ImageDraw.Draw(layer)
    draw_tracking(draw, (374, 215), "UPON 2.1", mono(23), (*MUTED, int(255 * appear)), 5)
    title_x = int(150 + 44 * (1 - ease_out(clamp((local - .12) / .42))))
    title_alpha = int(255 * clamp((local - .08) / .32))
    draw.text((title_x, 430), "Your health.", font=F_HERO, fill=(*WHITE, title_alpha))
    draw.text((title_x, 562), "In context.", font=F_HERO, fill=(*BLUE_BRIGHT, title_alpha))
    line_progress = ease_in_out(clamp((local - .25) / .55))
    draw.line((150, 748, 150 + int(680 * line_progress), 748), fill=(*BLUE, int(230 * appear)), width=5)
    draw_tracking(draw, (150, 790), "IMPORT · VERIFY · UNDERSTAND", F_LABEL, (*MUTED, int(220 * appear)), 4)
    return layer


def screen_scene(t: float, start: float, end: float, key: str, side: str,
                 label: str, title: str, body: str, small: bool = False) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    local = clamp((t - start) / (end - start))
    enter = ease_out(clamp(local / .20))
    opacity = active_opacity(t, start, end)
    card = SCREENS[key]
    copy = text_block(label, title, body, width=650 if side == "right" else 610, small=small)

    if side == "right":
        card_x = int(-45 - 55 * (1 - enter))
        card_y = (H - card.height) // 2 + 18
        copy_x = 1240 + int(55 * (1 - enter))
        copy_y = 240
    else:
        copy_x = 120 + int(-55 * (1 - enter))
        copy_y = 240
        card_x = W - card.width + 35 + int(55 * (1 - enter))
        card_y = (H - card.height) // 2 + 18

    paste_opacity(layer, card, (card_x, card_y), opacity)
    paste_opacity(layer, copy, (copy_x, copy_y + int(30 * (1 - enter))), opacity)

    draw = ImageDraw.Draw(layer)
    progress_x = 120 if side == "left" else 1240
    draw.line((progress_x, 850, progress_x + int(390 * ease_in_out(local)), 850), fill=(*BLUE, int(220 * opacity)), width=4)
    draw_tracking(draw, (progress_x, 880), f"{int((start / DURATION) * 100):02d} — {int((end / DURATION) * 100):02d}", F_META, (*MUTED, int(180 * opacity)), 3)
    return layer


def scene_trend(t: float, start: float, end: float) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    local = clamp((t - start) / (end - start))
    opacity = active_opacity(t, start, end)
    draw = ImageDraw.Draw(layer)
    copy = text_block("03 / TRENDS", "See what\nchanged.", "UpOn compares reviewed values over time—without calling movement good or bad.", width=650)
    paste_opacity(layer, copy, (120, 235 + int(30 * (1 - ease_out(local / .2)))), opacity)

    chart = Image.new("RGBA", (980, 650), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(chart)
    cdraw.rounded_rectangle((0, 0, 979, 649), radius=42, fill=(10, 17, 27, 220), outline=(255, 255, 255, 35), width=2)
    draw_tracking(cdraw, (48, 43), "VERIFIED HISTORY / SOURCE-LINKED", F_META, (*MUTED, 220), 2)
    for gy in (175, 285, 395, 505):
        cdraw.line((48, gy, 928, gy), fill=(255, 255, 255, 24), width=1)

    points = [(62, 500), (210, 458), (360, 473), (512, 352), (672, 378), (826, 238), (925, 260)]
    visible = ease_in_out(clamp((local - .08) / .68))
    path_points: list[tuple[int, int]] = []
    total_segments = len(points) - 1
    exact = visible * total_segments
    complete = int(exact)
    fraction = exact - complete
    path_points.extend(points[: complete + 1])
    if complete < total_segments:
        a, b = points[complete], points[complete + 1]
        path_points.append((int(a[0] + (b[0] - a[0]) * fraction), int(a[1] + (b[1] - a[1]) * fraction)))
    if len(path_points) > 1:
        glow = Image.new("RGBA", chart.size, (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.line(path_points, fill=(0, 120, 255, 150), width=18, joint="curve")
        glow = glow.filter(ImageFilter.GaussianBlur(14))
        chart.alpha_composite(glow)
        cdraw = ImageDraw.Draw(chart)
        cdraw.line(path_points, fill=(*BLUE_BRIGHT, 255), width=6, joint="curve")
        for point in path_points[:-1]:
            cdraw.ellipse((point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5), fill=WHITE)
    cdraw.text((48, 565), "No diagnosis. No invented dates. No hidden score.", font=F_CHIP, fill=(*MUTED, 230))
    paste_opacity(layer, chart, (835, 212), opacity)
    return layer


def scene_outro(t: float, start: float, end: float) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    local = clamp((t - start) / (end - start))
    appear = ease_out(clamp(local / .25))
    fade = active_opacity(t, start, end, fade=.35)
    paste_opacity(layer, ICON_108, (906, 210 + int(30 * (1 - appear))), fade)
    draw = ImageDraw.Draw(layer)
    alpha = int(255 * fade)
    brand_box = draw.textbbox((0, 0), "UpOn 2.1", font=F_BRAND)
    draw.text(((W - (brand_box[2] - brand_box[0])) // 2, 360), "UpOn 2.1", font=F_BRAND, fill=(*WHITE, alpha))
    slogan = "Your health. In context."
    slogan_box = draw.textbbox((0, 0), slogan, font=F_TITLE_SMALL)
    draw.text(((W - (slogan_box[2] - slogan_box[0])) // 2, 485), slogan, font=F_TITLE_SMALL, fill=(*BLUE_BRIGHT, alpha))
    draw_tracking(draw, (641, 650), "PRIVATE BETA FOR APPLE SILICON MACS", F_LABEL, (*MUTED, alpha), 4)
    draw_tracking(draw, (720, 690), "BY MEJALISM CORP · BINTULU, SARAWAK", F_META, (*MUTED, int(alpha * .8)), 2)
    draw.rounded_rectangle((735, 742, 1185, 822), radius=25, fill=(*BLUE, alpha))
    cta = "DOWNLOAD THE BETA"
    box = draw.textbbox((0, 0), cta, font=F_CHIP)
    draw.text(((W - (box[2] - box[0])) // 2, 767), cta, font=F_CHIP, fill=(*WHITE, alpha))
    draw_tracking(draw, (690, 910), "UPON-BY-MEJALISM.MOAILABS.CHATGPT.SITE", F_META, (*MUTED, int(alpha * .84)), 2)
    draw_tracking(draw, (748, 1015), "EDUCATIONAL SOFTWARE · NOT MEDICAL ADVICE", F_META, (*MUTED, int(alpha * .62)), 2)
    return layer


def render_frame(t: float) -> Image.Image:
    frame = ambient_background(t)
    scenes: list[Image.Image] = []
    if 0.0 <= t <= 3.5:
        intro = scene_intro(t)
        intro.putalpha(int(255 * active_opacity(t, 0.0, 3.5, .45)))
        scenes.append(intro)
    if 3.0 <= t <= 7.4:
        scenes.append(screen_scene(t, 3.0, 7.4, "import", "left", "01 / IMPORT", "Bring the\nreport.", "PDF, image, spreadsheet, or note. The original is encrypted on this Mac before extraction."))
    if 6.9 <= t <= 11.3:
        scenes.append(screen_scene(t, 6.9, 11.3, "verify", "right", "02 / VERIFY", "Check every\nvalue.", "Local OCR proposes the data. You review and correct it before it enters your health history.", small=True))
    if 10.8 <= t <= 15.3:
        scenes.append(scene_trend(t, 10.8, 15.3))
    if 14.8 <= t <= 19.2:
        scenes.append(screen_scene(t, 14.8, 19.2, "timeline", "left", "04 / TIMELINE", "Build the\nstory.", "Connect check-ups, interventions, and milestones to understand the context around the numbers.", small=True))
    if 18.7 <= t <= 23.2:
        scenes.append(screen_scene(t, 18.7, 23.2, "plan", "right", "05 / PLAN", "Choose the\nnext step.", "Prevention. Nutrition. Training. Supplements. Practical prompts stay linked to reviewed evidence.", small=True))
    if 22.7 <= t <= 27.2:
        scenes.append(screen_scene(t, 22.7, 27.2, "ask", "left", "06 / ASK AI", "Your model.\nYour choice.", "OpenAI, Claude, Gemini—or a local model through Ollama, llama.cpp, and LM Studio. Cloud only by consent.", small=True))
    if 26.7 <= t <= 30.0:
        scenes.append(scene_outro(t, 26.7, 30.0))
    for scene in scenes:
        frame.alpha_composite(scene)

    # Fine film grain, deterministic per frame.
    rng = np.random.default_rng(int(t * FPS) + 9102)
    noise = rng.normal(0, 2.0, (H, W, 1)).astype(np.int16)
    rgb = np.asarray(frame.convert("RGB"), dtype=np.int16)
    rgb = np.clip(rgb + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(rgb)


def write_audio() -> None:
    sample_rate = 48_000
    count = int(DURATION * sample_rate)
    t = np.arange(count, dtype=np.float64) / sample_rate
    segment = np.minimum((t / 7.5).astype(int), 3)
    roots = np.array([55.0, 65.406, 73.416, 49.0])
    root = roots[segment]
    phase = 2 * np.pi * np.cumsum(root) / sample_rate
    pulse = .42 + .58 * (np.sin(2 * np.pi * t / 8 - np.pi / 2) * .5 + .5)
    left = .19 * np.sin(phase) + .075 * np.sin(phase * 2.5 + .2) + .048 * np.sin(phase * 4.0)
    right = .19 * np.sin(phase + .035) + .075 * np.sin(phase * 2.5 + .31) + .048 * np.sin(phase * 4.0 + .11)
    left *= pulse
    right *= pulse

    for beat in np.arange(0.0, DURATION, .5):
        start = int(beat * sample_rate)
        length = min(int(.12 * sample_rate), count - start)
        x = np.arange(length) / sample_rate
        env = np.exp(-x * 34)
        tick = .035 * env * np.sin(2 * np.pi * 880 * x)
        left[start:start + length] += tick
        right[start:start + length] += tick * .78

    rng = np.random.default_rng(210)
    for cut in (3.0, 6.9, 10.8, 14.8, 18.7, 22.7, 26.7):
        start = int(cut * sample_rate)
        length = min(int(.65 * sample_rate), count - start)
        x = np.arange(length) / sample_rate
        env = np.exp(-x * 5.7)
        impact = .14 * env * np.sin(2 * np.pi * 92 * x)
        air = .018 * env * rng.normal(0, 1, length)
        left[start:start + length] += impact + air
        right[start:start + length] += impact + air[::-1]

    fade = np.ones(count)
    fade_in = int(.7 * sample_rate)
    fade_out = int(1.2 * sample_rate)
    fade[:fade_in] = np.linspace(0, 1, fade_in)
    fade[-fade_out:] = np.linspace(1, 0, fade_out)
    stereo = np.stack((left * fade, right * fade), axis=1)
    stereo /= max(1.0, np.max(np.abs(stereo)) / .88)
    pcm = (stereo * 32767).astype(np.int16)

    with wave.open(str(AUDIO), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(pcm.tobytes())


def render_previews() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    times = (1.7, 5.3, 9.0, 13.1, 17.1, 21.1, 25.0, 28.4)
    thumbs: list[Image.Image] = []
    for index, timestamp in enumerate(times, start=1):
        image = render_frame(timestamp)
        image.save(WORK / f"preview-{index:02d}-{timestamp:04.1f}.jpg", quality=92)
        thumbs.append(image.resize((480, 270), Image.Resampling.LANCZOS))
    sheet = Image.new("RGB", (960, 1080), BLACK)
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % 2) * 480, (index // 2) * 270))
    sheet.save(WORK / "preview-contact.jpg", quality=92)
    render_frame(1.7).save(POSTER, quality=92, optimize=True)


def render_video() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_audio()
    command = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(TEMP_VIDEO),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    total = int(DURATION * FPS)
    for frame_number in range(total):
        timestamp = frame_number / FPS
        process.stdin.write(render_frame(timestamp).tobytes())
        if frame_number % (FPS * 2) == 0:
            print(f"Rendered {timestamp:04.1f}s / {DURATION:.1f}s", flush=True)
    process.stdin.close()
    return_code = process.wait()
    if return_code:
        raise RuntimeError(f"Video encode failed with status {return_code}")

    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(TEMP_VIDEO), "-i", str(AUDIO),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-t", str(DURATION), "-movflags", "+faststart", str(OUT),
    ], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="Render representative stills only")
    args = parser.parse_args()
    render_previews()
    if not args.preview:
        render_video()


if __name__ == "__main__":
    main()
