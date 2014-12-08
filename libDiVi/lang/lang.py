
from pycparser import c_parser

class lang:
	
	def getFunctions(self,data):
		return None

class c(lang):
	def __init__(self):
		self.parser = c_parser.CParser()

	def getFunctions(self, data):
		try:
			ast = self.parser.parse(data)
			ast.show()
		except:
			print("Got ERROR in C Parsing")
		funcs = [{'name':'max','return':int,'args':[int,int]}]
		return funcs

class python(lang):

	def getFunctions(self, data):
		funcs = []
		return funcs
