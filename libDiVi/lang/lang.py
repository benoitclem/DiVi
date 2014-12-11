
from pycparser import c_parser
import re

class lang:
	
	def getFunctions(self,data):
		return None

class c(lang):
	def __init__(self):
		self.parser = c_parser.CParser()
		self.funcRule = '(?P<return>\w+)\s*(?P<name>\w+)\s?\((?P<args>(?P<arg>\w+\s*[*]?\s*\w+(,\s?)?)+)?\)'
		self.argRule = '(?P<type>\w+)\s*(?P<pointer>[*])?\s*(?P<name>\w+)'

	def matchBasicFunction(self,data):
		m = re.match(self.funcRule,data)
		if m:
			f = m.groupdict()
			print(f)
			del f['arg']
			if f['return'][:3] == 'int':
				f['return'] = int
			elif f['return'][:4] == 'float':
				f['return'] = float
			if f['args']:
				args = [arg.strip() for arg in f['args'].split(',')]
				targs = []
				for arg in args:
					p = {}
					m = re.match(self.argRule,arg)
					a = m.groupdict()
					if a['type'] == 'int':
						a['type'] = int
					elif a['type'] == 'float':
						a['type'] == float
					targs.append(a)
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
