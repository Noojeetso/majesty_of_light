import pygame
from pygame._sdl2 import Window
import network
import QuadTree
import Tentacle
import perlin


class BoidTexture(pygame.sprite.Sprite):
    def __init__(self, path):
        super().__init__()
        self.orig_image = pygame.image.load(path)
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()


class ScreenProperties:
    def __init__(self, window_width, window_height):
        self.width = window_width
        self.height = window_height
        self.monitor_width = pygame.display.Info().current_w
        self.monitor_height = pygame.display.Info().current_h
        self.screen = pygame.display.set_mode([self.width, self.height], pygame.RESIZABLE)
        self.window_ = Window.from_display_module()

    def get_window_x(self):
        return self.window_.position[0]

    def get_window_y(self):
        return self.window_.position[1]


class Translation:
    x = 0
    y = 0

    def set_vector(self, x, y):
        self.x = x
        self.y = y


class Sea:
    perlin_time = 100

    def __init__(self, seed, monitor_height):
        self.perlin_gen = perlin.Perlin(seed)
        # self.level = self.monitor_height * 2 // 3
        self.level = monitor_height


# class CurrentState:
#     time_seconds = 0
#     delta_time = 0
#     cursor_pos = pygame.Vector2()


class App:
    def __init__(self, seed: int):
        pygame.init()
        pygame.display.set_caption("Client")
        self.seed = seed
        self.time_seconds = 0
        self.delta_time = 0
        self.cursor_pos = pygame.Vector2()

        self.screen_properties = ScreenProperties(700, 500)

        self.is_running = False
        # self.state = CurrentState()
        self.translation = Translation()
        self.clock = pygame.time.Clock()

        self.bkg = pygame.image.load("bkg.jpg").convert()
        self.sea: Sea = Sea(self.seed, self.screen_properties.monitor_height)
        self.quadtree: QuadTree.QuadTree = QuadTree.QuadTree(self.screen_properties.screen.get_rect(), 4)
        self.deb_rect = QuadTree.Rectangle(0, 0, self.screen_properties.width // 4, self.screen_properties.height // 4)
        self.transmitting_objects: dict[str: network.TransmitObject] = dict()

        self.tentacle_list = []
        self.tentacle = pygame.sprite.Group()
        seg = Tentacle.Segment(250, 250, 0, 20)
        self.tentacle.add(seg)
        self.tentacle_list.append(seg)

        self.box_1 = network.TransmitObject("box_1", "box.png", pygame.Vector2(250, 150), 0)
        self.transmitting_objects["box_1"] = self.box_1

        for i in range(1, 30):
            seg = Tentacle.Segment(self.tentacle_list[i - 1], 0, (30 - i)**1.12)
            self.tentacle.add(seg)
            self.tentacle_list.append(seg)

        self.segments: list[Tentacle.Segment(pygame.sprite.Sprite)] = self.tentacle.sprites()

        self.boid_textures: list[BoidTexture] = []
        for i in range(60):
            self.boid_textures.append(BoidTexture("fish.png"))

    def update_transition_from_data(self, received_list: list[any]):
        """Update data received from the server"""
        self.time_seconds = int(received_list[0])
        # print("TIME", self.time_seconds)
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

    def update_events_and_screen(self):
        self.update_events()
        self.update_screen()
        return True

    def update_events(self):
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.screen_properties.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.screen_properties.width = event.w
                self.screen_properties.height = event.h
                # self.monitor_width = pygame.display.Info().current_w NE NADO PLZ ETO RAZMER EKRANA
                # self.monitor_height = pygame.display.Info().current_h
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(self.screen_properties.window_.position)
            if event.type == pygame.MOUSEMOTION:
                self.cursor_pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                self.is_running = False
                pygame.quit()
                return False

    def update_screen(self):
        self.calculate_translation()
        self.draw_frame()
        # print(self.clock.get_fps())
        self.delta_time = self.clock.tick(60)
        self.sea.perlin_time += self.delta_time

    def calculate_translation(self):
        translation_x = -self.screen_properties.get_window_x()
        translation_y = -self.screen_properties.get_window_y()
        self.translation.set_vector(translation_x, translation_y)

    def draw_frame(self):
        # self.fill_screen_black()
        self.draw_background()
        self.draw_sea()
        self.draw_boids()
        self.draw_tentacle()
        pygame.display.update()

    def fill_screen_black(self):
        self.screen_properties.screen.fill((0, 0, 0))

    def draw_background(self):
        self.screen_properties.screen.blit(self.bkg, (self.translation.x, self.translation.y))

    def draw_sea(self):
        move_x = -self.translation.x
        move_y = self.sea.level - \
                 self.screen_properties.monitor_height / 2 - \
                 self.screen_properties.get_window_y()

        step = 10
        y_1 = self.sea.perlin_gen.get_value(move_x / 500 + self.time_seconds * 0.0005) * 100 + move_y
        for x in range(0, self.screen_properties.width + step, step):
            y_2 = self.sea.perlin_gen.get_value((move_x + x) / 500 +
                                                self.time_seconds * 0.0005) * 100 + move_y
            # pygame.draw.line(self.screen_properties.display, (255, 255, 255), pygame.Vector2(x - step, y_1),
            #                  pygame.Vector2(x, y_2), width=2)
            y_1 = y_2
            pygame.draw.polygon(self.screen_properties.screen, (50, 135, 220),
                                [(x - step, self.screen_properties.height),
                                 (x - step, y_1), (x, y_2),
                                 (x, self.screen_properties.height)])

    def draw_boids(self):
        # Drawing boids
        # boid_counter = 0
        # for boid in self.quadtree.show():
        # print(boid_counter, boid)
        # boid_counter += 1
        self.quadtree.show(pygame, self.screen_properties.screen,
                           self.boid_textures, self.translation.x, self.translation.y, 0)

    def draw_tentacle(self):
        for i in range(1, len(self.segments)):
            # self.segments[i].set_a(self.segments[i - 1].b, len(self.tentacle) - (i+1))
            # pygame.draw.line(self.screen_properties.display,
            #                  (255, 255, 255), self.segments[i].a, self.segments[i].b, width=2)
            self.segments[i].rect = self.segments[i].rect.move(self.translation.x, self.translation.y)
            self.screen_properties.screen.blit(self.segments[i].image, self.segments[i].rect)

    def draw_box(self):
        self.screen_properties.screen.blit(self.box_1.image.convert(),
                                            self.box_1.rect.move(self.translation.x, self.translation.y))

    def get_sending_bytes(self):
        """Stringify global cursor pos and it's status"""
        # print(str(self.cursor_pos) + ' ' + str(int(pygame.mouse.get_focused())))
        cursor = self.cursor_pos + \
                 pygame.Vector2(self.screen_properties.get_window_x(), self.screen_properties.get_window_y())
        return (str(cursor) + ' ' + str(int(pygame.mouse.get_focused())) + ' ' +
                str(int(pygame.mouse.get_pressed()[0]))).encode("utf-8")
