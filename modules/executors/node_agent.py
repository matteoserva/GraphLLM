from ..parser import solve_templates
from .common import solve_placeholders
from ..common import try_solve_files
import json


class AgentController:
    def __init__(self, *args):
        self.current_prompt = ""
        self.base_prompt = ""
        self.tokens=["Thought: ","Action:","Inputs:","Observation: "]
        self.state = "INIT"
        self.current_iteration = 0
        self.answer = ""
        self.hints = ""
        self.subtype="simple"
        self.enabled_input = 0

    def set_parameters(self,arg):
        if "tokens" in arg:
            self.tokens = arg["tokens"]
        if "hints" in arg:
            self.hints = arg["hints"]
        if "subtype" in arg:
            self.subtype = arg["subtype"]

    def get_properties(self):
        res = {"input_rule":"OR"}
        return res

    def _reset_internal_state(self):
        self.state = "INIT"
        self.current_prompt = self.base_prompt
        self.current_iteration = 0

    def load_config(self,args):

        template_args =  try_solve_files(args)
        self.base_prompt , _ = solve_templates("{}", template_args)

        self._reset_internal_state()
        pass

    def set_dependencies(self,args):
        self.ops_executor = args[0]

    def _handle_tool_response(self,prompt_args):

        new_observation = str(prompt_args)
        if len(new_observation) > 0:
            if len(self.tokens[3]) > 0 and self.tokens[3][0] == "<" and self.tokens[3][-1] == ">":
                new_observation = self.tokens[3] + new_observation + "</" + self.tokens[3][1:] + "\n" + self.tokens[0]
            else:
                new_observation = self.tokens[3] + new_observation + "\n" + self.tokens[0]
        self.current_prompt += new_observation
        return self.current_prompt

    def _handle_query(self,prompt_args):
        ops_string = self.ops_executor.get_formatted_ops()
        variables = {"tools":ops_string, "hints": self.hints}
        self.current_prompt ,_ = solve_templates(self.base_prompt, [ops_string])
        self.current_prompt = solve_placeholders(self.current_prompt,[],variables)
        return self.current_prompt

    def _handle_llm_response(self,resp):

        resp = self._clean_response(resp)
        self.current_prompt += resp
        respo = self._parse_response(resp)
        respo["raw"] = resp

        return respo

    def _execute_prompt(self):
        prompt = yield
        print("sono thread")
        # send query
        res = self._handle_query(prompt)
        llm_response = yield (1,res)

        while True:
            # call tool
            self.current_iteration += 1
            if self.current_iteration >= 10:
                yield (0, Exception("llm agent overrun"))
            respo = self._handle_llm_response(llm_response)

            skip_tool_call = False
            if self.subtype == "reflexion":
                s0 = self.current_prompt.split("<planning>")[-1]
                s1 = s0[s0.find("<thinking>"):]
                current_trace = "<question>" + prompt + "</question>\n" + s1
                reflexion_response = yield(3,current_trace)
                parsed_response = json.loads(reflexion_response)
                if parsed_response["result"] != "success":
                    tool_response = "Exception: " + parsed_response["comment"]
                    skip_tool_call = True

            if not skip_tool_call:
                tool_response = yield (2, respo)

            if (respo["command"].startswith("answer")) and not isinstance(tool_response, Exception):
                self.state = "COMPLETE"
                self.answer = respo["args"]

            # fase 3
            if isinstance(tool_response, Exception):
                tool_response = "Exception: " + str(tool_response)
            if (self.state == "COMPLETE"):
                self._reset_internal_state()
                yield (0, tool_response)
            else:
                res = self._handle_tool_response(tool_response)
                llm_response = yield (1, res)

    def _handle_graph_request(self,inputs):
        outputs = [None] * 4
        true_inputs = len([el for el in inputs if el])
        if(true_inputs != 1):
            throw ("controller: invalid number of inputs")
        if not inputs[self.enabled_input]:
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
