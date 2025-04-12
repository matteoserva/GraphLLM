from .common import GenericTool,RunGraphMixin
import subprocess
import json
import tempfile

class AgentWeb(GenericTool):
    tool_name = "web"
    def __init__(self):
        pass

    def download(self,url):
        """Downloads the webpage at url {url} and saves its html content to a temporary file"""
        fullargs = ["python3", "extras/scraper/scrape.py", url]
        result = subprocess.run(fullargs, capture_output=True, text=True, input="")
        return "Webpage at url " + url + " successfully saved at " + tempfile.gettempdir() + "/pagina.md"

    def web_search(self,query):
        """performs a web search using a search engine."""
        modified_query = query.replace(" ","+")
        search_url = "https://lite.duckduckgo.com/lite/?q=" + modified_query + ""
        self.download(search_url)
        fullargs = ["-s", "```", "graphs/run_template.txt","templates/extract_search_results.txt",tempfile.gettempdir() + "/pagina.md","5"]
        val = self._run_graph(*fullargs)
        v2 = val[0]
        return v2
