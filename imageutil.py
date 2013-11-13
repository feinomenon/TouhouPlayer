import player

import win32api, win32con, win32gui, win32ui
import numpy as np
from PIL import Image, ImageChops, ImageOps

import os
import time
import pdb

def take_screenshot(x0, y0, dx, dy):
    """
    Takes a screenshot of the region of the active window starting from
    (x0, xy) with width dx and height dy.
    """
    hwnd = win32gui.GetForegroundWindow()   # Window handle
    wDC = win32gui.GetWindowDC(hwnd)        # Window device context
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()

    dataBitMap = win32ui.CreateBitmap()     # PyHandle object
    dataBitMap.CreateCompatibleBitmap(dcObj, dx, dy)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(dx, dy) , dcObj, (x0, y0), win32con.SRCCOPY)
    image = dataBitMap.GetBitmapBits(1)

    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)

    return image

# TODO: Turn this into a class
class Radar(object):
    def __init__(self):
        self.x0 = 35    # Coordinates for gameplay area
        self.y0 = 42
        self.dx = 384
        self.dy = 448
        self.cur_img = None

        self.fov = 50   # Radius within which to check for hostile objects

    def screenshot_img(self):
        """Takes a screenshot and transforms it into a PIL image."""
        screenshot = take_screenshot(self.x0, self.y0, self.dx, self.dy)
        new_img = Image.frombuffer("RGBA", (384, 448), screenshot,
                                   "raw", "RGBA", 0, 1)
        # new_img.show()
        return new_img

    def find_diff(self, orig_img):
        new_img = self.screenshot_img()
        diff_img = ImageChops.difference(orig_img, new_img)
        # diff_img.show()
        return ImageOps.grayscale(diff_img)

def main():
    time.sleep(1)   # Quick, switch to the game screen!
    radar = Radar()
    img1 = radar.screenshot_img()
    time.sleep(.03)
    diff = radar.find_diff(img1)
    diff.show()

if __name__ == '__main__':
    main()
