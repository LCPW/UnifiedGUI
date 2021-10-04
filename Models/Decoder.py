class Decoder:
    def __init__(self, num_receivers):
        self.num_receivers = num_receivers
        self.active = False

        self.receivers = []
        self.receiver_buffer = []
        self.decoded = []

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