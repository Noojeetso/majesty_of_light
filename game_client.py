import application
import pickle
import network

if __name__ == "__main__":
    client_network = network.Network()
    app = application.App(client_network.seed)
    app.is_running = True
    print("Loaded unpickled: ", 123)
    while app.is_running:
        app.is_running = app.update_events_and_screen()
        bytes_ = app.get_sending_bytes()
        # print("Sending: ", bytes_)
        resp = client_network.send(bytes_)
        app.update_transition_from_data(pickle.loads(resp))
        print("Loaded unpickled: ", resp)
