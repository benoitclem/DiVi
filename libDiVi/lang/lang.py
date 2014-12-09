
from pycparser import c_parser
import re

class lang:
	
	def getFunctions(self,data):
		return None

class c(lang):
	def __init__(self):
		self.parser = c_parser.CParser()
		self.funcRule = '(?P<return>\w+)\s*(?P<name>\w+)\s?\((?P<args>(?P<arg>\w+\s*\w+(,\s?)?)+)\)'

	def matchBasicFunction(self,data):
		m = re.match(self.funcRule,data)
		if m:
			f = m.groupdict()
			del f['arg']
			if f['return'][:3] == 'int':
				f['return'] = int
			else:
				f['return'] = None
			args = [arg.strip() for arg in f['args'].split(',')]
			targs = []
			for arg in args:
				if arg[:3] == 'int':
					targs.append(int)
				if arg[:5] == 'float':
					targs.append(float)
			f['args'] = targs
			return f
		else:
			return None

	def getFunctions(self, data):
		funcs = self.matchBasicFunction(data)
		if funcs:
			return [funcs]
		else:
			return []

class python(lang):

	def getFunctions(self, data):
		funcs = []
		return funcs
