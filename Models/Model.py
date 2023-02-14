import importlib
import os

from Utils import Logging


class Model:
    """
    The model is responsible for storing and processing the data.
    A model contains up to one encoder and up to one decoder.
    """
    def __init__(self):
        """
        Initializes the model.
        """
        self.encoder = None
        self.decoder = None

    def add_decoder(self, decoder_type, parameters, parameter_values):
        """
        Adds a new decoder.
        Dynamically imports the module of the implementation and creates an instance of the class in the said
        module (e.g. ExampleDecoder.ExampleDecoder()).
        :param decoder_type: Decoder type.
        :param parameters: Information about parameters.
        :param parameter_values: User-defined parameter values.
        :return: Information about decoder.
        """
        module_pkg = importlib.import_module('.' + decoder_type, package='Models.Implementations.Decoders')
        module = getattr(module_pkg, decoder_type)
        self.decoder = module(parameters, parameter_values)
        return self.decoder.info

    def add_encoder(self, encoder_type, parameters, parameter_values):
        """
        Adds a new encoder.
        :param encoder_type: Encoder type.
        :param parameters: Information about parameters.
        :param parameter_values: User-defined parameter values.
        """
        module_pkg = importlib.import_module('.' + encoder_type, package='Models.Implementations.Encoders')
        module = getattr(module_pkg, encoder_type)
        self.encoder = module(parameters, parameter_values)
        return self.encoder.info

    @staticmethod
    def get_available_decoders():
        """
        Get a list of available decoders.
        :return: List of available decoders.
        """
        path = os.path.join('.', 'Models', 'Implementations', 'Decoders')
        names_extensions = [os.path.splitext(file) for file in os.listdir(path)]
        names_extensions = list(filter(lambda name_extension: name_extension[1] == '.py', names_extensions))
        names = [name_extension[0] for name_extension in names_extensions]
        return names

    @staticmethod
    def get_available_encoders():
        """
        Get a list of available encoders.
        :return: List of avilable encoders.
        """
        path = os.path.join('.', 'Models', 'Implementations', 'Encoders')
        names_extensions = [os.path.splitext(file) for file in os.listdir(path)]
        names_extensions = list(filter(lambda name_extension: name_extension[1] == '.py', names_extensions))
        names = [name_extension[0] for name_extension in names_extensions]
        return names

    def get_decoded(self):
        """
        Gets value updates from the decoder.
        Note: Do not use is_decoder_available, since get_decoded also gets executed when the plot is not active (stopped).
        :return: Decoder value updates if it is available, else None.
        """
        if self.decoder is not None:
            return self.decoder.get_decoded()
        else:
            return None

    def get_decoder_info(self):
        """
        Gets information about decoder.
        Decoder type, receiver information, landmark information.
        :return: Decoder information dictionary if decoder exists, else None.
        """
        if self.decoder is not None:
            return self.decoder.info
        else:
            return None

    @staticmethod
    def get_decoder_parameters(decoder_type):
        """
        Gets information about parameters of a given decoder type.
        :param decoder_type: Decoder type.
        :return: Parameter information.
        """
        module_pkg = importlib.import_module('.' + decoder_type, package='Models.Implementations.Decoders')
        module = getattr(module_pkg, decoder_type)
        try:
            parameters = module.get_parameters()
        except AttributeError:
            Logging.info("Function get_parameters not defined.")
            parameters = None
        return parameters

    @staticmethod
    def get_encoder_parameters(encoder_type):
        """
        Gets information about parameters of a given encoder type.
        :param encoder_type: Encoder type.
        :return: Parameter information.
        """
        module_pkg = importlib.import_module('.' + encoder_type, package='Models.Implementations.Encoders')
        module = getattr(module_pkg, encoder_type)
        try:
            parameters = module.get_parameters()
        except AttributeError as e:
            Logging.info("Function get_parameters not defined.")
            parameters = None
        return parameters

    def get_encoder_info(self):
        """
        Gets information about encoder.
        :return: Encoder information dictionary if decoder exists, else None.
        """
        if self.encoder is not None:
            return self.encoder.info
        else:
            return None

    def is_decoder_active(self):
        """
        Checks whether a decoder is available.
        :return: Whether a decoder is defined and is active.
        """
        return self.decoder is not None and self.decoder.active

    def is_encoder_active(self):
        """
        Checks whether an encoder is available.
        :return: Whether an encoder is defined.
        """
        return self.encoder is not None and self.encoder.active

    def remove_encoder(self):
        """
        Removes the encoder.
        """
        try:
            self.encoder.shutdown()
        except:
            pass

        self.encoder = None

    def remove_decoder(self):
        """
        Removes the decoder.
        """
        self.decoder.decoder_removed()
        self.decoder = None

    def start_decoder(self):
        """
        Starts the decoder.
        """
        self.decoder.start()

    def stop_decoder(self):
        """
        Stops the decoder.
        """
        self.decoder.stop()
