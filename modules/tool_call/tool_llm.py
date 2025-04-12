from .common import GenericTool,RunGraphMixin
import subprocess
import json



class AgentLLM(GenericTool,RunGraphMixin):
    tool_name = "llm"
    def __init__(self):
        pass

    def query_file(self,filename, question):
        """Uses a external agent to answer a {question} about the file saved in {filename}."""
        val = self._run_graph("graphs/query_file.txt",filename,question)
        val = val[0]
        return val

    def _query_information(self, question):
        """Queries a external agent to obtain information about everything."""
        val = ""
        return val

    def summarize(self,filename):
        """Uses a external agent to generate a plain-text summary of the content of a file."""
        val = self._run_graph("graphs/run_template.txt","templates/summarize_full.txt",filename)
        val = val[0]
        with open(tempfile.gettempdir() + "/summary.txt","w") as f:
            f.write(val)

        res = f"Summary of {filename} successfully generated and saved in " + tempfile.gettempdir() +"/summary.txt"
        if len(val) < 1024:
            res = res + "\n\n" + val
        return res