import pygame
import os

SOUNDS_DIR = "sounds"


def play_boot():
    pygame.mixer.init()
    sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "boot.mp3"))
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000))


def play_beep():
    pygame.mixer.init()
    sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "beep.mp3"))
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000))


def play_chime():
    pygame.mixer.init()
    sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "chime.mp3"))
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000))


def play_scan():
    pygame.mixer.init()
    sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "scan.wav"))
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000))
