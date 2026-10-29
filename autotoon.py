import os
import math
import textwrap
import numpy as np
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 540, 960, 12
OUTPUT = "output/autotoon_short.mp4"

story = os.environ.get("STORY", "").strip()
if story:
    scenes = [s.strip() for s in story.splitlines() if s.strip()]
else:
    scenes = [
        "Chintu ne gaon mein chai ki dukaan kholi!",
        "Customer bola: Chai mein cheeni kam hai!",
        "Chintu bola: Paise bhi toh kam diye hain!",
        "Customer chup... sab hans pade!"
    ]

def font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_scene(text, scene, frame):
    im = Image.new("RGB", (W, H), (255, 220, 160))
    d = ImageDraw.Draw(im)

    # Village background
    d.rectangle((0, 560, W, H), fill=(110, 175, 95))
    d.ellipse((420, 70, 490, 140), fill=(255, 185, 45))

    # Village houses
    for x, color in [(25, (235, 145, 90)), (380, (240, 195, 115))]:
        d.rectangle((x, 390, x+130, 560), fill=color,
                    outline=(90, 55, 35), width=4)
        d.polygon([(x-12, 395), (x+65, 320), (x+142, 395)],
                  fill=(150, 60, 48))
        d.rectangle((x+45, 465, x+85, 560), fill=(105, 65, 40))

    # Tea stall
    d.rectangle((145, 500, 395, 595), fill=(125, 75, 42))
    d.rectangle((165, 460, 375, 505), fill=(255, 245, 210))
    d.text((270, 480), "CHAI CORNER", font=font(19),
           fill=(100, 45, 30), anchor="mm")

    # Cartoon character
    cx, cy = 270, 300 + int(5 * math.sin(frame / 3))
    d.ellipse((cx-48, cy-55, cx+48, cy+45),
              fill=(205, 145, 95), outline=(65, 40, 25), width=4)
    d.pieslice((cx-50, cy-70, cx+50, cy+15),
               180, 360, fill=(40, 28, 22))
    d.ellipse((cx-26, cy-15, cx-10, cy+3), fill="white")
    d.ellipse((cx+10, cy-15, cx+26, cy+3), fill="white")
    d.ellipse((cx-20, cy-10, cx-12, cy+1), fill="black")
    d.ellipse((cx+12, cy-10, cx+20, cy+1), fill="black")
    d.arc((cx-20, cy-2, cx+20, cy+28), 0, 180,
          fill=(70, 25, 20), width=4)
    d.rectangle((cx-15, cy+40, cx+15, cy+65),
                fill=(195, 130, 85))
    d.ellipse((cx-58, cy+50, cx+58, cy+180),
              fill=(40, 110, 180), outline=(30, 45, 60), width=4)

    # Story caption
    d.rounded_rectangle((25, 690, 515, 860), radius=25,
                        fill=(255, 255, 245),
                        outline=(75, 55, 40), width=4)
    lines = textwrap.wrap(text, width=27)[:3]
    for i, line in enumerate(lines):
        d.text((270, 775 + (i-(len(lines)-1)/2)*42),
               line, font=font(27), fill=(40, 40, 40), anchor="mm")

    d.rounded_rectangle((25, 25, 515, 90), radius=20,
                        fill=(125, 45, 35))
    d.text((270, 57), "GAON KI COMEDY",
           font=font(30), fill=(255, 245, 210), anchor="mm")
    d.text((270, 920), f"Scene {scene+1}/{len(scenes)}",
           font=font(19), fill=(30, 55, 25), anchor="mm")

    return np.asarray(im)

def main():
    os.makedirs("output", exist_ok=True)
    with imageio.get_writer(
        OUTPUT, fps=FPS, codec="libx264",
        quality=7, macro_block_size=2
    ) as video:
        for i, caption in enumerate(scenes):
            for frame in range(FPS * 3):
                video.append_data(draw_scene(caption, i, frame))
    print("Video ready:", OUTPUT)

if __name__ == "__main__":
    main()
