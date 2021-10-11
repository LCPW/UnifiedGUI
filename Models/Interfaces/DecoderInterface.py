import importlib
import threading


class DecoderInterface:
    def __init__(self, num_receivers, receiver_types, receiver_descriptions=None):
        self.num_receivers = num_receivers
        self.receiver_types = receiver_types
        self.receiver_descriptions = receiver_types if receiver_descriptions is None else receiver_descriptions
        self.active = False

        self.receivers = []
        self.receiver_buffer = []

        for i in range(self.num_receivers):
            # Dynamically import the module of the implementation
            module = importlib.import_module('.' + self.receiver_types[i], package='Models.Implementations.Receivers')
            # Create an instance of the class in the said module (e.g. ExampleReceiver.ExampleReceiver())
            instance = getattr(module, self.receiver_types[i])(self.receiver_descriptions[i])
            self.receivers.append(instance)
            self.receiver_buffer.append([])

        self.decoded = []

    def start(self):
        for i in range(self.num_receivers):
            thread = threading.Thread(target=self.receivers[i].listen, daemon=True)
            thread.start()
        self.active = True

    def stop(self):
        # TODO: Stop threads?
        self.active = False

    def get_num_receivers(self):
        return self.num_receivers

    def get_receiver_info(self):
        x = []
        for receiver in self.receivers:
            x.append({'description': receiver.description, 'sensor_descriptions': receiver.sensor_descriptions})
        return x

    def is_active(self):
        return self.active

    def get_received(self):
        self.empty_receiver_buffers()
        return self.receiver_buffer

    def get_decoded(self):
        return self.decoded

    def empty_receiver_buffers(self):
        for i in range(len(self.receivers)):
            n = self.receivers[i].get_available()
            for j in range(n):
                self.receiver_buffer[i].append(self.receivers[i].get(0))

        # self.decoded = []
        # for i in range(0, len(self.receiver_buffer[0])):
        #     t, x = self.receiver_buffer[0][i]
        #
        #     if x < 0.5:
        #         self.decoded.append((t, "A"))
        #     else:
        #         self.decoded.append((t, "B"))