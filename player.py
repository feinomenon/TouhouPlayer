from radar import Radar, GAME_RECT
import numpy as np
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import win32api, win32con, win32gui, win32ui

import random
import os
import time
import logging

logging.basicConfig(filename='thplayer.log', level=logging.DEBUG)

MOVE = {'left': 0x25,   # 2 pixels each movement
        'up': 0x26,
        'right': 0x27,
        'down': 0x28}

MISC = {'shift': 0x10,  # focus
        'esc': 0x1B}

ATK = {'z': 0x5A,      # shoot
       'x': 0x58}      # bomb

# Coordinates of center of hitbox
HIT_X = 192 + GAME_RECT['x0']
HIT_Y = 385 + GAME_RECT['y0']

def key_press(key):
    # TODO: Check with actual position of sprite
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
        # TODO: Need some way of knowing that we've lost a life.

    def move_left(self):
        if self.hit_x > self.bounds['x0'] + self.radar.apothem:
            key_press(MOVE['left'])
            self.hit_x -= 4
            self.radar.center_x -= 4
        else:
            logging.warning("Too far left!")

    def move_right(self):
        if self.hit_x < self.bounds['dx'] - self.radar.apothem:
            key_press(MOVE['right'])
            self.hit_x += 4
            self.radar.center_x += 4
        else:
            logging.warning("Too far right!")

    def move_up(self):
        if self.hit_y > self.bounds['y0'] + self.radar.apothem:
            key_press(MOVE['up'])
            self.hit_y -= 4
            self.radar.center_y -= 4
        else:
            logging.warning("Too far up!")

    def move_down(self):
        if self.hit_y < self.bounds['dy']:   # - self.radar.apothem:
            key_press(MOVE['down'])
            self.hit_y += 4
            self.radar.center_x += 4
        else:
            logging.warning("Too far down!")

    def shift(self, dir):     # Focused movement; probably not necessary
        key_hold(MISC['shift'])
        key_press(MOVE[dir])
        key.key_release(MISC['shift'])

    def shoot(self):
        key_press(ATK['z'])

    def bomb(self):
        key_press(ATK['x'])

    def evade(self):
        h_dists, v_dists = self.radar.obj_dists
        if h_dists.size > 0:
            h_avg = np.average(h_dists)
            v_avg = np.average(v_dists)

            # Move in the direction where the bullets are farthest on average.
            # if v_avg < 15:
            #     self.move_down()
            if h_avg > 0:
                self.move_right()
            elif h_avg < 0:
                self.move_left()

        # else:
        #     # Move toward center when not dodging things
        #     self.move_toward(HIT_X, HIT_Y)

    def move_toward(self, x, y):
        """Bring character closer to (x, y)"""
        if self.hit_x < x:
            self.move_right()
        elif self.hit_x > x:
            self.move_left()

        if self.hit_y < y:
            self.move_down()
        elif self.hit_y > y:
            self.move_up()

    def start(self):
        # self.shoot_constantly = LoopingCall(self.shoot)
        # self.bomb_occasionally = LoopingCall(self.bomb)
        self.evader = LoopingCall(self.evade)

        # self.shoot_constantly.start(0)
        self.evader.start(.3)
        # self.bomb_occasionally.start(10, False)

def start_game():
    time.sleep(2)
    for i in range(5):
        key_press(0x5A)
        time.sleep(1.5)
    time.sleep(3)

def movetest(player):
    for i in range(3):
        player.radar.update_fov()
        player.move_up()
        player.move_up()
        time.sleep(1)

def main():
    start_game()
    radar = Radar((HIT_X, HIT_Y), 50, .03, 90)
    player = PlayerCharacter(radar)
    # movetest(player)

    reactor.callWhenRunning(player.start)
    reactor.callWhenRunning(radar.start)
    reactor.run()

if __name__ == "__main__":
    main()
