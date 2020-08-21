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
gg_img = pygame.image.load(PATH_TO_ICO).convert_alpha()
pygame.display.set_icon(gg_img)

# загрузка текстур

ball_img = pygame.image.load(PATH_TO_BALL).convert_alpha()
# ball_img = pygame.transform.scale(ball_img, (RADIUS*2, RADIUS*2))
background_center = pygame.image.load(PATH_TO_BACK_1).convert()
background_center = pygame.transform.scale(background_center, (WIDTH, HEIGHT-(BOTTOM*2)))
background_bottom = pygame.image.load(PATH_TO_BACK_2).convert()
background_bottom_1 = pygame.transform.scale(background_bottom, (WIDTH, BOTTOM))
wall = pygame.image.load(PATH_TO_BACK_2).convert()

bottom_line = pygame.image.load(PATH_TO_BOTTOM).convert()
bottom_line = pygame.transform.scale(bottom_line, (WIDTH, 200))

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

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(ball_img, (RADIUS*2, RADIUS*2))
        self.rect = self.image.get_rect()
        self.rect.centerx = 100
        self.rect.centery = int(HEIGHT/2) + 50
        self.last_vol = HEIGHT - ((get_vol()*VOL_ADD_RATE)+25)
        self.vol_level = HEIGHT - ((get_vol()*VOL_ADD_RATE)+25)

    def update(self):
        self.last_vol = self.vol_level
        self.vol_level = HEIGHT - ((get_vol()*VOL_ADD_RATE)+25)
        print(self.vol_level)

        if self.vol_level > HEIGHT-BOTTOM:
            self.vol_level = (HEIGHT-BOTTOM) - RADIUS
        elif self.vol_level < BOTTOM:
            self.vol_level = BOTTOM+RADIUS

        if self.vol_level - self.last_vol < -ANIMATION_RATE:
            self.vol_level = self.last_vol - ANIMATION_RATE
        elif self.vol_level - self.last_vol > ANIMATION_RATE:
            self.vol_level = self.last_vol + ANIMATION_RATE 
        elif abs(self.vol_level - self.last_vol) > 0 and abs(self.vol_level - self.last_vol) < 12:
            self.vol_level = self.last_vol
        self.rect.centery = self.vol_level




counter = 0
vol_level = int(HEIGHT/2) + 50

top_ball = pygame.sprite.Group()
top_ball.add(Ball())



start_screen = True
game = False
end_game = False
gg = 0

while True:
    clock.tick(FPS)
    if(start_screen == True):
        screen.fill(WHITE)
        for i in pygame.event.get():
            print(i.type)
            print(pygame.K_UP)
            if i.type == 769:
                print("gg")
                gg = 0
                game = True
                end_game = False
                start_screen = False
            elif i.type == pygame.QUIT: exit()    
            
        pygame.display.update()

    elif(game):
        if gg == 0:
            del all_walls
            del top_ball

            all_walls = pygame.sprite.Group()
            top_ball = pygame.sprite.Group()
            top_ball.add(Ball())

        last_wall = new_wall(last_wall)

        screen.fill(WHITE)

        # Фон сверху и снизу
        background_bottom_1_rec = background_bottom_1.get_rect(center=(WIDTH//2, BOTTOM//2))
        screen.blit(background_bottom_1, background_bottom_1_rec) 

        background_bottom_1_rec = background_bottom_1.get_rect(center=(WIDTH//2, HEIGHT - (BOTTOM//2)))
        screen.blit(background_bottom_1, background_bottom_1_rec) 

        bottom_line_rec = bottom_line.get_rect(center=[WIDTH//2, BOTTOM+65])
        screen.blit(bottom_line, bottom_line_rec)
        bottom_line_rec = bottom_line.get_rect(center=[WIDTH//2, (HEIGHT - BOTTOM)+70])
        screen.blit(bottom_line, bottom_line_rec)

        
        # Фон в центре
        background_center_rec = background_center.get_rect(center=(int(WIDTH/2), int(HEIGHT/2)))
        screen.blit(background_center, background_center_rec) 

        all_walls.draw(screen)
        top_ball.draw(screen)
        top_ball.update()
        all_walls.update()

        hits = pygame.sprite.groupcollide(top_ball, all_walls, False, False)
        if hits != {}:
            game = False
            end_game = True
            start_screen = False

        pygame.display.update()
        gg += 1
        for i in pygame.event.get():
            if i.type == pygame.QUIT: exit() 


    elif(end_game):
        screen.fill(WHITE)
        for i in pygame.event.get():
            if i.type == 769:
                gg = 0
                game = True
                end_game = False
                start_screen = False
            elif i.type == pygame.QUIT: exit() 

        pygame.display.update()

