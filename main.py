import pyaudio
import wave
import librosa
import numpy
import sys
import time
import pygame
import math
from random import randint
from colors import *
from config import *

# system const
CHUNK = 1024
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 22050
RECORD_SECONDS = 0.05
WAVE_OUTPUT_FILENAME = "output.wav"

# init audio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


def get_vol(): # Получение уровня звука
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    audio_data = 'output.wav'
    x, sr = librosa.load(audio_data)
    x = list(x)
    su = 0
    for i in x:
        su += abs(i)


    vol = int(su/len(x)*1000)
    return vol


# создаем игру и окно
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

# загрузка текстур

ball_img = pygame.image.load(PATH_TO_BALL).convert_alpha()
ball_img = pygame.transform.scale(ball_img, (RADIUS*2, RADIUS*2))
background_center = pygame.image.load(PATH_TO_BACK_1).convert()
background_center = pygame.transform.scale(background_center, (WIDTH, HEIGHT-(BOTTOM*2)))
background_bottom = pygame.image.load(PATH_TO_BACK_2).convert()
background_bottom_1 = pygame.transform.scale(background_bottom, (WIDTH, BOTTOM))
wall = pygame.image.load(PATH_TO_BACK_2).convert()


class Wall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x_size = randint(100, 320)
        self.y_size = randint(20, ((HEIGHT-(BOTTOM*2)) / 2))
        self.position_generate = randint(0, 1e6)
        self.image = pygame.transform.scale(wall, (self.x_size, self.y_size))
        self.rect = self.image.get_rect()
        self.rect.centerx = 1980
        if self.position_generate%2 == 0:
            self.rect.centery = int(HEIGHT - (BOTTOM + (self.y_size/2)))
        else:
            self.rect.centery = int(BOTTOM + (self.y_size/2))
    
    def update(self):
        self.rect.centerx -= SPEED
        if self.rect.centerx < -1 * (self.x_size/2):
            self.kill()



counter = 0
last_wall = 0
vol_level = int(HEIGHT/2) + 50

all_walls = pygame.sprite.Group()
last_wall = 0

def new_wall(last_wall):
    if last_wall < randint(40, DELAY_GENERATE_WALL):
        last_wall += 1
    else:
        h = randint(0, 1e5)
        if h%2 == 0:
            new_wall = Wall()
            all_walls.add(new_wall)
            last_wall = 0
        last_wall += 1

    return last_wall

 
while True:
    clock.tick(FPS)

    last_wall = new_wall(last_wall)
    last_vol = vol_level
    vol_level = HEIGHT - ((get_vol()*VOL_ADD_RATE)+25)

    if vol_level > HEIGHT-BOTTOM:
        vol_level = (HEIGHT-BOTTOM) - RADIUS
    elif vol_level < BOTTOM:
        vol_level = BOTTOM+RADIUS

    if vol_level - last_vol < -ANIMATION_RATE:
        vol_level = last_vol - ANIMATION_RATE
    elif vol_level - last_vol > ANIMATION_RATE:
        vol_level = last_vol + ANIMATION_RATE 
    elif abs(vol_level - last_vol) > 0 and abs(vol_level - last_vol) < 12:
        vol_level = last_vol


    screen.fill(WHITE)

    # Фон сверху и снизу
    background_bottom_1_rec = background_bottom_1.get_rect(center=(WIDTH//2, BOTTOM//2))
    screen.blit(background_bottom_1, background_bottom_1_rec) 

    background_bottom_1_rec = background_bottom_1.get_rect(center=(WIDTH//2, HEIGHT - (BOTTOM//2)))
    screen.blit(background_bottom_1, background_bottom_1_rec) 

    #background_bottom_1_rec = background_bottom_1.get_rect(center=(WIDTH - (BOTTOM/2), HEIGHT/2))
    #screen.blit(background_bottom_1, background_bottom_1_rec) 
    
    # Фон в центре
    background_center_rec = background_center.get_rect(center=(int(WIDTH/2), int(HEIGHT/2)))
    screen.blit(background_center, background_center_rec) 

    # Шар
    ball_img_rec = ball_img.get_rect(center=(100, vol_level))
    screen.blit(ball_img, ball_img_rec)
    all_walls.draw(screen)


    # Линии сверху, снизу 
    pygame.draw.line(screen, (123, 123, 123), [0, BOTTOM], [WIDTH, BOTTOM], 3)
    pygame.draw.line(screen, (123, 123, 123), [0, HEIGHT-BOTTOM], [WIDTH, HEIGHT-BOTTOM], 3)

    all_walls.update()
    pygame.display.update()



    for i in pygame.event.get():
        if i.type == pygame.QUIT: exit()

    

