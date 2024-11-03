from modules.logging.logger import Logger
from modules.executors import get_executors


def default_logger(*args, **kwargs):
    print(*args, **kwargs)


_available_executors = None


class ExecutorFactory:

    @staticmethod
    def makeExecutor(type="stateless", config={}):
        global _available_executors
        if not _available_executors:
            _available_executors = get_executors()
        full_config = {}
        full_config["name"] = config.get("name", "/")
        full_config["logger"] = config.get("logger", Logger())
        full_config["client"] = config.get("client", None)
        full_config["path"] = config.get("path", "/")

        executor = None
        if type in _available_executors:
            executor = _available_executors[type](full_config)

        return executor
