import win32api, win32con, win32gui, win32ui
import numpy as np
from PIL import Image, ImageChops, ImageOps
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import os
import time
import logging

logging.basicConfig(filename='radar.log',level=logging.DEBUG)

# Coordinates for gameplay area
GAME_RECT = {'x0': 35, 'y0': 42, 'dx': 384, 'dy': 448}

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

    return Image.frombuffer("RGBA", (384, 448), image, "raw", "RGBA", 0, 1)

class Radar(object):
    def __init__(self, (hit_x, hit_y), apothem, blink_time, diff_threshold):
        self.x0 = GAME_RECT['x0']
        self.y0 = GAME_RECT['y0']
        self.dx = GAME_RECT['dx']
        self.dy = GAME_RECT['dy']

        # TODO: Keep updating center to match character's hitbox
        self.center_x, self.center_y = (hit_x, hit_y)

        self.apothem = apothem    # Distance within which to check for hostiles
        self.curr_fov = take_screenshot(self.x0, self.y0, self.dx, self.dy)
        self.obj_dists = (np.empty(0), np.empty(0))  # distances of objects in fov
        self.blink_time = blink_time           # Pause between screenshots
        self.diff_threhold = diff_threshold    # Diffs above this are dangerous

        # TODO: Call self.scan_fov only when self.curr_fov is updated
        self.scanner = LoopingCall(self.scan_fov)

    def update_fov(self):
        """Takes a screenshot and makes it the current fov."""
        # TODO: Only need to record the part we actually examine in scan_fov
        self.curr_fov = take_screenshot(self.x0, self.y0, self.dx, self.dy)
        # self.curr_fov.show()

    def get_diff(self):
        """Takes a new screenshots and compares it with the current one."""
        # time.sleep(.03) # TODO: Make this non-blocking
        old_fov = self.curr_fov
        # old_fov.show()
        self.update_fov()
        # self.curr_fov.show()
        diff_img = ImageChops.difference(old_fov, self.curr_fov)
        # diff_img.show()
        return ImageOps.grayscale(diff_img)

    def scan_fov(self):
        """
        Updates self.object_locs with a NumPy array of (x, y) coordinates
        (in terms of the current fov) of detected objects.
        """
        diff_ar = np.array(self.get_diff())

        # Get the slice of the array representing the fov
        # NumPy indexing: array[rows, cols]
        # x = self.center_x
        # y = self.center_y

        # Look at front, left, and right of hitbox
        # Note: fov_ar is a view of diff_ar that gets its own set of indices starting at 0,0
        fov_ar = diff_ar[self.center_x-self.apothem:self.center_x+self.apothem,
                         self.center_y-self.apothem:self.center_y]

        # TODO: Give this a better name, since it's not the vertical center of the array
        fov_center = (fov_ar[:,0].size-1, fov_ar[0,:].size/2)
        # Zero out low diff values.
        fov_ar[fov_ar < self.diff_threhold] = 0
        # Get the indices of non-zero values.
        obj_locs = np.transpose(np.nonzero(fov_ar))
        # logging.debug(fov_ar)
        # logging.debug(obj_locs)

        # Update self.obj_dists with distances of currently visible objects
        if obj_locs.size > 0:
            self.obj_dists = self.get_distance(obj_locs, fov_center)
        else:
            self.obj_dists = (np.empty(0), np.empty(0))

    def get_distance(self, locs, reference):
        """Get average horizontal and vertical distances of objects in fov as a pair
        of NumPy arrays."""
        h_dists = (locs[:, 0] - reference[0])
        v_dists = (locs[:, 1] - reference[1])
        return (h_dists, v_dists)

    def start(self):
        self.curr_img = self.update_fov()
        self.scanner.start(self.blink_time, False)

def main():
    radar = Radar((192 + GAME_RECT['x0'], 385 + GAME_RECT['y0']))
    reactor.callWhenRunning(radar.start)
    reactor.run()

    # start = time.time()
    # radar.start()
    # arr = radar.scan_fov()
    # # print(arr)
    # print(time.time() - start)

if __name__ == '__main__':
    main()
