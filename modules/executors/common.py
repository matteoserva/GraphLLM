
from modules.common.base_node import BaseExecutor as GenericExecutor
from modules.common.base_node import BaseGuiParser as BaseGuiParser
from modules.common.base_node import BaseGuiNode as BaseGuiNode

from modules.common.prompt_utils import solve_placeholders, solve_prompt_args

class ExecutorOutput():
    def __init__(self,data,meta={}):
        self.data = data
        self.meta = meta

    def __str__(self):
        return str(self.data)


