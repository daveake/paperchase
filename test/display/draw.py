import os
import sys

from PIL import Image, ImageDraw, ImageFont
from papirus import Papirus

WHITE = 1
BLACK = 0

papirus = Papirus()

image = Image.new('1', papirus.size, WHITE)

draw = ImageDraw.Draw(image)

draw.line((0, 0) + papirus.size, fill=0)
draw.line((0, papirus.size[1], papirus.size[0], 0), fill=0)
del draw

papirus.display(image)
papirus.update()

