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
        encoded_send = app.get_encoded_send_data()
        # print("Sending: ", encoded_send_data)
        encoded_response = client_network.send(encoded_send)
        decoded_response = decode_response_data(encoded_response)
        app.update_transition_from_data(decoded_response)
        # print("Loaded unpickled: ", resp)
