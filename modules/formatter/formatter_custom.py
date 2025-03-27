from .parser import parse_raw, check_special_tokens
import copy


class FormatterCustom:
    def __init__(self):
        self.f = None

    def load_custom_model(self, model_name):
        #        print("Model name:",model_name)
        self.model_name = model_name
        formatter = {}
        formatter["enable_system"] = True
        if model_name.find("c4ai-command-r") >= 0:
            formatter = {}
            formatter["bos"] = "<BOS_TOKEN>"
            formatter["bor"] = "<|START_OF_TURN_TOKEN|><|"
            formatter["eor"] = "_TOKEN|>"

            formatter["eom"] = "<|END_OF_TURN_TOKEN|>"

            formatter["system_name"] = "SYSTEM"
            formatter["user_name"] = "USER"
            formatter["assistant_name"] = "CHATBOT"

            formatter["enable_system"] = False
            formatter["roles"] = ["raw", "system", "user", "assistant"]
        elif model_name.lower().find("qwen2") >= 0 or model_name.lower().find("qwq") >= 0:
            formatter = {}
            formatter["bos"] = ""
            formatter["bor"] = "<|im_start|>"
            formatter["eor"] = "\n"

            formatter["eom"] = "<|im_end|>\n"

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"

            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "user", "assistant", "system", "tool"]
            formatter["role_string"] = {"tool": formatter["bor"] + "user" + formatter["eor"]}

            if model_name.lower().find("qwq") >= 0:
                formatter["clean_thinking"] = True

        elif model_name.lower().find("phi-4") >= 0:
            formatter = {}
            formatter["bos"] = ""
            formatter["role_string"] = {"user": "<|im_start|>user<|im_sep|>", "assistant": "<|im_start|>assistant<|im_sep|>",
                                        "system": "<|im_start|>system<|im_sep|>"}
            formatter["role_eom"] = {"user": "<|im_end|>", "assistant": "<|im_end|>", "system": "<|im_end|>"}
            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "system", "user", "assistant"]

        elif model_name.lower().find("exaone") >= 0:
            formatter = {}
            formatter["bos"] = ""
            formatter["role_string"] = {"user": "[|user|]", "assistant": "[|assistant|]", "system": "[|system|]"}
            formatter["role_eom"] = {"user": "\n", "assistant": "[|endofturn|]\n", "system": "[|endofturn|]\n"}
            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "system", "user", "assistant"]
        elif model_name.lower().find("glm") >= 0 or model_name.lower().find("codegeex") >= 0:
            formatter = {}
            formatter["bos"] = "[gMASK]<sop>"
            formatter["bor"] = "<|"
            formatter["eor"] = "|>\n"

            formatter["eom"] = ""

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"

            formatter["enable_system"] = False
            formatter["roles"] = ["raw", "user", "assistant", "system"]
        elif model_name.lower().find("yuan") >= 0:
            formatter = {}
            formatter["bos"] = ""
            formatter["bos"] = ""
            formatter["bor"] = ""
            formatter["eor"] = ""

            formatter["eom"] = "\n"

            formatter["system_name"] = ""
            formatter["user_name"] = "Instruction: "
            formatter["assistant_name"] = "Response:\n"
            formatter["role_string"] = {"user": "", "assistant": "", "system": ""}
            formatter["role_eom"] = {"user": "<sep>", "assistant": "<n>", "system": "\n"}
            formatter["enable_system"] = False
            formatter["roles"] = ["raw", "system", "user", "assistant"]
        elif model_name.lower().find("platypus-yi") >= 0:
            formatter = {}
            formatter["bos"] = ""
            formatter["bos"] = ""
            formatter["bor"] = ""
            formatter["eor"] = ""

            formatter["eom"] = "\n"

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"
            formatter["role_string"] = {"user": "USER: ", "assistant": "ASSISTANT: ", "system": ""}
            formatter["role_eom"] = {"user": "\n", "assistant": "\n", "system": "\n"}

            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "system", "user", "assistant"]
        elif model_name.lower().find("deepseek") >= 0:
            formatter = {}
            formatter["bos"] = "<｜begin▁of▁sentence｜>"
            formatter["bor"] = ""
            formatter["eor"] = ""

            formatter["eom"] = "\n"

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"
            formatter["role_string"] = {"user": "User: ", "assistant": "Assistant: ", "system": ""}
            formatter["role_eom"] = {"user": "\n\n", "assistant": "<｜end▁of▁sentence｜>", "system": "\n\n"}

            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "system", "user", "assistant"]
        elif model_name.lower().startswith("internlm"):
            formatter = {}
            formatter["bos"] = "<s>"
            formatter["bor"] = "<|im_start|>"
            formatter["eor"] = "\n"

            formatter["eom"] = "<|im_end|>\n"

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"
            # formatter["role_string"] = {"user":"<|im_start|>user\n","assistant":"<|im_start|>assistant\n","system":""}
            # formatter["role_eom"] = {"user":"<|im_end|>\n","assistant":"<|im_end|>\n","system":""}

            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "system", "user", "assistant"]
        elif model_name.lower().startswith("solar"):
            formatter = {}
            formatter["bos"] = "<s>"
            formatter["bor"] = "<|im_start|> "
            formatter["eor"] = "\n"

            formatter["eom"] = "<|im_end|>\n"

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"
            # formatter["role_string"] = {"user":"<|im_start|>user\n","assistant":"<|im_start|>assistant\n","system":""}
            # formatter["role_eom"] = {"user":"<|im_end|>\n","assistant":"<|im_end|>\n","system":""}

            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "system", "user", "assistant"]
        elif model_name.lower().startswith("yi") or model_name.lower().startswith("faro") or model_name.lower().startswith("orca"):
            formatter = {}
            formatter["bos"] = "<|startoftext|>"
            formatter["bos"] = ""
            formatter["bor"] = "<|im_start|>"
            formatter["eor"] = "\n"

            formatter["eom"] = "<|im_end|>\n"

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"
            # formatter["role_string"] = {"user":"<|im_start|>user\n","assistant":"<|im_start|>assistant\n","system":""}
            # formatter["role_eom"] = {"user":"<|im_end|>\n","assistant":"<|im_end|>\n","system":""}

            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "system", "user", "assistant"]
        elif model_name.lower().startswith("calme"):
            formatter = {}
            formatter["bos"] = "<|startoftext|>"
            formatter["bos"] = ""
            formatter["bor"] = "<|im_start|>"
            formatter["eor"] = "\n"

            formatter["eom"] = "<|im_end|>\n"

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"
            formatter["role_string"] = {"user": "<|im_start|>user\n", "assistant": "<|im_start|>assistant\n", "system": ""}
            formatter["role_eom"] = {"user": "<|im_end|>\n", "assistant": "<|im_end|>\n", "system": "<|im_end|>\n"}

            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "system", "user", "assistant"]
        elif model_name.lower().startswith("wizardlm"):
            formatter = {}
            formatter["bos"] = ""
            formatter["bos"] = ""
            formatter["bor"] = ""
            formatter["eor"] = ""

            formatter["eom"] = "\n"

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"
            formatter["role_string"] = {"user": "USER: ", "assistant": "ASSISTANT: ", "system": ""}
            formatter["role_eom"] = {"user": " ", "assistant": "</s>", "system": " "}

            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "system", "user", "assistant"]
        elif model_name.lower().startswith("mistral-nemo"):
            formatter = {}
            formatter["bos"] = "<s>"
            formatter["bor"] = ""
            formatter["eor"] = ""

            formatter["eom"] = ""

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"
            formatter["role_string"] = {"user": "[INST] ", "assistant": "", "system": "[INST]"}
            formatter["role_eom"] = {"user": "[/INST]", "assistant": "", "system": "[/INST]"}

            formatter["enable_system"] = False
            formatter["roles"] = ["raw", "user", "assistant"]
        elif model_name.lower().startswith("mistral") or model_name.lower().startswith("mixtral"):
            formatter = {}
            formatter["bos"] = ""
            formatter["bor"] = ""
            formatter["eor"] = ""

            formatter["eom"] = ""

            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"
            formatter["role_string"] = {"user": "[INST]_", "assistant": "", "system": "[INST]"}
            formatter["role_eom"] = {"user": "[/INST]", "assistant": "", "system": "[/INST]"}

            formatter["enable_system"] = False
            formatter["roles"] = ["raw", "user", "assistant"]
        elif model_name.lower().startswith("gemma"):
            formatter = {}
            formatter["bos"] = "<bos>"
            formatter["bor"] = "<start_of_turn>"
            formatter["eor"] = "\n"

            formatter["eom"] = """<end_of_turn>\n"""
            formatter["system_name"] = "user"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "model"

            formatter["enable_system"] = False
            formatter["roles"] = ["raw", "user", "assistant"]
        elif ((model_name.lower().startswith("phi") and model_name.find("updated") >= 0) or
              model_name.lower().startswith("phi-3.1")):
            formatter = {}
            formatter["bos"] = "<s>"
            if model_name.lower().find("medium") >= 0:
                formatter["bos"] = "<s>"
            formatter["bor"] = "<|"
            formatter["eor"] = "|>\n"
            formatter["lf"] = "<0x0A>"
            formatter["eom"] = """<|end|>\n"""
            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"
            print("phi 3 updated")
            formatter["enable_system"] = True
            formatter["roles"] = ["raw", "system", "user", "assistant"]
            formatter["role_eom"] = {"user": "<|end|>\n", "assistant": "<|end|>\n", "system": "<|end|>\n"}
        elif model_name.lower().startswith("phi"):
            formatter = {}
            formatter["bos"] = "<s>"
            if model_name.lower().find("medium") >= 0:
                formatter["bos"] = "<s>"
            formatter["bor"] = "<|"
            formatter["eor"] = "|>\n"
            formatter["lf"] = "<0x0A>"
            formatter["eom"] = """<|end|>\n"""
            formatter["system_name"] = "user"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"

            formatter["enable_system"] = False
            formatter["roles"] = ["raw", "user", "assistant"]
            formatter["role_eom"] = {"user": "<|end|>\n", "assistant": "<|end|>\n", "system": "\n\n"}
        elif model_name.lower().startswith("openchat"):
            formatter["bos"] = "<|begin_of_text|>"  ##non capisco
            # formatter["bos"]=""
            formatter["bor"] = "<|start_header_id|>"
            formatter["eor"] = "<|end_header_id|>\n\n"

            formatter["eom"] = """<|eot_id|>"""
            # formatter["row"]=formatter["row1"] + formatter["row2"]
            formatter["roles"] = ["raw", "system", "user", "assistant"]
            formatter["system_name"] = "System"
            formatter["user_name"] = "GPT4 Correct User"
            formatter["assistant_name"] = "GPT4 Correct Assistant"
        else:  # llama

            formatter["bos"] = "<|begin_of_text|>"  ##non capisco
            # formatter["bos"]=""
            formatter["bor"] = "<|start_header_id|>"
            formatter["eor"] = "<|end_header_id|>\n\n"

            formatter["eom"] = """<|eot_id|>"""
            # formatter["row"]=formatter["row1"] + formatter["row2"]
            formatter["roles"] = ["raw", "system", "user", "assistant", "ipython", "call"]
            formatter["role_string"] = {"call": "<|start_header_id|>assistant<|end_header_id|>\n\n"}
            formatter["role_eom"] = {"call": "<|eom_id|>"}
            formatter["system_name"] = "system"
            formatter["user_name"] = "user"
            formatter["assistant_name"] = "assistant"

        return formatter

    def load_model(self, model_name):
        self.f = self.load_custom_model(model_name)
        return True


    def apply_format_templates(self, prompt):
        formatter = self.f
        a = prompt
        system_name = "system"
        if not formatter["enable_system"]:
            system_name = "user"
        a = a.replace("{p:bos}\n", formatter["bos"])
        a = a.replace("{p:bos}", formatter["bos"])
        if "bor" in formatter:
            a = a.replace("\n{p:system}\n", formatter["bor"] + formatter["system_name"] + formatter["eor"])
        if "eom" in formatter:
            a = a.replace("{p:eom}\n", formatter["eom"])
        if "bor" in formatter:
            a = a.replace("\n{p:user}\n", formatter["bor"] + formatter["user_name"] + formatter["eor"])
            a = a.replace("\n{p:assistant}\n", formatter["bor"] + formatter["assistant_name"] + formatter["eor"])
        return a

    def build_prompt(self, messages, force_system=False, **kwargs):
        messages = copy.deepcopy(messages)

        #remove thinking tokens if the assistant response is not a a prefill
        if self.f.get("clean_thinking"):
            assistant_messages = [el for el in messages[:-1] if el["role"] == "assistant"]
            for el in assistant_messages:
                el["content"] = el["content"].split("</think>")[-1].lstrip()

        prompt = self.build_handmade_prompt(messages, force_system)

        # workaround per deepseek
        if self.model_name.lower().startswith("deepseek") and prompt.endswith("Assistant: "):
            prompt = prompt[:-1]
            # workaround per deepseek
        if self.model_name.lower().startswith("glm") and prompt.endswith("<|assistant|>\n"):
            prompt = prompt[:-1]

        return prompt

    def build_handmade_prompt(self, messages, force_system=False):

        formatter = self.f
        skip_bos = False
        skip_final = False
        modifiers = [{"skip_preamble": False, "skip_postamble": False} for el in messages]
        fake_system = False

        if messages[0]["role"] == "raw":
            skip_bos = True
            if len(messages) > 1 and messages[1]["role"] == "assistant":
                modifiers[1]["skip_preamble"] = True
        if messages[-1]["role"] == "raw" or messages[-1]["role"] == "assistant":
            skip_final = True
        if messages[-1]["role"] == "assistant":
            modifiers[-1]["skip_postamble"] = True
            skip_postamble = len(messages) - 1
        if messages[0]["role"] == "system" and len(messages) > 1 and "system" not in formatter["roles"] and force_system:
            modifiers[0]["skip_postamble"] = True
            modifiers[1]["skip_preamble"] = True
            fake_system = True

        prompt = ""
        if not skip_bos:
            prompt = formatter["bos"]
        skip_last = False
        for i in range(len(messages)):
            el = messages[i]
            if el["role"] not in formatter["roles"]:
                if el["role"] == "system" and force_system:
                    pass
                elif el["role"] == "tool":
                    el["role"] = "user"
                else:
                    continue

            if el["role"] == "raw":
                val = self.apply_format_templates(el["content"])
                # print(val,end="")
                prompt = prompt + val
            else:
                if not modifiers[i]["skip_preamble"]:
                    if "role_string" in formatter and el["role"] in formatter["role_string"]:
                        prompt = prompt + formatter["role_string"][el["role"]]
                    else:
                        role_name = formatter["assistant_name"] if el["role"] == "assistant" else el["role"]
                        role_name = formatter["system_name"] if el["role"] == "system" else role_name
                        role_name = formatter["user_name"] if el["role"] == "user" else role_name
                        prompt = prompt + formatter["bor"] + role_name + formatter["eor"]
                prompt = prompt + el["content"]
                if i == 0 and fake_system:
                    prompt += "\n\n"
                if not modifiers[i]["skip_postamble"]:
                    if "role_eom" in formatter and el["role"] in formatter["role_eom"]:
                        prompt = prompt + formatter["role_eom"][el["role"]]
                    else:
                        prompt = prompt + formatter["eom"]
        if not skip_final:
            if "role_string" in formatter and "assistant" in formatter["role_string"]:
                prompt = prompt + formatter["role_string"]["assistant"]
            else:
                prompt = prompt + formatter["bor"] + formatter["assistant_name"] + formatter["eor"]
        if "lf" in formatter:
            pass
            # prompt = prompt.replace("\n",formatter["lf"])
        #        print(prompt)

        #    input_string += "\n"
        return prompt
