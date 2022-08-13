from pygame import Vector2
import pygame
import math


class Vector1:
    def __init__(self, x):
        self.value = x


class Tentacle:
    def __init__(self, length: int, segments_count: int, root_position: pygame.Vector2):
        self.tentacle = pygame.sprite.Group()
        self.tentacle_segments = []
        self.root_position = root_position
        self.segments_count = segments_count

        seg = Segment(self.root_position.x, self.root_position.y, 0, 20)
        self.tentacle.add(seg)
        self.tentacle_segments.append(seg)

        for i in range(1, segments_count):
            seg = Segment(0, (segments_count - i)**1.12, parent_segment=self.tentacle.sprites()[i - 1])
            self.tentacle.add(seg)
            self.tentacle_segments.append(seg)

    def get_length(self) -> int:
        return self.segments_count

    def get_root_position(self) -> pygame.Vector2:
        return self.root_position

    def get_segments(self) -> list['Segment']:
        return self.tentacle_segments


class Segment(pygame.sprite.Sprite):
    len_ = 0

    # TODO: remove arg lists
    def __init__(self, arg, *args, parent_segment: 'Segment(pygame.sprite.Sprite)' = None):
        super().__init__()
        self.angle = Vector1(0)
        self.parent: 'Segment'
        if parent_segment is not None:
            self.parent = parent_segment
            self.a = self.parent.b.copy()
            self.angle.value = arg
            self.len_ = args[0]
        else:
            self.a = Vector2(arg, args[0])
            self.angle.value = args[1]
            self.len_ = args[2]
        self.b = pygame.Vector2()
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
