from modules.executors.common import BaseGuiParser
from .copy_parser import CopyParser

class StandardMuxParser(CopyParser):
    node_types = ["standard_mux"]