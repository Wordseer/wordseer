import json
# from jsonrpc import ServerProxy, JsonRpc20, TransportTcpIp
import jsonrpclib
from pprint import pprint


class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()
result = nlp.parse("Hello world!  It is so beautiful.")
pprint(result)

from nltk.tree import Tree
tree = Tree.parse(result['sentences'][0]['parsetree'])
pprint(tree)
