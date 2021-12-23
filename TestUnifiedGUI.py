import unittest
import os
import importlib
import sys


# TODO: Option to test only a single file instead of all decoders?
# TODO: Individual Testcase file for each type

def is_same_shape2(l1, l2):
    return len(l1) == len(l2) and all([len(l1[i]) == len(l2[i]) for i in range(len(l1))])


class TestDecoders(unittest.TestCase):
    SINGLE_FILE = None

    def setUp(self):
        # self.single_file = None
        self.modules = []
        self.classes = []

        path = os.path.join('.', 'Models', 'Implementations', 'Decoders')
        if self.SINGLE_FILE is not None:
            files = [self.SINGLE_FILE + ".py"]
        else:
            files = os.listdir(path)

        for file in files:
            name, extension = os.path.splitext(file)
            if extension == '.py':
                m = importlib.import_module('.' + name, package='Models.Implementations.Decoders')
                self.modules.append(m)
                # TODO: ???
                c = getattr(m, name)(None, None)
                self.classes.append(c)

    # def test1(self):
    #    actual = True
    #    expected = True
    #    self.assertEqual(expected, actual, msg="123")

    def test_parameters(self):
        def message(msg, mod):
            return msg + "[Module: " + str(mod) + "]."

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
                    self.assertIn('description', keys, message("Description must be defined.", m))
                    self.assertIsInstance(p['description'], str, message("Description must be str.", m))
                    self.assertIn('dtype', keys, message("Datatype must be defined.", m))
                    self.assertIn(p['dtype'], ['bool', 'int', 'float', 'string', 'item'],
                                  message("Parameter datatype not support in module", m))
                    self.assertIn('default', keys, message("Default must be defined.", m))

                    if p['dtype'] == 'bool':
                        self.assertIn(p['default'], [True, False], message("Default must be True or False.", m))
                    elif p['dtype'] == 'int':
                        self.assertIsInstance(p['default'], int, message("Default value must be int.", m))
                        self.assertIn('min', keys, message("Minimum must be defined.", m))
                        self.assertIsInstance(p['min'], int, message("Minimum value must be int.", m))
                        self.assertIn('max', keys, message("Maximum must be defined.", m))
                        self.assertIsInstance(p['max'], int, message("Maximum value must be int.", m))
                    elif p['dtype'] == 'float':
                        self.assertIsInstance(p['default'], (float, int),
                                              message("Default value must be float or int.", m))
                        self.assertIn('min', keys, message("Minimum must be defined.", m))
                        self.assertIsInstance(p['min'], (float, int), message("Minimum value must be float or int.", m))
                        self.assertIn('min', keys, message("Maximum must be defined.", m))
                        self.assertIsInstance(p['min'], (float, int), message("Maximum value must be float or int.", m))
                        self.assertIn('decimals', keys, message("Decimals must be defined.", m))
                        self.assertIsInstance(p['decimals'], int, message("Decimals value must be int.", m))
                    elif p['dtype'] == 'string':
                        self.assertIsInstance(p['default'], str, message("Default value must be str.", m))
                        self.assertIn('max_length', keys, message("Maximum length must be defined.", m))
                        self.assertIsInstance(p['max_length'], int, message("Max length must be int.", m))
                    elif p['dtype'] == 'item':
                        self.assertIn('items', keys, message("Items must be defined.", m))
                        self.assertIsInstance(p['items'], list, message("Items must be list.", m))
                        for i in p['items']:
                            self.assertIsInstance(i, str, message("Items must be str.", m))
                        self.assertIn(p['default'], p['items'], message("Default item must be in items.", m))

    def test_receivers(self):
        for c in self.classes:
            self.assertIn('receiver_types', dir(c), "receiver_types not defined.")
            self.assertIsInstance(c.receiver_types, list, "receiver_types is not a list.")
            self.assertGreater(len(c.receiver_types), 0, "receiver_types must contain at least one receiver.")
            # TODO: Test that receivers actually exist


class TestEncoders(unittest.TestCase):
    def test234(self):
        self.assertTrue(True)


class TestReceivers(unittest.TestCase):
    pass


class TestTransmitters(unittest.TestCase):
    pass


# if __name__ == '__main__':
#     unittest.main()

if __name__ == '__main__':
    # TODO
    if len(sys.argv) == 3:
        file = sys.argv.pop()
        if sys.argv[2] == 'TestEncoders':
            TestEncoders.SINGLE_FILE = file
        elif sys.argv[2] == 'TestDecoders':
            TestDecoders.SINGLE_FILE = file
        elif sys.argv[2] == 'TestReceivers':
            TestReceivers.SINGLE_FILE = file
        elif sys.argv[2] == 'TestTransmitters':
            TestTransmitters.SINGLE_FILE = file
        else:
            print(f"{sys.argv[2]} is not a valid argument.")
            sys.exit(1)

    print("ARGV")
    print(sys.argv)
    # sys.argv = sys.argv[:2]
    unittest.main()