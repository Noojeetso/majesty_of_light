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


def threaded_client(conn):
    conn.send(str.encode("Seed: " + str(seed)))
    connected_clients.add(conn)
    reply = ""
    while True:
        try:
            bytes_ = conn.recv(1024)
            # print("Loaded raw:", bytes_)
            pos_ = bytes_.decode("utf-8")
            # print("Pos:", pos_[1:-1].split(", "))
            # print("pos_", pos_)

            app.is_pressed = int(pos_[-1])
            in_focus = int(pos_[-3])
            # print("in_focus", in_focus)
            pos_ = pos_[1:-5].split(", ")
            # print("pos_", pos_)
            if in_focus:
                app.cursor_pos.xy = int(pos_[0]), int(pos_[1])

            data = app.get_sending_bytes(round(time.time() * 1000))
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
        app.update_positions()
