import pygame
from pygame import Vector2
import random


def rand_v(width, height):
    return Vector2(random.random() * width, random.random() * height)


def limit(vec2: Vector2, max_val):
    try:
        vec2.scale_to_length(min(vec2.magnitude(), max_val))
    except:
        pass


def dist(x_1, y_1, x_2, y_2):
    return ((x_1 - x_2)**2 + (y_1 - y_2)**2)**.5


class Boid:
    max_force = .007
    max_speed = 30

    def __init__(self, width, height, position: Vector2 = None, velocity: Vector2 = None, acceleration: Vector2 = None):
        self.position: Vector2 = Vector2(0, height/2) + rand_v(width, height/4)
        self.velocity: Vector2 = rand_v(50, 50)
        # print(self.velocity)
        self.acceleration: Vector2 = Vector2()
        self.align_steer = Vector2()
        self.cohesion_steer = Vector2()
        self.separation_steer = Vector2()

    def update(self, delta_time: float):
        # print(self.velocity)
        self.position += self.velocity * delta_time * .01
        self.velocity += self.acceleration * delta_time * .01
        # limit(self.velocity, self.max_speed)
        # limit(self.acceleration, self.max_force)

    def distance(self, boid: 'Boid'):
        return ((self.position.x - boid.position.x)**2 + (self.position.y - boid.position.y)**2)**.5

    def distance_squared(self, boid: 'Boid'):
        return ((self.position.x - boid.position.x)**2 + (self.position.y - boid.position.y)**2)**.5

    def align(self, boids):
        steering = Vector2()
        total = 0
        for other in boids:
            steering += other.velocity
            total += 1
            if total:
                steering /= total
                try:
                    steering.scale_to_length(self.max_speed)
                except:
                    pass
                steering -= self.velocity
                limit(steering, self.max_force)
        return steering

    def separation(self, boids):
        steering = Vector2()
        total = 0
        for other in boids:
            d = dist(self.position.x, self.position.y, other.position.x, other.position.y)
            diff = self.position - other.position
            if d:
                diff /= (d * d)
            steering += diff
            total += 1
        if total:
            steering /= total
            try:
                steering.scale_to_length(self.max_speed)
            except:
                pass
            steering -= self.velocity
            limit(steering, self.max_force)
        return steering

    def cohesion(self, boids):
        steering = Vector2()
        total = 0
        for other in boids:
            steering += other.position
            total += 1
        if total:
            steering /= total
            steering -= self.position
            try:
                steering.scale_to_length(self.max_speed)
            except:
                pass
            steering -= self.velocity
            limit(steering, self.max_force)
        return steering

    def al_co_se(self, boids: list['Boid']):
        """Apply align, cohesion and separation"""
        self.align_steer.xy = 0, 0
        self.cohesion_steer.xy = 0, 0
        self.separation_steer.xy = 0, 0
        counter = 0
        for other in boids:
            # print(other)
            self.align_steer += other.velocity
            self.cohesion_steer += other.position
            dist = self.distance_squared(other)
            if dist:
                self.separation_steer += (self.position - other.position) / (dist * dist)
            else:
                self.separation_steer += (self.position - other.position) * 1
            counter += 1

        if counter:
            # align
            self.align_steer /= counter
            try:
                self.align_steer.scale_to_length(self.max_speed)
            except:
                pass
            self.align_steer -= self.velocity
            limit(self.align_steer, self.max_force)
            # print("align_steer", self.align_steer)
            # cohesion
            self.cohesion_steer /= counter
            # print("cohesion_steer", self.cohesion_steer, self.position)
            self.cohesion_steer -= self.position
            try:
                self.cohesion_steer.scale_to_length(self.max_speed)
            except:
                pass
            self.cohesion_steer -= self.velocity
            limit(self.cohesion_steer, self.max_force)
            # print("cohesion_steer", self.cohesion_steer)
            # separation
            self.separation_steer /= counter
            try:
                self.separation_steer.scale_to_length(self.max_speed)
            except:
                pass
            self.separation_steer -= self.velocity
            limit(self.separation_steer, self.max_force)
            # print("separation_steer", self.separation_steer)
        # print(self.align_steer + self.cohesion_steer + self.separation_steer)
        return self.align_steer + self.cohesion_steer + self.separation_steer

    def edges(self, boundary: pygame.Rect):
        if self.position.x > boundary.x + boundary.width:
            # self.acceleration.x = -self.max_force
            # self.velocity.x = -abs(self.velocity.x)
            self.position.x -= boundary.width
        if self.position.x < boundary.x:
            # self.acceleration.x = self.max_force
            self.position.x += boundary.width
        if self.position.y > boundary.y + boundary.height:
            self.acceleration.y = -self.max_force
            self.velocity.y = -abs(self.velocity.y)
            # self.position.y -= boundary.height
        if self.position.y < boundary.y:
            self.acceleration.y = self.max_force
            self.velocity.y = abs(self.velocity.y)
            # self.position.y += boundary.height


class Flock:
    boids: list[Boid] = list()

    def __init__(self, width: int, height: int):
        self.boundary = pygame.Rect(0, height*3//4, width, height//4)

    def add(self, boid: Boid):
        self.boids.append(boid)

    def update(self, boid: Boid, found_boids_50: list[Boid], found_boids_100: list[Boid], delta_time: float):
        boid.acceleration += boid.al_co_se(found_boids_50)
        # alignment = boid.align(found_boids_50)
        # # print("alignment", alignment)
        # cohesion = boid.cohesion(found_boids_50)
        # # print("cohesion", cohesion)
        # separation = boid.separation(found_boids_100)
        # # print("separation", separation)

        # boid.acceleration += alignment
        # boid.acceleration += cohesion
        # boid.acceleration += separation

        boid.update(delta_time)
        boid.edges(self.boundary)
        boid.acceleration *= 0.99
        # boid.acceleration.xy = 0, 0
        # boid.acceleration = boid.al_co_se(found_boids)
        # boid.update(delta_time)
        # boid.edges(self.boundary)
