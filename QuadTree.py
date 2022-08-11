import pygame
import math

'''
class Point:
    def __init__(self, x: float, y: float, data):
        self.x = x
        self.y = y
        self.data = data
'''


class Rectangle:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.width_h = width // 2
        self.height_h = height // 2

    def set(self, vec2: pygame.Vector2):
        self.x = vec2.x - self.width_h
        self.y = vec2.y - self.height_h

    def contains(self, point) -> bool:
        return self.x <= point.position.x <= self.x + self.width and self.y <= point.position.y <= self.y + self.height

    def intersects(self, rect: 'Rectangle') -> bool:
        return not (rect.x > self.x + self.width or rect.x + rect.width < self.x or
                    rect.y > self.y + self.height or rect.y + rect.height < self.y)


class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.rSquared = self.r * self.r

    def set(self, vec2: pygame.Vector2, radius):
        self.x = vec2.x
        self.y = vec2.y
        self.r = radius
        self.rSquared = self.r * self.r

    def contains(self, point):
        return (point.position.x - self.x)**2 + (point.position.y - self.y)**2 <= self.rSquared

    def intersects(self, rect: Rectangle):
        width = rect.width // 2
        height = rect.height // 2
        x_dist = abs(rect.x + width - self.x)
        y_dist = abs(rect.y + height - self.y)
        edges = (x_dist - width)**2 + (y_dist - height)**2

        if x_dist > self.r + width or y_dist > self.r + height:
            return False

        if x_dist <= width or y_dist <= height:
            return True

        return edges <= self.rSquared


class QuadTree:
    def __init__(self, boundary: Rectangle, capacity: int):
        self.boundary = boundary
        self.capacity = capacity
        self.northwest: 'QuadTree' = None
        self.northeast: 'QuadTree' = None
        self.southwest: 'QuadTree' = None
        self.southeast: 'QuadTree' = None
        self.points = list()
        self.is_divided = False

    def reset(self, points):
        self.northwest: 'QuadTree' = None
        self.northeast: 'QuadTree' = None
        self.southwest: 'QuadTree' = None
        self.southeast: 'QuadTree' = None
        self.points = list()
        self.is_divided = False
        for point in points:
            self.insert(point)

    def subdivide(self):
        x = self.boundary.x
        y = self.boundary.y
        width = self.boundary.width // 2
        height = self.boundary.height // 2
        nw = Rectangle(x, y + height, width, height)
        self.northwest = QuadTree(nw, self.capacity)
        ne = Rectangle(x + width, y + height, width, height)
        self.northeast = QuadTree(ne, self.capacity)
        sw = Rectangle(x, y, width, height)
        self.southwest = QuadTree(sw, self.capacity)
        se = Rectangle(x + width, y, width, height)
        self.southeast = QuadTree(se, self.capacity)
        self.is_divided = True

    def insert(self, point):
        if not self.boundary.contains(point):
            return False

        if len(self.points) < self.capacity:
            self.points.append(point)
            return True
        else:
            if not self.is_divided:
                self.subdivide()
            return (self.northwest.insert(point) or self.northeast.insert(point) or
                    self.southwest.insert(point) or self.southeast.insert(point))

    def query(self, range_, found):
        if range_.intersects(self.boundary):
            for point in self.points:
                if range_.contains(point):
                    # print("found")
                    found.append(point)
            if self.is_divided:
                self.northwest.query(range_, found)
                self.northeast.query(range_, found)
                self.southwest.query(range_, found)
                self.southeast.query(range_, found)

    def show(self, pygame_: pygame, screen: pygame.Surface, boid_textures, move_x, move_y, boid_counter):
        # pygame_.draw.rect(screen, (255, 255, 255), pygame_.Rect(self.boundary.x, self.boundary.y,
        #                                                         self.boundary.width, self.boundary.height), width=1)

        for boid in self.points:
            boid_texture = boid_textures[boid_counter]
            # print(boid_texture.rect)
            boid_texture.rect.center = boid.position.x + move_x, boid.position.y + move_y
            boid_texture.image = pygame.transform.rotozoom(
                boid_texture.orig_image,  - math.atan2(boid.velocity.y, boid.velocity.x) * 180 / 3.14, 2)
            boid_texture.rect = boid_texture.image.get_rect(center=boid_texture.rect.center)
            # pygame.draw.circle(self.screen, (0, 255, 0), pygame.Vector2(boid.position.x + move_x,
            #                                                             boid.position.y + move_y), 3)
            screen.blit(boid_texture.image, boid_texture.rect)
            boid_counter += 1

        if self.is_divided:
            boid_counter = self.northwest.show(pygame_, screen, boid_textures, move_x, move_y, boid_counter)
            boid_counter = self.northeast.show(pygame_, screen, boid_textures, move_x, move_y, boid_counter)
            boid_counter = self.southwest.show(pygame_, screen, boid_textures, move_x, move_y, boid_counter)
            boid_counter = self.southeast.show(pygame_, screen, boid_textures, move_x, move_y, boid_counter)

        return boid_counter
