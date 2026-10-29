import os
import math
import textwrap
import numpy as np
import imageio.v2 as imageio

from PIL import Image, ImageDraw, ImageFont


# ==========================================
# AUTOTOON AI - VERSION 2
# 60-second vertical cartoon video generator
# ==========================================

WIDTH = 540
HEIGHT = 960

FPS = 12
SCENE_COUNT = 12
SECONDS_PER_SCENE = 5
TOTAL_SECONDS = SCENE_COUNT * SECONDS_PER_SCENE

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "autotoon_short.mp4")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ------------------------------------------
# Default story: 12 scenes
# ------------------------------------------

DEFAULT_STORY = [
    "Ek chhote se gaon mein Aman naam ka ladka rehta tha.",
    "Aman ka sapna tha ki woh ek din bahut bada aadmi bane.",
    "Ek din use raste mein ek purana rahasyamayi box mila.",
    "Box ke andar ek chamakta hua jadui patthar tha.",
    "Patthar achanak chamka aur ek ajeeb awaaz aayi.",
    "Aman darr gaya, lekin usne himmat nahi hari.",
    "Awaaz ne kaha ki asli taakat uske andar hai.",
    "Aman ne gaon ke logon ki madad karna shuru kiya.",
    "Dheere dheere poora gaon usse pyaar karne laga.",
    "Ek din gaon par bahut badi musibat aa gayi.",
    "Aman ne himmat aur samajhdari se sabko bacha liya.",
    "Us din Aman samajh gaya ki asli hero banna kya hota hai!"
]


# ------------------------------------------
# Load story from GitHub Actions input
# ------------------------------------------

story_input = os.environ.get("STORY", "").strip()

if story_input:
    custom_scenes = [
        line.strip()
        for line in story_input.replace("\n", "|").split("|")
        if line.strip()
    ]

    scenes = (custom_scenes + DEFAULT_STORY)[:SCENE_COUNT]
else:
    scenes = DEFAULT_STORY.copy()

while len(scenes) < SCENE_COUNT:
    scenes.append(DEFAULT_STORY[len(scenes) % len(DEFAULT_STORY)])


# ------------------------------------------
# Fonts
# ------------------------------------------

def load_font(size):
    possible_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]

    for path in possible_fonts:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass

    return ImageFont.load_default()


TITLE_FONT = load_font(30)
CAPTION_FONT = load_font(25)
SMALL_FONT = load_font(18)


# ------------------------------------------
# Helpers
# ------------------------------------------

def rounded_box(draw, box, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width
    )


def draw_centered_text(draw, text, y, font, fill, max_width=470):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)

        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    for line in lines[:4]:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]

        draw.text(
            ((WIDTH - text_width) // 2, y),
            line,
            font=font,
            fill=fill,
            stroke_width=1,
            stroke_fill=(20, 20, 35)
        )

        y += 35

    return y


# ------------------------------------------
# Background
# ------------------------------------------

def draw_background(draw, scene_index, frame_number):
    night = scene_index in [3, 4, 9, 10]

    if night:
        sky = (28, 35, 82)
        ground = (34, 88, 63)
        sun_color = (255, 242, 170)
    else:
        sky = (117, 203, 255)
        ground = (95, 178, 92)
        sun_color = (255, 211, 70)

    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=sky)

    # Sun or moon
    sun_x = 440 + int(10 * math.sin(frame_number / 15))
    sun_y = 115

    draw.ellipse(
        (sun_x - 38, sun_y - 38, sun_x + 38, sun_y + 38),
        fill=sun_color
    )

    # Clouds
    if not night:
        cloud_x = (frame_number * 2) % (WIDTH + 150) - 100

        for cx, cy in [(cloud_x, 180), (cloud_x + 220, 270)]:
            draw.ellipse((cx, cy, cx + 70, cy + 35), fill="white")
            draw.ellipse(
                (cx + 25, cy - 20, cx + 85, cy + 35),
                fill="white"
            )
            draw.ellipse(
                (cx + 50, cy, cx + 105, cy + 35),
                fill="white"
            )

    # Distant hills
    draw.polygon(
        [(0, 510), (120, 350), (245, 510)],
        fill=(90, 155, 112)
    )

    draw.polygon(
        [(190, 510), (370, 330), (540, 510)],
        fill=(72, 145, 103)
    )

    # Ground
    draw.rectangle((0, 510, WIDTH, HEIGHT), fill=ground)

    # Road
    draw.polygon(
        [(205, 960), (335, 960), (300, 510), (250, 510)],
        fill=(185, 168, 130)
    )

    # Village house
    draw.rectangle(
        (55, 395, 200, 535),
        fill=(255, 222, 173),
        outline=(80, 55, 48),
        width=4
    )

    draw.polygon(
        [(35, 400), (125, 325), (220, 400)],
        fill=(155, 67, 57),
        outline=(80, 45, 40)
    )

    # House door
    draw.rectangle(
        (105, 455, 150, 535),
        fill=(116, 72, 45),
        outline=(70, 40, 25),
        width=3
    )

    # Window
    draw.rectangle(
        (65, 425, 95, 455),
        fill=(139, 214, 255),
        outline=(75, 65, 50),
        width=3
    )

    # Tree
    draw.rectangle(
        (390, 420, 420, 535),
        fill=(112, 70, 40)
    )

    draw.ellipse(
        (350, 345, 445, 440),
        fill=(42, 132, 64)
    )

    draw.ellipse(
        (390, 320, 475, 410),
        fill=(50, 150, 70)
    )


