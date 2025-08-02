from modules.executors.common import GenericExecutor
import time

class MetronomeNode(GenericExecutor):
    """Sends output periodically"""

    """(notes to self)
    - Working: no inputs. Free running, sends ts to output
    - inputs present, copy the input and sends this as second output

    start immediately sends message the first time it is scheduled (either free or with input)"""
    node_type = "metronome"



    def __init__(self, initial_parameters):
        super().__init__(initial_parameters)
        self.next_alarm = None
        self.graph_running = False

    def initialize(self,*args,**kwargs):
        pass
        #self.node.set_parameter("free_runs",1)

    def graph_started(self):
        self.first_run = True
        self.graph_running = True
        self.generated_output = "hello"
        self.free_running = False

    def __call__(self, inputs, *args):
        if self.first_run:
            if self.properties["start_immediate"] == "YES":
                self.next_alarm = time.time()
            else:
                self.next_alarm = time.time() + self.properties["period"]
            if len(inputs) > 0:
                self.generated_output = inputs[0]
            self.free_running = len(inputs)<= 0
        self.first_run = False

        if self.free_running:
            self.node.set_parameter("free_runs",1)

        current_time = None
        while self.graph_running:
            current_time = time.time()
            if current_time >= self.next_alarm:
                break

            sleep_time = self.next_alarm - current_time
            time.sleep(min(sleep_time, 0.1))  # Max 100ms sleep

        self.next_alarm = self.next_alarm + self.properties["period"]
        outputs = [current_time, self.generated_output]
        return outputs

    def graph_stopped(self):
        self.graph_running = False
        self.next_alarm = None
