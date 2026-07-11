#!/usr/bin/env python3
"""Overlay a labeled pixel grid so features can be measured by eye."""
import sys
from PIL import Image, ImageDraw, ImageFont
src, dst, step = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 50
im = Image.open(src).convert("RGB")
d = ImageDraw.Draw(im)
W, H = im.size
try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
except Exception:
    f = ImageFont.load_default()
for x in range(0, W, step):
    col = (255, 40, 40) if x % (step*2) == 0 else (255, 160, 160)
    d.line([(x, 0), (x, H)], fill=col, width=1)
    if x % (step*2) == 0:
        d.text((x+2, 2), str(x), fill=(255, 255, 0), font=f)
        d.text((x+2, H-20), str(x), fill=(255, 255, 0), font=f)
for y in range(0, H, step):
    col = (255, 40, 40) if y % (step*2) == 0 else (255, 160, 160)
    d.line([(0, y), (W, y)], fill=col, width=1)
    if y % (step*2) == 0:
        d.text((2, y+2), str(y), fill=(0, 255, 255), font=f)
        d.text((W-46, y+2), str(y), fill=(0, 255, 255), font=f)
im.save(dst)
print("wrote", dst, im.size)
