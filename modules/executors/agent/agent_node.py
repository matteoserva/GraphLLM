from modules.formatter import solve_templates
from modules.executors.common import solve_placeholders
from modules.common import try_solve_files
import json


class AgentController:
    def __init__(self, node_graph_parameters):
        self.base_prompt = ""
        self.tokens=["Thought: ","Action:","Inputs:","Observation: "]
        self.hints = ""
        self.subtype="simple"
        self.enabled_input = 0
        self.logger = node_graph_parameters["logger"]
        self.path = node_graph_parameters.get("path", "/")
        self.reflexion_history = ""

    def set_parameters(self,arg):
        if "tokens" in arg:
            self.tokens = arg["tokens"]
        if "hints" in arg:
            self.hints = arg["hints"]
        if "subtype" in arg:
            self.subtype = arg["subtype"]
        if "multi_turn" in arg:
            self.multi_turn = arg["multi_turn"]

    def get_properties(self):
        res = {"input_rule":"OR"}
        return res

    def load_config(self,args):

        # the three parts of the prompt must be passed separately

        template_args =  try_solve_files(args)
        self.base_prompt , _ = solve_templates("{}", template_args)

        pass

    def set_dependencies(self,args):
        self.ops_executor = args[0]

    def _build_tool_response(self,prompt_args,skip_generation = False):

        new_observation = str(prompt_args)
        if True or len(new_observation) > 0:
            if len(self.tokens[3]) > 0 and self.tokens[3][0] == "<" and self.tokens[3][-1] == ">":
                new_observation = self.tokens[3] + new_observation + "</" + self.tokens[3][1:] + "\n" + ("" if skip_generation else self.tokens[0])
            else:
                new_observation = self.tokens[3] + new_observation + "\n" + ("" if skip_generation else self.tokens[0])
        self.logger.log("print",self.path,new_observation,end="")

        return new_observation

    def _build_template(self,ops_string):
        variables = {"tools":ops_string, "hints": self.hints}
        new_prompt ,_ = solve_templates(self.base_prompt, [],variables)
        new_prompt = solve_placeholders(new_prompt,[],variables)
        return new_prompt

    def _handle_query(self,template,prompt_args):
        new_prompt, _ = solve_templates(template, [prompt_args], {})
        return new_prompt

    def _parse_llm_response(self,resp):

        resp = self._clean_response(resp)

        respo = self._parse_response(resp)
        respo["raw"] = resp

        return respo

    def _prompt_insert_scratchpad(self,clean_prompt,scratchpad):
        new_prompt = clean_prompt.replace("{}", scratchpad)
        return new_prompt

    def _execute_prompt(self):

        state = "INIT"
        current_iteration = 0

        prompt = yield
        print("sono thread")
        # send query
        ops_string = yield(2,{"command":"get_formatted_ops","args":[]})
        prompt_template = self._build_template(ops_string)
        clean_prompt = self._handle_query(prompt_template,prompt)

        if "{}" not in clean_prompt:
            clean_prompt += "{}"
        scratchpad = ""
        reflexion_scratchpad = self.reflexion_history + "<question>" + prompt + "</question>\n"
        while True:
            current_prompt = self._prompt_insert_scratchpad(clean_prompt, scratchpad)
            llm_response = yield (1, current_prompt)

            # call tool
            current_iteration += 1
            if current_iteration >= 10:
                final_response = Exception("llm agent overrun")
                break

            scratchpad += llm_response
            respo = self._parse_llm_response(llm_response)

            skip_tool_call = False
            if self.subtype == "reflexion":
                current_prompt = self._prompt_insert_scratchpad(clean_prompt,scratchpad)
                s0 = llm_response.split("</planning>\n")[-1]
                reflexion_scratchpad += s0
                reflexion_response = yield(3,reflexion_scratchpad)
                parsed_response = json.loads(reflexion_response)
                if parsed_response["result"] != "success":
                    tool_response = "Exception: " + parsed_response["comment"]
                    skip_tool_call = True

            if not skip_tool_call:
                tool_response = yield (2, respo)

            if (respo["command"].startswith("answer")) and not isinstance(tool_response, Exception):
                state = "COMPLETE"

            # fase 3
            if isinstance(tool_response, Exception):
                tool_response = "Exception: " + str(tool_response)
            if state != "COMPLETE":
                new_observation = self._build_tool_response(tool_response,False)
            else:  #complete
                new_observation = self._build_tool_response("answer sent to user",True)
            scratchpad += new_observation
            reflexion_scratchpad += new_observation
            if (state == "COMPLETE"):
                reflexion_scratchpad += "<evaluation> The answer has been sent to the user </evaluation>\n"
                final_response = tool_response
                break

        if hasattr(self,"multi_turn") and self.multi_turn and "{p:user}" in prompt_template:
            current_prompt = self._prompt_insert_scratchpad(clean_prompt, scratchpad).strip()
            if not current_prompt.endswith("{p:eom}"):
                current_prompt += "{p:eom}"
            final_template = "\n\n{p:user}" +prompt_template.split("{p:user}")[-1]
            current_prompt += final_template
            self.base_prompt = current_prompt
            self.reflexion_history = reflexion_scratchpad

        yield(0, final_response)

    def _handle_graph_request(self,inputs):
        outputs = [None] * 4
        true_inputs = len([el for el in inputs if el is not None])
        if(true_inputs != 1):
            throw ("controller: invalid number of inputs")
        if inputs[self.enabled_input] is None:
            throw("controller: unexpected input")

        if self.enabled_input == 0:
            self.t1 = self._execute_prompt()
            next(self.t1)

        id, val = self.t1.send(inputs[self.enabled_input])
        self.enabled_input = id
        outputs[id] = val
        inputs[self.enabled_input] = None

        return outputs

    def __call__(self,*args,**kwargs):
        return self._handle_graph_request(*args,**kwargs)

    def _clean_response(self, resp):
        resp = resp.strip()
        while "\n\n" in resp:
           resp = resp.replace("\n\n","\n")
        resp = resp.split("\nObservation")[0]
        resp = resp+"\n"
        return resp

    def _parse_response(self,resp):
        comando = resp[resp.find(self.tokens[1]) + len(self.tokens[1]):].split("\n")[0].strip()

        if resp.find("<action_name>") >= 0:
            s1 = resp.split("<action_parameter>")
            a1 = s1[0]
            p1 = s1[1:]
            a2 = a1[a1.find("<action_name>")+13:a1.find("</action_name>")].strip()
            p2 = [ el[:el.find("</action_parameter>")].strip() for el in p1]
            comando = a2
            parametri = p2

        elif comando.find("(") >= 0:  # forma compatta comando(parametri)
            c1 = comando.split("(")
            comando = c1[0].strip()
            c2 = c1[1].find(")")
            if c2 < 0:
                parametri = c1[1][:-1]
            else:
                parametri = c1[1][:c2]
        else:
            parametri = resp[resp.find("Inputs:") + 7:].strip()

        if resp.find("Answer:") >= 0:
            comando = "answer"
            parametri = resp[resp.find("Answer:") + 7:].strip().split("\n")[0]
        resp = {"command":comando,"args":parametri}

        return resp
