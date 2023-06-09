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

RST = 24

disp = Adafruit_SSD1306.SSD1306_128_64(rst=24)

disp.begin()
width = disp.width
height = disp.height

disp.clear()
disp.display()

font = ImageFont.truetype('SamsungOne/SamsungOneKorean-700.ttf', 14)
image = Image.new('1',(width, height))
draw = ImageDraw.Draw(image)

draw.text((5, 7), '현재 습도가 높습니다', font=font, fill=255)

disp.image(image)
disp.display()

