import pygame
import os
import random
import neat

from vectors import *

pygame.font.init()

WIN_HEIGHT = 600
WIN_WIDTH = 800
MARGIN = 30
SPEED = 20

def load_file(name):
    return pygame.image.load(os.path.join("imgs", name + ".png"))


class Platform:
    IMG = load_file("platform")
    LENGTH = 50
    MARGIN = 30

    def __init__(self, place=None):
        self.position = Vector(MARGIN, WIN_HEIGHT/2)
        self.velocity = Velocity(0, 0)
        self.up = False
        self.down = False

        if place:
            self.player_wasd = True
        else:
            self.right()

    def left(self):
        self.player_wasd = True
        self.position = Vector(MARGIN, WIN_HEIGHT/2)

    def right(self):
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

    def go_up(self):
        self.up = True
        self.velocity.y = -SPEED
        # print("up")

    def go_down(self):
        self.down = True
        self.velocity.y = SPEED

    def not_up(self):
        self.up = False
        self.velocity.y = 0

    def not_down(self):
        self.down = False
        self.velocity.y = 0


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

    def update(self, game):
        self.position += self.velocity

        if abs(self.velocity.y) > 50:
            self.velocity.y /= 2

        if self.position.x > WIN_WIDTH - self.IMG.get_width() or self.position.x < 0:
            self.reset()
            game.score = 0

            if game.AI:
                game.ge[game.counter].fitness -= 10
                game.ge[game.counter+1].fitness -= 10
                game.counter += 1
                print(game.counter)

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

        self.score = 0

        self.AI = False

        self.nets =[]
        self.ge =[]
        self.bots = []

        self.generation = 0

        self.config = None
        self.counter = 0

        self.left = None
        self.right = None

        self.population = None

    def create_platforms(self, genome=None):
        if not genome:
            platform1 = Platform("wasd")

            platform2 = Platform()
            self.platforms.append(platform1)
            self.platforms.append(platform2)



    def setup(self, genome=None):
        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()


        self.pong = Pong()
        self.score = 0
        self.nets = []
        self.ge = []
        self.bots = []
        self.counter = 0

        if genome:
            self.AI = True
            self.generation += 1
            for _, g in genome:
                net = neat.nn.FeedForwardNetwork.create(g, self.config)
                self.nets.append(net)
                self.bots.append(Platform())
                g.fitness = 0
                self.ge.append(g)
            self.left = self.bots[0]

            self.right = self.bots[1]

            self.population = len(self.bots)
        self.create_platforms(genome)


    def update(self):

        self.left.left()

        self.right.right()

        for i, bot in enumerate(self.bots):
            if self.left == bot:
                other = self.right
            else:
                other = self.left
            self.decide_how_move(i, bot, other)
            # print(bot.velocity)


        for platform in self.platforms:
            platform.update()
        self.pong.update(self)

        if self.counter > len(self.bots)-2:
            self.mainloop = False


        if self.AI and self.mainloop:
            self.left = self.bots[self.counter]
            self.right = self.bots[self.counter+1]
            self.platforms = [self.left, self.right]



        for platform in self.platforms:
            if self.pong.collide(platform):
                self.pong.velocity += platform.velocity
                if not self.pong.passed(platform):
                    self.pong.velocity.change_x_direction()
                    self.pong.velocity.change_magnitude()
                    self.score += 1
                    if self.AI:
                        self.ge[self.counter].fitness += 10
                        self.ge[self.counter+1].fitness += 10
                else:
                    self.pong.velocity.change_y_direction()
                    self.pong.position.reset()
                    self.score = 0
                    print(self.AI)
                    if self.AI:
                        self.ge[self.counter].fitness -= 10
                        self.ge[self.counter+1].fitness -= 10
                        self.counter += 1
                        print(self.counter)
        # print(self.counter)



    def decide_how_move(self, x, bot, other):
        output = self.nets[x].activate((bot.position.y,
                                        bot.position.x,
                                        other.position.y,
                                        other.position.x,
                                        self.pong.position.x,
                                        self.pong.position.y
                                        ))
        #print(output)
        if output[0] > 0.5:
            bot.velocity.y += 5
        # else:
        #     bot.velocity.y = 0

        if output[1] < 0.5:
            #print("hello")
            bot.velocity.y += -5
        # else:
        #     bot.velocity.y = 0





    def main(self, genome=None, config=None):
        self.setup(genome)
        print(self.AI)
        self.mainloop = True

        while self.mainloop:
            # self.clock.tick(self.TICK)

            self.check_events()
            self.draw_window()

            self.update()
        print("end")

    def AI_run(self):
        self.AI = True
        self.generation = 0
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config-feedforward.txt")

        self.config = neat.config.Config(
                                neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path
        )
        p = neat.Population(self.config)
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        self.winner = p.run(self.main, 50)


    def left_player(self):
        for player in self.platforms:
            if player.player_wasd:
                return player

    def right_player(self):
        for player in self.platforms:
            if not player.player_wasd:
                return player

    def check_events(self):
        left = self.left_player()
        right = self.right_player()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    self.run_loop = False
                    pygame.quit()
                    quit()
            if event.type == pygame.KEYDOWN and not self.AI:
                if event.key == pygame.K_w and not left.down:
                    left.go_up()
                if event.key == pygame.K_s and not left.up:
                    left.go_down()

                if event.key == pygame.K_UP and not right.down:
                    right.go_up()
                if event.key == pygame.K_DOWN and not right.up:
                    right.go_down()

            if event.type == pygame.KEYUP and not self.AI:
                if event.key == pygame.K_w:
                    left.not_up()

                if event.key == pygame.K_s:
                    left.not_down()


                if event.key == pygame.K_UP:
                    right.not_up()

                if event.key == pygame.K_DOWN:
                    right.not_down()


    def draw_window(self):

        self.win.blit(self.BG, (0, 0))

        for platform in self.platforms:
            platform.draw(self.win)


        self.pong.draw(self.win)

        text = self.STAT_FONT.render("Score: " + str(self.score), 1, (255, 255, 255))
        self.win.blit(text, (self.WIDTH - 10 - text.get_width(), 10))

        pygame.display.update()

Game().AI_run()
