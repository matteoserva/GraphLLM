from modules.formatter import PromptBuilder
import json
import requests
#from . import common
from ..common import get_formatter,build_prompt,merge_params
from ..formatter import Formatter
import time
import copy
from threading import BoundedSemaphore

DEFAULT_HOST="localhost"

class LLamaCppClient:
    def __init__(self, host=DEFAULT_HOST, port=8080, base_url=None, model=None):
        self.host = host
        self.port = port
        if base_url:
            self.base_url = base_url
            if model:
                self.base_url = base_url + "/upstream/" + model
        else:
            self.base_url = "http://" + self.host + ":" + str(self.port)
        self.client_parameters = {}
        a = {}
        #a["n_predict"] = 1024 * 4
        a["stop"] = ["<|eom_id|>", "<|eot_id|>", "<|end|>", "<|im_end|>", "</s>", "<end_of_turn>", "<|im_start|>", "[|endofturn|]"]
        #        a["temperature"] = 0.0
        a["seed"] = -1
        a["cache_prompt"] = True
        a["stream"] = True
        # a["n_probs"] = 10
        # a["n_keep"] = -1
        # a["top_k"] = 5
        self.prompt_metadata = {}
        self.default_params = a
        self.connected = False
        self.formatter = Formatter()

    def get_formatter_config(self):
        props = self.get_server_props()
        model_props = {"model_name": self.model_name}
        if "chat_template" in props:
            model_props["chat_template"] = props["chat_template"]
            if "bos_token" in props:
                model_props["bos_token"] = props["bos_token"]
            model_props["apply_template"] = self.apply_template

        return model_props

    def connect(self):
        if not self.connected:
            props = self.get_server_props()
            self.max_slots = props.get("total_slots", 1)

            if "model_path" in props:
                model_path = props["model_path"]
            else:
                model_path = props["default_generation_settings"]["model"]
            model_name = model_path.split("/")[-1]
            self.model_name = model_name

            model_props = self.get_formatter_config()

            self.formatter.load_model(model_props)
            # get_formatter(props)
            self.connetion_semaphore = BoundedSemaphore(value=self.max_slots)
            self.connected = True

    def set_parameters(self, parameters):
        client_config_names = ["host", "port"]
        if "port" in parameters:
            self.port = parameters["port"]
        if "host" in parameters:
            self.host = parameters["host"]
            self.connect()
        else:
            self.parameters = parameters

    def get_model_name(self):
        return self.model_name

    def get_server_props(self):
        if self.connected:
            return self.server_props
        url = "http://" + self.host + ":" + str(self.port) + "/props"

        retries = 30
        while retries > 0:
            r = requests.get(url)
            resp = json.loads(r.content)
            retries -= 1
            if "error" in resp:
                print("server busy")
                time.sleep(2)
            else:
                break
        max_context = resp["default_generation_settings"]["n_ctx"]

        # try detecting the bos token
        if "chat_template" in resp:
            try:
                rendered = self.tokenize("<<<<USER>>>>", add_special=True, with_pieces=True)
                textval = "".join([el["piece"] for el in rendered])
                bos_token = textval[:textval.find("<<<<USER>>>>")]
                if len(resp.get("bos_token","")) <= 0:
                    resp["bos_token"] = bos_token

            except:
                pass

        self.context_size = max_context
        self.server_props = resp
        return resp

    def _ricevi(self, req_params, pass_raw, callback):
        ret = []
        with self.connetion_semaphore:
            with requests.post(**req_params) as r1:
                a = 1
                for line in r1.iter_lines():
                    # filter out keep-alive new lines
                    a = a + 1
                    if line:
                        decoded_line = line.decode('utf-8')
                        json_decoded = json.loads(decoded_line[6:])
                        if ("stop" not in json_decoded) or json_decoded["stop"]:
                            self.prompt_metadata = json_decoded

                        if "truncated" in json_decoded and (json_decoded["truncated"] or False):
                            del json_decoded["prompt"]
                            print(json.dumps(json_decoded, indent=4))

                            raise Exception("truncated")
                        if "content" not in json_decoded:
                            print(json_decoded)

                        if pass_raw and len(json_decoded["content"]) > 0:
                            tmp_res = json_decoded['completion_probabilities']
                            # print(tmp_res)
                            if len(tmp_res) == 0:
                                continue
                            tmp_res = tmp_res[0]["probs"]
                            tmp_res = [(el["tok_str"], el["prob"]) for el in tmp_res]
                            tmp_res = str(tmp_res) + "\n"
                            #
                        else:
                            tmp_res = json_decoded["content"]
                        if callback:
                            callback(tmp_res)
                        if len(tmp_res) > 0:
                            ret.append(tmp_res)

        if self.prompt_metadata.get("stopped_eos", False):
            eos_tokens = ["<|endoftext|>"]
            if len(ret) > 0 and ret[-1] in eos_tokens:
                ret = ret[:-1]
        retstring = "".join(ret)
        return retstring, len(ret)

    def tokenize(self, p, add_special=False, with_pieces=False):
        url = self.base_url + "/tokenize"
        a = {}
        a["content"] = p
        a["add_special"] = add_special
        if with_pieces:
            a["with_pieces"] = with_pieces
        js = json.dumps(a)
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, data=js, headers=headers)
        r1 = r.text
        r2 = r1
        r3 = json.loads(r2)
        r4 = r3["tokens"]
        # print("tokens: ", len(r4))
        return r4

    def apply_template(self, messages,*args, **kwargs):
        url = self.base_url + "/apply-template"
        a = {}
        a["messages"] = messages

        js = json.dumps(a)
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, data=js, headers=headers)
        r1 = r.text
        r2 = r1
        r3 = json.loads(r2)
        r4 = r3["prompt"]
        # print("tokens: ", len(r4))
        return r4

    def detokenize(self, p):
        url = self.base_url + "/detokenize"
        a = {}
        a["tokens"] = p
        js = json.dumps(a)
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, data=js, headers=headers)
        r1 = r.text
        r2 = r1
        r3 = json.loads(r2)
        # print(r3)
        return r3

    def _send_prompt_text(self, p, params, callback, send_tokenized=True):
        tokens = self.tokenize(p)
        # detokenized = self.detokenize(tokens)

        a = merge_params(self.default_params, params)
        if send_tokenized:
            a["prompt"] = tokens
        else:
            a["prompt"] = p

        requested_num_tokens_answer = a.get("n_predict",1024)
        if len(tokens) + requested_num_tokens_answer >= self.context_size:
            raise Exception("context size exceeded: " + str(len(tokens)) + " + " + requested_num_tokens_answer)

        # a = {"messages":p}
        js = json.dumps(a)
        # print(a,"\n-\n" + p + "-")
        url = self.base_url + "/completion"
        headers = {"Content-Type": "application/json"}

        data = js
        pass_raw = "n_probs" in a

        req_params = {"url": url, "data": data, "headers": headers, "stream": True}
        g, actual_num_tokens_answer = self._ricevi(req_params, pass_raw, callback)

        if len(tokens) + actual_num_tokens_answer >= self.context_size:
            raise Exception("After inference, context size exceeded: " + str(len(tokens)) + " + " + actual_num_tokens_answer)

        return g

    def _send_prompt_builder(self, p, params, callback):
        prompt = p._build(self.formatter)
        use_template = self.formatter.use_template
        send_tokenized = not use_template
        return self._send_prompt_text(prompt, params, callback, send_tokenized=send_tokenized)

    def apply_format_templates(self, prompt):
        return self.formatter.apply_format_templates(prompt)

    def send_prompt(self, p, params=None, callback=None):
        if params is None:
            params = self.client_parameters
        if isinstance(p, PromptBuilder):
            return self._send_prompt_builder(p, params, callback)
        else:
            return self._send_prompt_text(p, params, callback)