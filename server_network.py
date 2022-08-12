import socket
from _thread import *
import pickle
import server_application
import time


seed = round(time.time() * 1000)
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
print(local_ip)

server_ip = local_ip
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server_ip, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

connected_clients = set()
updated_clients = set()
server_data = dict()


class Storage:
    idCount = 0


storage = Storage()


class ParsedData:
    is_pressed: bool = False
    in_focus: bool = False
    cursor_pos: list[int] = list()


class PacketParser:
    parsed_data = ParsedData()
    decoded_data: str = ""

    def parse_data(self, encoded_data: bytes):
        self.decode_data(encoded_data)
        self.read_data()

    def decode_data(self, encoded_data: bytes):
        self.decoded_data = encoded_data.decode("utf-8")

    def read_data(self):
        self.check_if_pressed()
        self.check_in_focus()
        self.parse_cursor_pos()

    def check_if_pressed(self):
        self.parsed_data.is_pressed = bool(int(self.decoded_data[-1]))

    def check_in_focus(self):
        self.parsed_data.in_focus = bool(int(self.decoded_data[-3]))

    def parse_cursor_pos(self):
        cursor_coordinates = self.decoded_data[1:-5].split(", ")
        self.parsed_data.cursor_pos = [int(cursor_coordinates[0]), int(cursor_coordinates[1])]

    def is_pressed(self):
        return self.parsed_data.is_pressed

    def in_focus(self):
        return self.parsed_data.in_focus

    def get_cursor_pos(self):
        return self.parsed_data.cursor_pos


def threaded_client(conn):
    conn.send(str.encode("Seed: " + str(seed)))
    connected_clients.add(conn)
    parser = PacketParser()
    current_time_seconds: int

    while True:
        try:
            data_bytes = conn.recv(1024)
            parser.parse_data(data_bytes)

            app.is_pressed = parser.is_pressed()
            app.in_focus = parser.in_focus()
            if app.in_focus:
                # app.cursor_pos.xy = int(parser.parsed_data.cursor_pos[0]), int(parser.parsed_data.cursor_pos[1])
                app.cursor_pos.xy = parser.get_cursor_pos()

            current_time_seconds = round(time.time() * 1000)
            data = app.get_sending_bytes(current_time_seconds)
            # print("Sending pickled:", data)
            # server_data =
            # if server_data.keys() != data.keys():
            #     updated_clients.clear()
            conn.sendall(pickle.dumps(data))
        except:
            break

    print("Lost connection")
    storage.idCount -= 1
    connected_clients.remove(conn)
    conn.close()


def accept_connections():
    thread_running = True
    while thread_running:
        conn, addr = s.accept()
        print("Connected to:", addr)

        storage.idCount += 1
        start_new_thread(threaded_client, (conn, ))


if __name__ == "__main__":
    app = server_application.App()

    start_new_thread(accept_connections, ())

    app.is_running = True
    while app.is_running:
        app.update_events_and_positions()
