#
# oled.py
# Wireless Network Term Project
#
# Created by IT DICE on 2023/06/05.
#
import time
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

display = Adafruit_SSD1306.SSD1306_128_64(rst=24)

display.begin()
width = display.width
height = display.height

display.clear()
display.display()

font = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 15)
image = Image.new('1',(width, height))
draw = ImageDraw.Draw(image)

draw.text((100, 100), 'TEST OLED', font=font, fill=255)

display.image(image)
display.display()
time.sleep(3)

