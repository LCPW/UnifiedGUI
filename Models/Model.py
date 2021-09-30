from Models import Encoder, Decoder, ExampleDecoder
import time
import threading


class Model:
    def __init__(self):
        self.encoder = None
        self.decoder = None

        self.decoded = []

    def is_encoder_availabe(self):
        return self.encoder is not None

    def add_encoder(self, encoder_type):
        pass

    def remove_encoder(self):
        self.encoder = None

    def is_decoder_available(self):
        return self.decoder is not None

    def add_decoder(self, decoder_type):
        if decoder_type == "ExampleDecoder":
            self.decoder = ExampleDecoder.ExampleDecoder()

    def remove_decoder(self):
        self.decoder = None

    def encode_message(self, msg):
        self.encoder.encode_message(msg)

    def get_received(self):
        if not self.is_decoder_available():
            return []
        else:
            return self.decoder.get_received()

    def get_decoded(self):
        # if self.is_decoder_available():
        #     n = self.decoder.get_available()
        #     for i in range(0, n):
        #         x = self.decoder.pop(i)
        #         self.decoded.append(x)
        # return self.decoded
        if not self.is_decoder_available():
            return []
        else:
            return self.decoder.get_decoded()

