

class lang:
	
	def getFunctions(self,data):
		return None

class c(lang):

	def getFunctions(self, data):
		funcs = [{'name':'max','return':int,'args':[int,int]}]
		return funcs

class python(lang):

	def getFunctions(self, data):
		funcs = []
		return funcs
