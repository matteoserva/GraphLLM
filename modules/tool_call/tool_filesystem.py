from .common import GenericTool
import os
import tempfile

class AgentFilesystem(GenericTool):
    tool_name = "filesystem"

    def __init__(self):
        pass

    def ls(self,dirname):
        """
        Lists the content of a specified directory.

        Args:
            dirname (str): The directory path to list.

        Returns:
            str: A string containing the directory contents, including ".\n..\nciao.txt\npagina.md".
        """
        if not dirname.startswith("/tmp"):
            return "Error: You only have access to /tmp"
        try:
            files = os.listdir(dirname)
        except OSError as e:
            return f"Error accessing directory: {str(e)}"

        return "\n".join(files)

    def read_file(self,file_name):
        """Reads a file and outputs its content. This function fails if the file is too large."""
        if not file_name.startswith("/"):
            return "Error: You need to input a full path for the file_name"
        if not file_name.startswith(tempfile.gettempdir()):
            return "Error: You don't have access to that directory"
        file_stats = os.stat(file_name)
        file_size = file_stats.st_size

        if file_size > 2048:
            return f"file {file_name} is too large for read(). You should use the query_file() tool to query its content if the tool is available."
        with open(file_name,"r") as f:
            content = f.read()
        return content

    def write_file(self,file_name,file_content):
        """writes a file. files can only be created in /tmp"""
        if not file_name.startswith("/"):
            return "Error: You need to input a full path for the file_name"
        if not file_name.startswith(tempfile.gettempdir()):
            return "Error: You don't have access to that directory. please use " + tempfile.gettempdir()
        with open(file_name,"w") as f:
            f.write(file_content)
        return "file " + file_name + " created successfilly"

    def answer_file(self, file_name):
        """Returns a file as answer for the user question. The file must have been created previously"""
        with open(file_name,"r") as f:
            content = f.read()
        print ("------------- agent answer from file\n" + content)
        return content