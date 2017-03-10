import os
import sys

from PIL import Image
from PIL import ImageOps
from papirus import Papirus

papirus = Papirus()

image = Image.open('compass.png')

papirus.display(image)
papirus.update()