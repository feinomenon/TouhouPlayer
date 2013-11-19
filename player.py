from radar import Radar, GAME_RECT
import numpy as np
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import win32api, win32con, win32gui, win32ui

import random
import os
import time
import logging

logging.basicConfig(filename='thplayer.log',level=logging.DEBUG)

MOVE = {'left': 0x25,   # 2 pixels each movement
        'up': 0x26,
        'right': 0x27,
        'down': 0x28}

MISC = {'shift': 0x10,  # focus
        'esc': 0x1B}

ATK = {'z': 0x5A,      # shoot
       'x': 0x58}      # bomb

HIT_X = 192 + GAME_RECT['x0']
HIT_Y = 385 + GAME_RECT['y0']

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
    def __init__(self, radar, hit_x=HIT_X, hit_y=HIT_Y, radius=3):
        self.hit_x = hit_x
        self.hit_y = hit_y
        self.radius = radius
        self.width = 62
        self.height = 82    # slight overestimation
        self.radar = radar
        self.bounds = GAME_RECT
        # TODO: Need some way of knowing that we've hit a wall
        # TODO: Need some way of knowing that we've lost a life.

    def move_left(self):
        if self.hit_x >= self.bounds['x0'] + self.radar.apothem:
            key_press(MOVE['left'])
            self.hit_x -= 4
            self.radar.center_x -= 4

    def move_right(self):
        if self.hit_x <= self.bounds['dx'] - self.radar.apothem:
            key_press(MOVE['right'])
            self.hit_x += 4
            self.radar.center_x += 4

    def move_up(self):
        if self.hit_y >= self.bounds['y0'] + self.radar.apothem:
            key_press(MOVE['up'])
            self.hit_y -= 8
            self.radar.center_y -= 8

    def move_down(self):
        if self.hit_y <= self.bounds['dy'] - self.radar.apothem:
            key_press(MOVE['down'])
            self.hit_y += 8
            self.radar.center_x += 8

    def shift(self, dir):     # Focused movement
        key_hold(MISC['shift'])
        key_press(MOVE[dir])
        key.key_release(MISC['shift'])

    def shoot(self):
        key_press(ATK['z'])

    def bomb(self):
        key_press(ATK['x'])

    def evade(self):
        h_dists, v_dists = self.radar.obj_dists
        h_avg = np.average(h_dists)
        v_avg = np.average(v_dists)

        if h_dists.size > 0:
            if h_avg > 0:
                self.move_right()
            else:
                self.move_left()

            if v_avg > 0:
                self.move_up()
            else:
                self.move_down()
        else:
            self.move_to(HIT_X, HIT_Y)

    def move_to(self, x, y):
        """Bring character to (x, y)"""
        pass

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
    radar = Radar((HIT_X, HIT_Y))
    player = PlayerCharacter(radar)

    reactor.callWhenRunning(player.start)
    reactor.callWhenRunning(radar.start)
    reactor.run()

if __name__ == "__main__":
    main()
