from modules.executors.common import BaseGuiParser

class TextInputParser(BaseGuiParser):
    node_types = ["code_infill"]

    def parse_node(self ,old_config):
        new_config = {}
        new_config["type"] = "code_infill"
        properties = old_config.get("properties", {})
        files = properties.get("files", [])
        file_names = [el["name"] for el in files]
        file_init = [el["content"] for el in files]

        repo_name = properties.get("repo_name","test")
        exec = []
        conf = {"repo_name": repo_name, "file_names": file_names}
        outputs = old_config["linked_outputs"]
        if(len(outputs) > 0):
            output0 = [ el for el in outputs[0] if el["type"].endswith("llm_call")]
            if len(output0) == 1:
                exec = [str(output0[0]["id"]) + "[0]"]
                conf["free_runs"] = 1

        new_config["conf"] = conf
        new_config["init"] = file_init
        new_config["exec"] = exec

        return new_config