# ------------------------------------------
# Cartoon boy
# ------------------------------------------

def draw_boy(draw, scene_index, frame_number):
    bob = int(5 * math.sin(frame_number * 0.15))

    center_x = 285
    body_y = 650 + bob

    # Legs
    draw.line(
        (center_x - 20, body_y + 85, center_x - 35, body_y + 145),
        fill=(35, 45, 105),
        width=18
    )

    draw.line(
        (center_x + 20, body_y + 85, center_x + 35, body_y + 145),
        fill=(35, 45, 105),
        width=18
    )

    # Shoes
    draw.ellipse(
        (center_x - 55, body_y + 132,
         center_x - 20, body_y + 155),
        fill=(45, 35, 35)
    )

    draw.ellipse(
        (center_x + 20, body_y + 132,
         center_x + 55, body_y + 155),
        fill=(45, 35, 35)
    )

    # Arms
    draw.line(
        (center_x - 30, body_y + 10,
         center_x - 65, body_y + 65),
        fill=(222, 163, 120),
        width=18
    )

    draw.line(
        (center_x + 30, body_y + 10,
         center_x + 65, body_y + 65),
        fill=(222, 163, 120),
        width=18
    )

    # Shirt
    draw.rounded_rectangle(
        (center_x - 42, body_y - 5,
         center_x + 42, body_y + 100),
        radius=18,
        fill=(40, 105, 230),
        outline=(25, 45, 110),
        width=4
    )

    # Neck
    draw.rectangle(
        (center_x - 13, body_y - 35,
         center_x + 13, body_y - 5),
        fill=(222, 163, 120)
    )

    # Face
    face_y = body_y - 100

    draw.ellipse(
        (center_x - 42, face_y - 45,
         center_x + 42, face_y + 45),
        fill=(235, 180, 135),
        outline=(65, 45, 40),
        width=3
    )

    # Hair
    draw.pieslice(
        (center_x - 45, face_y - 55,
         center_x + 45, face_y + 15),
        start=180,
        end=360,
        fill=(35, 28, 30)
    )

    # Hair spikes
    draw.polygon(
        [
            (center_x - 38, face_y - 25),
            (center_x - 32, face_y - 58),
            (center_x - 10, face_y - 35),
            (center_x + 5, face_y - 62),
            (center_x + 20, face_y - 35),
            (center_x + 37, face_y - 48),
            (center_x + 40, face_y - 15),
        ],
        fill=(35, 28, 30)
    )

    # Eyes
    eye_y = face_y - 2

    draw.ellipse(
        (center_x - 25, eye_y - 7,
         center_x - 10, eye_y + 9),
        fill="white"
    )

    draw.ellipse(
        (center_x + 10, eye_y - 7,
         center_x + 25, eye_y + 9),
        fill="white"
    )

    draw.ellipse(
        (center_x - 20, eye_y - 2,
         center_x - 12, eye_y + 7),
        fill=(25, 30, 45)
    )

    draw.ellipse(
        (center_x + 15, eye_y - 2,
         center_x + 23, eye_y + 7),
        fill=(25, 30, 45)
    )

    # Expression changes
    if scene_index in [3, 4, 9]:
        # Surprised expression
        draw.ellipse(
            (center_x - 9, face_y + 15,
             center_x + 9, face_y + 34),
            outline=(95, 35, 35),
            width=3
        )
    else:
        # Smile
        draw.arc(
            (center_x - 15, face_y + 10,
             center_x + 15, face_y + 30),
            start=0,
            end=180,
            fill=(95, 35, 35),
            width=3
        )


