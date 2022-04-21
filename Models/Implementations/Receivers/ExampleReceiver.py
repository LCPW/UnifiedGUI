from Models.Interfaces.ReceiverInterface import ReceiverInterface
from Utils import Queue


class ExampleReceiver(ReceiverInterface):
    def __init__(self):
        super().__init__()

        self.num_sensors = 1
        self.sensor_names = ["Test"]

        super().setup()

    def listen_step(self):
        if not Queue.queue.empty():
            values, t = Queue.queue.get()
            values = (values,)
            self.append_values(values, timestamp=t + 1)