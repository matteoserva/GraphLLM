from modules.executors.common import BaseGuiParser
from .copy_parser import CopyParser

class PackParser(CopyParser):
    node_types = ["copy_pack"]
