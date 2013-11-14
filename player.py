from imageutil import Radar
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import win32api, win32con, win32gui, win32ui

import random
import os
import time

MOVE = {'left': 0x25,   # 2 pixels each movement
        'up': 0x26,
        'right': 0x27,
        'down': 0x28}

MISC = {'shift': 0x10,  # focus
        'esc': 0x1B}

ATK = {'z': 0x5A,      # shoot
       'x': 0x58}      # bomb

def key_press(key):
    # TODO: Make this non-blocking
    win32api.keybd_event(key, 0, 0, 0)
    # reactor.callLater(.02, win32api.keybd_event,key, 0,
    #                   win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(.02)
    win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

def key_hold(self, key):
    win32api.keybd_event(key, 0, 0, 0)

def key_release(key):
    win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)


class PlayerCharacter(object):
    def __init__(self, hit_x=223, hit_y=397, radius=3, radar=None):
        self.hit_x = hit_x
        self.hit_y = hit_y
        self.radius = radius
        self.width = 62
        self.height = 82    # slight overestimation
        self.radar = radar

    def move_left(self):
        # for i in range(4):
        # TODO: Hitbox should not be allowed to move outside of gameplay area
        key_press(MOVE['left'])
        self.hit_x -= 4

    def move_right(self):
        # for i in range(4):
        key_press(MOVE['right'])
        self.hit_x += 4

    def move_up(self):
        # for i in range(4):
        key_press(MOVE['up'])
        self.hit_y -= 8

    def move_down(self):
        # for i in range(4):
        key_press(MOVE['down'])
        self.hit_y += 8

    def shift(self, dir):     # Focused movement
        key_hold(MISC['shift'])
        key_press(MOVE[dir])
        key.key_release(MISC['shift'])

    def shoot(self):
        key_press(ATK['z'])

    def bomb(self):
        key_press(ATK['x'])

    def evade(self):
        object_locs = self.radar.object_locs
        if object_locs[0].size != 0:
            self.move_down()
            # print(self.hit_x, self.hit_y)

    def start(self):
        self.shoot_constantly = LoopingCall(self.shoot)
        self.bomb_occasionally = LoopingCall(self.bomb)
        self.evader = LoopingCall(self.evade)

        self.shoot_constantly.start(0)
        self.evader.start(.03)
        # self.bomb_occasionally.start(10, False)

def start_game():
    time.sleep(2)
    for i in range(5):
        key_press(0x5A)
        time.sleep(1.5)

def main():
    start_game()
    radar = Radar((223, 379))
    player = PlayerCharacter(radar=radar)

    reactor.callWhenRunning(player.start)
    reactor.callWhenRunning(radar.start)
    reactor.run()

if __name__ == "__main__":
    main()
