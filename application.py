import pygame
import pickle
from pygame._sdl2 import Window
import network
import QuadTree
import random
import flocking
import Tentacle
import perlin
import math


class BoidTexture(pygame.sprite.Sprite):
    def __init__(self, path):
        super().__init__()
        self.orig_image = pygame.image.load(path)
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()


class App:
    def __init__(self, seed: int):
        pygame.init()
        pygame.display.set_caption("Client")
        self.seed = seed
        self.time_millis = 0
        self.width = 700
        self.height = 500
        self.monitor_width = pygame.display.Info().current_w
        self.monitor_height = pygame.display.Info().current_h
        self.screen = pygame.display.set_mode([self.width, self.height], pygame.RESIZABLE)
        self.window_ = Window.from_display_module()  # TODO window position
        self.perlin_gen = perlin.Perlin(self.seed)
        self.perlin_time = 100
        self.quadtree: QuadTree = QuadTree.QuadTree(self.screen.get_rect(), 4)

        self.is_running = False
        self.transmitting_objects: dict[str: network.TransmitObject] = dict()
        self.clock = pygame.time.Clock()
        self.deb_rect = QuadTree.Rectangle(0, 0, self.width // 4, self.height // 4)
        self.delta_time = 0
        self.cursor_pos = pygame.Vector2()

        # self.draw_sprites = pygame.sprite.Group()
        # self.bkg = pygame.image.load("1.jpg")
        self.bkg = pygame.image.load("bkg.jpg")

        self.tentacle_list = []
        # self.tentacle_root = pygame.Vector2(self.width//2, 150)
        self.tentacle = pygame.sprite.Group()
        seg = Tentacle.Segment(250, 250, 0, 20)
        self.tentacle.add(seg)
        self.tentacle_list.append(seg)

        # self.sea_level = self.monitor_height * 2 // 3
        self.sea_level = self.monitor_height

        self.box_1 = network.TransmitObject("box_1", "box.png", pygame.Vector2(250, 150), 0)
        # self.draw_sprites.add(box_1)
        self.transmitting_objects["box_1"] = self.box_1

        for i in range(1, 30):
            seg = Tentacle.Segment(self.tentacle_list[i - 1], 0, (30 - i)**1.12)
            self.tentacle.add(seg)
            self.tentacle_list.append(seg)

        self.segments: list[Tentacle.Segment(pygame.sprite.Sprite)] = self.tentacle.sprites()

        self.boid_textures: list[BoidTexture] = []
        for i in range(60):
            self.boid_textures.append(BoidTexture("fish.png"))

    def transition_update(self, received_list: list[any]):
        """Update data received from the server"""
        self.time_millis = int(received_list[0])
        # print("TIME", self.time_millis)
        for object_ in received_list[1:]:
            if object_["name"] == "tentacle":
                length = len(self.tentacle_list)
                for i in range(length):
                    # print("item", object["segments"][i][0], object["segments"][length - 1 - i][1])
                    self.tentacle_list[i].rect = object_["segments"][length - 1 - i][0]
                    self.tentacle_list[i].angle = object_["segments"][length - 1 - i][1]
                    self.tentacle_list[i].rot_and_scale(i)
                continue
            if object_["name"] == "flock":
                self.quadtree = object_["quadtree"]
                continue
            self.transmitting_objects[object_["name"]].pos_angle_update(object_["pos"], object_["angle"])

    def update(self):
        """Drawing objects and update events"""
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.width = event.w
                self.height = event.h
                # self.monitor_width = pygame.display.Info().current_w NE NADO PLZ ETO RAZMER EKRANA
                # self.monitor_height = pygame.display.Info().current_h
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(self.window_.position)
            if event.type == pygame.MOUSEMOTION:
                self.cursor_pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                self.is_running = False
                pygame.quit()
                return False

        self.screen.fill((0, 0, 0))
        move_x = -self.window_.position[0]
        move_y = -self.window_.position[1]

        self.screen.blit(self.bkg, (move_x, move_y))

        # Drawing sea surface
        move_sea_x = -move_x
        move_sea_y = self.sea_level - self.monitor_height/2 - self.window_.position[1]

        step = 10
        y_1 = self.perlin_gen.get_value(move_sea_x / 500 + self.time_millis * 0.0005) * 100 + move_sea_y
        for x in range(0, self.width + step, step):
            y_2 = self.perlin_gen.get_value((move_sea_x + x) / 500 + self.time_millis * 0.0005) * 100 + move_sea_y
            # pygame.draw.line(self.screen, (255, 255, 255), pygame.Vector2(x - step, y_1),
            #                  pygame.Vector2(x, y_2), width=2)
            y_1 = y_2
            pygame.draw.polygon(self.screen, (50, 135, 220),
                                [(x - step, self.height), (x - step, y_1), (x, y_2), (x, self.height)])

        # Drawing boids
        # boid_counter = 0
        # for boid in self.quadtree.show():
        # print(boid_counter, boid)
        self.quadtree.show(pygame, self.screen, self.boid_textures, move_x, move_y, 0)
        # boid_counter += 1

        # Drawing tentacle
        for i in range(1, len(self.segments)):
            # self.segments[i].set_a(self.segments[i - 1].b, len(self.tentacle) - (i+1))
            # pygame.draw.line(self.screen, (255, 255, 255), self.segments[i].a, self.segments[i].b, width=2)
            self.segments[i].rect = self.segments[i].rect.move(move_x, move_y)
            self.screen.blit(self.segments[i].image, self.segments[i].rect)

        # Drawing box
        # self.screen.blit(self.box_1.image,  self.box_1.rect.move(move_x, move_y))

        pygame.display.flip()
        # print(self.clock.get_fps())
        self.delta_time = self.clock.tick(60)
        self.perlin_time += self.delta_time
        return True

    def get_sending_bytes(self):
        """Stringify global cursor pos and it's status"""
        # print(str(self.cursor_pos) + ' ' + str(int(pygame.mouse.get_focused())))
        cursor = self.cursor_pos + pygame.Vector2(self.window_.position[0], self.window_.position[1])
        return (str(cursor) + ' ' + str(int(pygame.mouse.get_focused())) + ' ' +
                str(int(pygame.mouse.get_pressed()[0]))).encode("utf-8")
