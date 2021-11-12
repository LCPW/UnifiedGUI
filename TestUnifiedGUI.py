import unittest
import os
import importlib


# TODO: Option to test only a single file instead of all decoders?
# TODO: Individual Testcase file for each type?


class TestDecoders(unittest.TestCase):
    def setUp(self):
        self.modules = []
        self.classes = []

        for file in os.listdir('./Models/Implementations/Decoders'):
            name, extension = os.path.splitext(file)
            if extension == '.py':
                m = importlib.import_module('.' + name, package='Models.Implementations.Decoders')
                self.modules.append(m)
                c = getattr(m, name)(None)
                self.classes.append(c)

    #def test1(self):
    #    actual = True
    #    expected = True
    #    self.assertEqual(expected, actual, msg="123")

    def test_parameters(self):
        def message(msg, mod): return msg + "[Module: " + str(mod) + "]."

        for m in self.modules:
            try:
                params = m.PARAMETERS
            except AttributeError:
                return
            if params is not None:
                d = [p['description'] for p in params]
                self.assertTrue(len(d) == len(set(d)), message("Parameter descriptions must be unique.", m))
                for p in params:
                    keys = list(p.keys())
                    self.assertIn('description', keys)
                    self.assertIsInstance(p['description'], str)
                    self.assertIn('dtype', keys)
                    self.assertIn(p['dtype'], ['bool', 'int', 'float', 'string', 'item'], message("Parameter datatype not support in module", m))
                    self.assertIn('default', keys)

                    if p['dtype'] == 'bool':
                        self.assertIn(p['default'], [True, False])
                    elif p['dtype'] == 'int':
                        self.assertIsInstance(p['default'], int, message("Default value must be int.", m))
                        self.assertIn('min', keys)
                        self.assertIsInstance(p['min'], int, message("Minimum value must be int.", m))
                        self.assertIn('max', keys)
                        self.assertIsInstance(p['max'], int, message("Maximum value must be int.", m))
                    elif p['dtype'] == 'float':
                        self.assertIsInstance(p['default'], (float, int), message("Default value must be float or int.", m))
                        self.assertIn('min', keys)
                        self.assertIsInstance(p['min'], (float, int), message("Minimum value must be float or int.", m))
                        self.assertIn('min', keys)
                        self.assertIsInstance(p['min'], (float, int), message("Maximum value must be float or int.", m))
                        self.assertIn('decimals', keys)
                        self.assertIsInstance(p['decimals'], int, message("Decimals value must be int.", m))
                    # TODO

    def test_receivers(self):
        for c in self.classes:
            self.assertIn('receiver_types', dir(c), "receiver_types not defined.")
            self.assertIsInstance(c.receiver_types, list, "receiver_types is not a list.")
            self.assertGreater(len(c.receiver_types), 0, "receiver_types must contain at least one receiver.")
            # TODO: Test that receivers actually exist


class TestEncoders(unittest.TestCase):
    pass


class TestReceivers(unittest.TestCase):
    pass


class TestTransmitters(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()