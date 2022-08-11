import application
import pickle
import network

print("name: ", __name__)
if __name__ == "__main__":
    print("name: ", __name__)
    n = network.Network()
    print("name: ", __name__)
    app = application.App(n.seed)
    print("name: ", __name__)
    app.is_running = True
    print("Loaded unpickled: ", 123)
    while app.is_running:
        app.is_running = app.update()
        bytes_ = app.get_sending_bytes()
        # print("Sending: ", bytes_)
        resp = n.send(bytes_)
        app.transition_update(pickle.loads(resp))
        print("Loaded unpickled: ", resp)
