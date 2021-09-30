from Models import Encoder, Decoder, ExampleDecoder
import time
import threading


class Model:
    def __init__(self):
        self.encoder = None
        self.decoder = None

    def is_encoder_availabe(self):
        return self.encoder is not None

    def add_encoder(self, encoder_type):
        pass

    def encode_message(self, msg):
        self.encoder.encode_message(msg)

    def remove_encoder(self):
        self.encoder = None

    def is_decoder_available(self):
        return self.decoder is not None

    def add_decoder(self, decoder_type):
        if decoder_type == "ExampleDecoder":
            self.decoder = ExampleDecoder.ExampleDecoder()

    def remove_decoder(self):
        self.decoder = None

    def get_num_receivers(self):
        return self.decoder.get_num_receivers()

    def get_received(self):
        if not self.is_decoder_available():
            return []
        else:
            return self.decoder.get_received()

    def get_decoded(self):
        if not self.is_decoder_available():
            return []
        else:
            return self.decoder.get_decoded()

