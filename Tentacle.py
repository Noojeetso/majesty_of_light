from pygame import Vector2
import pygame
import math


class Vector1:
    def __init__(self, x):
        self.value = x


class Segment(pygame.sprite.Sprite):
    len_ = 0

    def __init__(self, arg, *args):
        super().__init__()
        self.angle = Vector1(0)
        self.parent: 'Segment'
        if isinstance(arg, Segment):
            self.parent = arg
            self.a = arg.b.copy()
            self.angle.value = args[0]
            self.len_ = args[1]
        else:
            self.a = Vector2(arg, args[0])
            self.angle.value = args[1]
            self.len_ = args[2]
        self.calculate_b()
        self.orig_image = pygame.image.load("seg.png")
        self.image = pygame.image.load("seg.png")
        self.rect = self.orig_image.get_rect()
        self.rect.center = ((self.a + self.b)/2).xy

    def calculate_b(self):
        dx = self.len_ * math.cos(self.angle.value)
        dy = self.len_ * math.sin(self.angle.value)
        self.b = self.a + Vector2(dx, dy)

    def set_a(self, vec2: Vector2, number):
        self.a = vec2.copy()
        self.update(number)

    def update(self, number):
        self.calculate_b()
        self.rect.center = ((self.a + self.b)/2).xy
        # self.rot_and_scale(number)

    def follow(self, x, y, id_):
        target = Vector2(x, y)
        direction = target - self.a
        self.angle.value = math.atan2(direction.y, direction.x)
        # if id_ == 1:
        #     print("angle.value",  x, y, direction, self.angle.value)
        direction.scale_to_length(self.len_)
        direction *= -1
        self.a = target + direction

    def rot_and_scale(self, number):
        """rotate an image while keeping its center"""
        # pygame.transform.scale(self.orig_image, (15, 50), dest_surface=self.image)
        self.image = pygame.transform.rotozoom(self.orig_image, 90-self.angle.value*180/3.14, number * 2 / 10)
        self.rect = self.image.get_rect(center=self.rect.center)
