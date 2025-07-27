class BaseGuiParser:
    node_types = []

    def _make_default_config(self,old_config):
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        new_config["conf"] = old_config["properties"]

        return new_config

    def _calc_exec(self ,old_inputs ):

        new_inputs = old_inputs
        new_inputs = [str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs]
        val_exec = []

        max_arg_pos = -1
        for arg_pos, vel in enumerate(new_inputs):
            if vel:
                max_arg_pos = arg_pos
            val_exec.append(vel)
        if max_arg_pos > 0:
            val_exec = val_exec[:max_arg_pos+1]
        return val_exec

    def parse_node(self,old_config):
        new_config = self._make_default_config(old_config)
        return new_config

    def postprocess_nodes(self,new_nodes):
        pass