import win32api, win32con, win32gui, win32ui
import numpy as np
from PIL import Image, ImageChops, ImageOps

import os
import time
import pdb

def take_screenshot(x0, y0, dx, dy):
    """
    Takes a screenshot of the region of the active window starting from
    (x0, y0) with width dx and height dy.
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

class Radar(object):
    def __init__(self, (center_x, center_y)):
        self.x0 = 35    # Coordinates for gameplay area
        self.y0 = 42
        self.dx = 384
        self.dy = 448

        # Center ideally corresponds to character's hitbox
        self.center_x, self.center_y = (center_x, center_y)
        self.dist = 100   # Distance within which to check for hostiles

    def screenshot_img(self):
        # TODO: Take screenshot only of the current fov
        """Takes a screenshot and transforms it into a PIL image."""
        screenshot = take_screenshot(self.x0, self.y0, self.dx, self.dy)
        new_img = Image.frombuffer("RGBA", (384, 448), screenshot,
                                   "raw", "RGBA", 0, 1)
        # new_img.show()
        return new_img

    def get_diff(self):
        """Takes two screenshots and gets their difference in grayscale."""
        img1 = self.screenshot_img()
        time.sleep(.03) # TODO: Make this non-blocking
        img2 = self.screenshot_img()
        diff_img = ImageChops.difference(img1, img2)
        # Maybe don't need grayscale?
        # diff_img.show()
        return ImageOps.grayscale(diff_img)

    def scan_fov(self):
        """
        Returns the indices (in terms of the current fov) of pixels where
        there are objects.
        """
        diff_array = np.array(self.get_diff())

        # Get the slice of the array representing the fov
        # NumPy indexing: array[rows, cols]
        x = self.center_x
        y = self.center_y
        dist = self.dist
        # fov_array[0, 0] = diff_array[x, y]
        fov_array = diff_array[x - dist:x + dist,
                               y:y + dist]

        # Zero out diff values under 50; get the indices of non-zero values.
        # Is there a simpler way to get indices of values above a threshold?
        fov_array[fov_array < 60] = 0
        return np.nonzero(fov_array)

def main():
    time.sleep(2)   # Quick, switch to the game screen!
    radar = Radar((223, 379))

    # 448 columns x 384 rows
    # diff_array = np.array(diff)
    # Get indices where differences > 100 occur
    # f = lambda x: x > 100
    # list = [(i, filter(f, row)) for i, row in enumerate(diff_array)]
    # print(list)

    start = time.time()
    arr = radar.scan_fov()
    print(arr)
    print(time.time() - start)

if __name__ == '__main__':
    main()
