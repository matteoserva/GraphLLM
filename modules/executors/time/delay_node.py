from modules.executors.common import GenericExecutor
import time

class DelayNode(GenericExecutor):
    """Copies the input after a delay"""
    node_type = "delay"

    def __init__(self, initial_parameters):
        super().__init__(initial_parameters)
        self.next_alarm = None

    def initialize(self,*args,**kwargs):
        pass

    def graph_started(self):
        self.graph_running = True

    def __call__(self, inputs, *args):
        next_alarm = time.time() + self.properties["delay"]

        while self.graph_running:
            current_time = time.time()
            if current_time >= next_alarm:
                break

            sleep_time = next_alarm - current_time
            time.sleep(min(sleep_time, 0.1))  # Max 100ms sleep

        outputs = [el for el in inputs]
        return outputs

    def graph_stopped(self):
        self.graph_running = False

