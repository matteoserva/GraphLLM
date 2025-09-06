from modules.common import try_solve_files
from modules.executors.common import GenericExecutor
from .list_node import ListNode

class ConstantNode(ListNode):
    node_type = "constant"
    def __init__(self,*args):
        super().__init__(*args)

    def set_template(self,args):
        solved_args = try_solve_files(args)
        packed_args = [solved_args]
        super().set_template(packed_args)