# ------------------------------------------
# Scene renderer
# ------------------------------------------

def make_frame(scene_index, frame_number):
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    draw_background(draw, scene_index, frame_number)
    draw_boy(draw, scene_index, frame_number)

    # Top title
    rounded_box(
        draw,
        (25, 25, WIDTH - 25, 85),
        18,
        (20, 25, 45)
    )

    draw_centered_text(
        draw,
        "AUTOTOON AI",
        39,
        TITLE_FONT,
        (255, 220, 70)
    )

    # Story caption
    rounded_box(
        draw,
        (25, 790, WIDTH - 25, 925),
        22,
        (18, 22, 38)
    )

    draw_centered_text(
        draw,
        scenes[scene_index],
        815,
        CAPTION_FONT,
        (255, 255, 255),
        max_width=450
    )

    # Scene number
    scene_label = f"Scene {scene_index + 1}/{SCENE_COUNT}"

    draw.text(
        (WIDTH - 145, 100),
        scene_label,
        font=SMALL_FONT,
        fill=(255, 255, 255),
        stroke_width=2,
        stroke_fill=(25, 25, 40)
    )

    # Progress bar
    progress = (
        (scene_index * SECONDS_PER_SCENE)
        + (frame_number % (FPS * SECONDS_PER_SCENE)) / FPS
    ) / TOTAL_SECONDS

    bar_width = int((WIDTH - 50) * progress)

    draw.rounded_rectangle(
        (25, 945, WIDTH - 25, 955),
        radius=5,
        fill=(60, 60, 75)
    )

    draw.rounded_rectangle(
        (25, 945, 25 + bar_width, 955),
        radius=5,
        fill=(255, 210, 60)
    )

    return np.array(image)


# ------------------------------------------
# Generate video
# ------------------------------------------

def main():
    total_frames = FPS * TOTAL_SECONDS

    print("===================================")
    print("AUTOTOON AI - VIDEO GENERATOR V2")
    print(f"Scenes: {SCENE_COUNT}")
    print(f"Duration: {TOTAL_SECONDS} seconds")
    print(f"FPS: {FPS}")
    print("===================================")

    with imageio.get_writer(
        OUTPUT_FILE,
        fps=FPS,
        codec="libx264",
        quality=7,
        macro_block_size=16,
        ffmpeg_log_level="error"
    ) as writer:

        for frame_number in range(total_frames):
            scene_index = min(
                frame_number // (FPS * SECONDS_PER_SCENE),
                SCENE_COUNT - 1
            )

            frame = make_frame(scene_index, frame_number)
            writer.append_data(frame)

            if frame_number % (FPS * 5) == 0:
                print(
                    f"Rendering: "
                    f"{frame_number / FPS:.0f}/{TOTAL_SECONDS} seconds"
                )

    print("===================================")
    print("VIDEO READY!")
    print(f"Saved to: {OUTPUT_FILE}")
    print(f"Duration: {TOTAL_SECONDS} seconds")
    print("===================================")


if __name__ == "__main__":
    main()
