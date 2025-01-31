from modules.executors.common import BaseGuiParser
from .copy_parser import CopyParser

class UnpackParser(CopyParser):
    node_types = ["copy_unpack"]
