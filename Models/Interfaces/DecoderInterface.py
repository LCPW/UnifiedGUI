import importlib
import threading


class DecoderInterface:
    def __init__(self, num_receivers, receiver_types):
        self.num_receivers = num_receivers
        self.receiver_types = receiver_types
        self.active = False

        self.receivers = []
        self.receiver_buffer = []
        self.decoded = []

    def start(self):
        for i in range(self.num_receivers):
            # Dynamically import the module of the implementation
            my_module = importlib.import_module('.' + self.receiver_types[i], package='Models.Implementations.Receivers')
            # Create an instance of the class in the said module (e.g. ExampleReceiver.ExampleReceiver())
            instance = getattr(my_module, self.receiver_types[i])()
            self.receivers.append(instance)
            self.receiver_buffer.append([])
            thread = threading.Thread(target=self.receivers[i].listen)
            thread.start()
        self.active = True

    def get_num_receivers(self):
        return self.num_receivers

    def is_active(self):
        return self.active

    def get_received(self):
        return self.receiver_buffer

    def get_decoded(self):
        self.empty_buffers()
        return self.decoded

    def empty_buffers(self):
        for i in range(len(self.receivers)):
            n = self.receivers[i].get_available()
            for j in range(n):
                self.receiver_buffer[i].append(self.receivers[i].get(j))

        # self.decoded = []
        # for i in range(0, len(self.receiver_buffer[0])):
        #     t, x = self.receiver_buffer[0][i]
        #
        #     if x < 0.5:
        #         self.decoded.append((t, "A"))
        #     else:
        #         self.decoded.append((t, "B"))