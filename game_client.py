import application
import pickle
import network


def decode_response_data(encoded_data: bytes):
    return pickle.loads(encoded_data)


if __name__ == "__main__":
    client_network = network.Network()
    app = application.App(client_network.seed)
    app.is_running = True
    # print("Loaded unpickled: ", 123)
    while app.is_running:
        app.is_running = app.update_events_and_screen()
        encoded_send_data = app.get_encoded_send_data()
        # print("Sending: ", encoded_send_data)
        encoded_response_data = client_network.send(encoded_send_data)
        decoded_response_data = decode_response_data(encoded_response_data)
        app.update_transition_from_data(decoded_response_data)
        # print("Loaded unpickled: ", resp)
