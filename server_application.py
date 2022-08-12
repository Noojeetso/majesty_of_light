import pickle
import pygame
import network
import QuadTree
import flocking
import Tentacle


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Server")
        self.monitor_width = pygame.display.Info().current_w
        self.monitor_height = pygame.display.Info().current_h
        self.width = self.monitor_width
        self.height = self.monitor_height
        self.is_running = False
        self.transmitting_objects: dict[{str: network.TransmitObject}] = dict()
        self.clock = pygame.time.Clock()
        self.delta_time = 0
        self.cursor_pos = pygame.Vector2(self.width / 2, self.height / 2)
        self.was_pressed = False
        self.is_pressed = False
        self.in_focus = False

        # Initializing QuadTree
        self.boundary = QuadTree.Rectangle(0, 0, self.width, self.height)
        self.quadtree = QuadTree.QuadTree(self.boundary, 4)
        qtree = network.TransmitObject("flock", self.quadtree)
        self.transmitting_objects.update({"flock": qtree})

        self.circle = QuadTree.Circle(0, 0, 40)
        self.rect = QuadTree.Rectangle(0, 0, 40, 40)

        # Initializing Flock
        self.flock = flocking.Flock(self.width, self.height)
        for i in range(30):
            self.flock.add(flocking.Boid(self.width, self.height))
        self.dragged_boid: flocking.Boid = None

        # Initializing tentacle
        self.tentacle_root = pygame.Vector2(self.width//2, self.height + 100)
        self.tentacle = pygame.sprite.Group()
        self.tentacle_list = []
        seg = Tentacle.Segment(250, 250, 0, 20)
        self.tentacle.add(seg)
        self.tentacle_list.append(seg)

        for i in range(1, 30):
            seg = Tentacle.Segment(self.tentacle.sprites()[i - 1], 0, (30 - i)**1.12)
            self.tentacle.add(seg)
            self.tentacle_list.append(seg)

        # Initializing box
        box_1 = network.TransmitObject("box_1", "box.png", pygame.Vector2(250, 150), 0)
        self.transmitting_objects.update({"box_1": box_1})

        print("tentacle_list", self.tentacle_list)
        segs = network.TransmitObject("tentacle", self.tentacle_list)
        self.transmitting_objects.update({"tentacle": segs})

        self.segments: list[Tentacle.Segment(pygame.sprite.Sprite)] = self.tentacle.sprites()
        print("transmitting_objects", self.transmitting_objects)

    def update_events_and_positions(self):
        self.update_events()
        self.update_positions()
        # self.update_box_position()
        # print(self.clock.get_fps())
        self.delta_time = self.clock.tick(60)

    def update_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                pygame.quit()
                return

    def update_positions(self):
        self.update_tentacle_position()
        self.update_quadtree()
        self.update_boids_positions()

    def update_tentacle_position(self):
        self.segments[-1].follow(self.cursor_pos.x, self.cursor_pos.y, 1)
        self.segments[-1].update(len(self.tentacle))

        for i in range(len(self.tentacle)-2, -1, -1):
            self.segments[i].follow(self.segments[i + 1].a.x, self.segments[i + 1].a.y, 0)
            self.segments[i].update(len(self.tentacle) - (i+1))

        self.segments[0].set_a(self.tentacle_root, len(self.tentacle))
        for i in range(1, len(self.segments)):
            self.segments[i].set_a(self.segments[i - 1].b, len(self.tentacle) - (i+1))

    def update_quadtree(self):
        self.quadtree.reset(self.flock.boids)
        if self.in_focus:
            self.update_mouse_drag()

    def update_mouse_drag(self):
        if self.is_pressed:
            if not self.was_pressed:
                found_boids = []
                self.circle.set(self.segments[-1].a, 10)
                self.quadtree.query(self.circle, found_boids)
                if found_boids:
                    self.dragged_boid = found_boids[0]
                self.was_pressed = True
            elif self.dragged_boid is not None:
                self.dragged_boid.position = self.segments[-1].a
        else:
            self.dragged_boid = None
            self.was_pressed = False

    def update_boids_positions(self):
        for boid in self.flock.boids:
            found_boids_50 = []
            self.circle.set(boid.position, 100)
            self.quadtree.query(self.circle, found_boids_50)
            # print(found_boids_50)
            found_boids_100 = []
            # self.circle.set(boid.position, 0)
            # self.quadtree.query(self.circle, found_boids_100)
            self.flock.update(boid, found_boids_50, found_boids_100, self.delta_time)

    def update_box_position(self):
        self.transmitting_objects["box_1"].pos_angle_update(self.cursor_pos, 0)

    def get_sending_bytes(self, time_in_millis: int):
        # print("Here1", [value.data for key, value in self.transmitting_objects.items()])
        # print(len(pickle.dumps([time] + [object_.data for object_ in self.transmitting_objects.values()])))
        # return pickle.dumps([round(time.time() * 1000)] +
        #                     [object_.data for object_ in self.transmitting_objects.values()])
        return pickle.dumps([time_in_millis] + [object_.data for object_ in self.transmitting_objects.values()])
