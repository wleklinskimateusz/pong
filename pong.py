import pygame
import os
import random

from vectors import *

pygame.font.init()

WIN_HEIGHT = 600
WIN_WIDTH = 800
MARGIN = 30

def load_file(name):
    return pygame.image.load(os.path.join("imgs", name + ".png"))





class Platform:
    IMG = load_file("platform")
    LENGTH = 50
    MARGIN = 30

    def __init__(self, place=None):
        self.position = Vector(MARGIN, WIN_HEIGHT/2)
        self.velocity = Velocity(0, 0)
        if place:
            self.player_wasd = True
        else:
            self.player_wasd = False
            self.position.x = WIN_WIDTH - MARGIN - self.IMG.get_width()

    def draw(self, win):
        win.blit(self.IMG, (self.position.x, self.position.y))

    def update(self):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

        if self.position.x > WIN_WIDTH:
            self.position.x = WIN_WIDTH
        if self.position.x < 0:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = 0
        if self.position.y > WIN_HEIGHT - self.IMG.get_height():
            self.position.y = WIN_HEIGHT - self.IMG.get_height()

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)



class Pong:
    IMG = load_file('pong')

    def __init__(self):
        self.position = None
        self.velocity = None
        self.reset()

    def reset(self):
        self.position = Vector(WIN_WIDTH / 2, WIN_HEIGHT / 2)
        self.velocity = Velocity(random.randint(-7, 7), random.randint(-7, 7))
        if abs(self.velocity.x) < 3:
            self.reset()

    def draw(self, win):
        win.blit(self.IMG, (self.position.x, self.position.y))

    def update(self):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

        if self.position.x > WIN_WIDTH - self.IMG.get_width() or self.position.x < 0:
            self.reset()

        if self.position.y < 0 or self.position.y > WIN_HEIGHT - self.IMG.get_height():
            self.position.y - WIN_HEIGHT - self.IMG.get_height()
            self.velocity.change_y_direction()

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)

    def collide(self, platform):
        offset = (round(self.position.x) - round(platform.position.x), round(self.position.y) - round(platform.position.y))
        collision_point = platform.get_mask().overlap(self.get_mask(), offset)

        if collision_point:
            return True
        return False

    def passed(self, platform):
        if self.position.x < MARGIN + platform.IMG.get_width() - self.IMG.get_width()/2 or self.position.x > WIN_WIDTH - MARGIN - platform.IMG.get_width() -self.IMG.get_width() / 2:
            return True
        else:
            return False




class Game:
    WIDTH = WIN_WIDTH
    HEIGHT = WIN_HEIGHT

    BG = load_file("bg")

    STAT_FONT = pygame.font.SysFont("comicsans", 50)
    MID_FONT = pygame.font.SysFont("comicsans", 75)
    LARGE_FONT = pygame.font.SysFont("comicsans", 100)
    TICK = 30

    def __init__(self):
        self.mainloop = False

        self.win = None
        self.clock = None

        self.platforms = []
        self.pong = None

    def create_platforms(self):
        platform1 = Platform("wasd")

        platform2 = Platform()
        self.platforms.append(platform1)
        self.platforms.append(platform2)


    def setup(self):
        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()

        self.create_platforms()
        self.pong = Pong()

    def update(self):
        for platform in self.platforms:
            platform.update()
        self.pong.update()

        for platform in self.platforms:
            if self.pong.collide(platform):
                self.pong.velocity.y += platform.velocity.y
                if not self.pong.passed(platform):
                    self.pong.velocity.change_x_direction()
                    self.pong.velocity.change_magnitude()
                else:
                    self.pong.velocity.change_y_direction()
                    self.pong.position.reset()


    def main(self):

        self.setup()
        self.mainloop = True

        while self.mainloop:
            self.clock.tick(self.TICK)

            self.check_events()
            self.draw_windows()

            self.update()

    def left_player(self):
        for player in self.platforms:
            if player.player_wasd:
                return player

    def right_player(self):
        for player in self.platforms:
            if not player.player_wasd:
                return player

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    self.run_loop = False
                    pygame.quit()
                    quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.left_player().velocity.y = -10
                if event.key == pygame.K_s:
                    self.left_player().velocity.y = 10

                if event.key == pygame.K_UP:
                    self.right_player().velocity.y = -10
                if event.key == pygame.K_DOWN:
                    self.right_player().velocity.y = 10

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    self.left_player().velocity.y = 0


                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.right_player().velocity.y = 0


    def draw_windows(self):

        self.win.blit(self.BG, (0, 0))

        for platform in self.platforms:
            platform.draw(self.win)
        self.pong.draw(self.win)

        pygame.display.update()

Game().main()
