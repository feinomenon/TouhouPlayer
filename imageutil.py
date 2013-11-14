from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import win32api, win32con, win32gui, win32ui
import numpy as np
from PIL import Image, ImageChops, ImageOps

import os
import time

# Coordinates for gameplay area
SCAN_AREA = {'x0': 35, 'y0': 42, 'dx': 384, 'dy': 448}

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
        self.x0 = SCAN_AREA['x0']
        self.y0 = SCAN_AREA['y0']
        self.dx = SCAN_AREA['dx']
        self.dy = SCAN_AREA['dy']

        # Center ideally corresponds to character's hitbox
        self.center_x, self.center_y = (center_x, center_y)
        self.dist = 20   # Distance within which to check for hostiles

        # Current image
        self.curr_fov = None
        # Indices of visible objects in fov
        self.object_locs = (np.empty(0), np.empty(0))
        self.blink_time = .03
        self.diff_threhold = 100     # Diffs above this are dangerous

        # self.motion_detector = LoopingCall(self.get_diff)
        # TODO: Call self.scan_fov onnly when self.curr_fov is updated
        self.scanner = LoopingCall(self.scan_fov)

    def update_fov(self):
        """Takes a screenshot and transforms it into a PIL image."""
        # TODO: Only need to record the part we actually examine in scan_fov
        screenshot = take_screenshot(self.x0, self.y0, self.dx, self.dy)
        new_fov = Image.frombuffer("RGBA", (384, 448), screenshot,
                                   "raw", "RGBA", 0, 1)
        self.curr_fov = new_fov
        # self.curr_fov.show()

    def get_diff(self):
        """Takes a new screenshots and compares it with the current one."""
        # time.sleep(.03) # TODO: Make this non-blocking
        old_fov = self.curr_fov
        self.update_fov()
        diff_img = ImageChops.difference(old_fov, self.curr_fov)
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
        fov_array = diff_array[x-dist:x+dist, y-dist:y+dist]

        # Zero out low diff values; get the indices of non-zero values.
        # Is there a simpler way to get indices of values above a threshold?
        fov_array[fov_array < self.diff_threhold] = 0
        object_locs = np.nonzero(fov_array)     # Tuple of np array indices

        # print object_locs
        self.object_locs = object_locs

    def start(self):
        self.curr_img = self.update_fov()
        self.scanner.start(self.blink_time, False)

def main():
    time.sleep(2)   # Quick, switch to the game screen!
    radar = Radar((223, 379))
    reactor.callWhenRunning(radar.start)

    reactor.run()
    # 448 columns x 384 rows
    # diff_array = np.array(diff)
    # Get indices where differences > 100 occur
    # f = lambda x: x > 100
    # list = [(i, filter(f, row)) for i, row in enumerate(diff_array)]
    # print(list)

    # start = time.time()
    # arr = radar.scan_fov()
    # print(arr)
    # print(time.time() - start)

if __name__ == '__main__':
    main()
