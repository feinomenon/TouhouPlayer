from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import win32api, win32con, win32gui, win32ui

import os
import time

MOVE = {'left': 0x25,
        'up': 0x26,
        'right': 0x27,
        'down': 0x28,
        'shift': 0x10,  # focus
        'esc': 0x1B}

ATK = {'z': 0x5A,      # shoot
       'x': 0x58}      # bomb

def key_press(key):
    win32api.keybd_event(key, 0, 0, 0)
    time.sleep(.01)
    win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

def key_hold(self, key):
    win32api.keybd_event(key, 0, 0, 0)

def key_release(key):
    win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)


class PlayerCharacter(object):
    def __init__(self, hit_x=223, hit_y=397, radius=3):
        self.hit_x = hit_x
        self.hit_y = hit_y
        self.radius = radius

    def move(self, dir):
        for i in range(4):
            key_press(MOVE[dir])
        # TODO: Update own position after moving

    def shift(self, dir):     # Focused movement
        key_hold(MOVE['shift'])
        key_press(MOVE[dir])
        key.key_release(MOVE['shift'])

    def shoot(self):
        key_press(ATK['z'])

    def bomb(self):
        key_press(ATK['x'])


def main():
    time.sleep(3)

    # start the game
    for i in range(5):
        key_press(0x5A)
        time.sleep(1)

    player = PlayerCharacter()
    shoot = LoopingCall(player.shoot)
    move_left = LoopingCall(player.move, 'left')
    bomb_occasionally = LoopingCall(player.bomb)

    shoot.start(0)
    move_left.start(2, False)
    bomb_occasionally.start(10, False)
    reactor.run()

if __name__ == "__main__":
    main()
