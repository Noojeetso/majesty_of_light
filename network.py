import pygame
import socket
import pickle


class TransmitObject(pygame.sprite.Sprite):
    def __init__(self, name: str, *args):
        self.data: dict[{str: any}] = dict()
        super().__init__()
        self.data.update({"name": name})

        print("tupe?", name, args)
        if name == "tentacle":
            self.data.update({"segments": [[seg.rect, seg.angle] for seg in args[0]]})
        elif name == "flock":
            self.data.update({"quadtree": args[0]})
        else:
            self.orig_image = pygame.image.load(args[0])
            self.image = pygame.image.load(args[0])
            self.rect = self.image.get_rect()
            self.data.update({"rect": self.rect})
            self.data.update({"pos": args[1]})
            self.data.update({"angle": args[2]})

    def pos_update(self, pos: pygame.Vector2):
        self.data["pos"] = pos.copy()

    def pos_angle_update(self, pos: pygame.Vector2, angle):
        self.data["pos"] = pos.copy()
        self.data["angle"] = angle
        self.rect.center = self.data["pos"]

    # def update(self, delta_time):
    #     self.data["pos"] += self.data["velocity"] * delta_time
    #     self.rect.center = self.data["pos"]
    #     self.data["velocity"] += self.data["acceleration"] * delta_time


class Network:
    @staticmethod
    def get_sending_bytes(objects: list[TransmitObject]):
        return pickle.dumps([object_.data for object_ in objects])

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()
        server_ip = socket.gethostbyname(hostname)
        print("server ip:", server_ip)
        self.server = server_ip
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connected = False
        self.pos = self.connect()
        self.seed = int(self.pos[6:])
        print("Seed:", self.seed)

    def connect(self):
        while not self.connected:
            try:
                self.client.connect(self.addr)
                self.connected = True
                return self.client.recv(2048).decode()
            except:
                pass

    def send(self, data):
        try:
            self.client.send(data)
            resp = self.client.recv(13312)
            # print("Getting: ", resp)
            return pickle.loads(resp)
        except socket.error as e:
            print(e)
