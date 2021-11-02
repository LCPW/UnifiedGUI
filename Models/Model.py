import importlib


class Model:
    def __init__(self):
        self.encoder = None
        self.decoder = None

    def is_encoder_available(self):
        return self.encoder is not None

    def add_encoder(self, encoder_type):
        # TODO
        pass

    def encode_message(self, message):
        self.encoder.encode_message(message)

    def remove_encoder(self):
        self.encoder = None

    def is_decoder_available(self):
        return self.decoder is not None and self.decoder.active

    def add_decoder(self, decoder_type):
        # Dynamically import the module of the implementation
        module = importlib.import_module('.' + decoder_type, package='Models.Implementations.Decoders')
        # Create an instance of the class in the said module (e.g. ExampleDecoder.ExampleDecoder())
        self.decoder = getattr(module, decoder_type)()

    def start_decoder(self):
        self.decoder.start()

    def stop_decoder(self):
        self.decoder.stop()

    def remove_decoder(self):
        self.decoder = None

    def get_receiver_info(self):
        return self.decoder.get_receiver_info()

    def get_landmark_info(self):
        return self.decoder.get_landmark_info()

    def get_decoded(self):
        if not self.is_decoder_available():
            return None
        else:
            return self.decoder.get_decoded()