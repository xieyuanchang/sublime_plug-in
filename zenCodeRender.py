import sublime, sublime_plugin,re,string

class ZenCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		rs = self.view.sel()
		for region in rs:
			str = self.view.substr(self.view.line(region)).replace("\n","").replace("\r","").strip()
			html = ""
			try:
				html = self.expression(str).html()
			except Exception:
				print("invalid syntax :" + str)
			else:
				self.view.replace(edit, self.view.line(region), html)

	def _expression(self,reader):
		tk = reader.read()
		maker = atomMaker()
		if tk.T == tokenType.NULL:
			return None
		
		curAtom = None
		if tk.value == "(":
			curAtom = self._expression(reader)
			tk = reader.read()
			if tk.value != ")":
				print("invalid syntax :after [" + curAtom.me.value + "] ) is expected ,but It is [" + tk.value + "]")
		else:
			curAtom = maker.newAtom(tk)

		ret = curAtom
		while True:
			tk = reader.read()
			if tk.T == tokenType.NULL:
				break
			if tk.T == tokenType.SPLIT:
				if tk.value == ")":
					reader.reader.unread()
					break
				a = self._expression(reader)
				if tk.value == "+":
					curAtom.next = a
					curAtom = a
				elif tk.value == ">":
					curAtom.addChild(a)
					curAtom = a
			else:
				print("invalid syntax :[" + tk.value + "] is not a SPLIT")
		return ret
	
	def expression(self,zencode):
		reader = token_reader(zencode)
		return self._expression(reader)
		

		
class tokenType:
	"""Type of Token"""
	NULL = 0
	ATOM = 1
	SPLIT = 2
		
		
class token:
	"""Token object"""
	def __init__(self, a,b):
		self.T = a
		self.value = b

class string_reader:
	"""String Reader"""
	def __init__(self, str):
		self.data = str
		self.i = 0
	
	def read(self):
		if self.i < len(self.data):
			ret = self.data[self.i]
			self.i = self.i + 1
			return ret
		else:
			return ""

	def unread(self):
		if  self.i > 0:
			self.i = self.i - 1

class token_reader:
 		"""Token Reader"""
 		def __init__(self, str):
 			self.reader = string_reader(str)

 		def read(self):
 			tk = token(tokenType.NULL,"")
 			b = self.reader.read()
 			if b == "":
 				return tk 
 			if b >= "A"	and b <= "z":
 				tmp = b
 				while True:
 					b = self.reader.read()
 					if b =="":
 						break
 					flg = True
 					if b >= "A"	and b <= "z":
 						tmp = tmp + b
 						flg = False
 					if b >= "0"	and b <= "9":
 						tmp = tmp + b
 						flg = False
 					if b == "*"	or b == "." or b == "#":
 						tmp = tmp + b
 						flg = False
 					if flg:
 						self.reader.unread()
 						break
 				tk.T = tokenType.ATOM
 				tk.value = tmp
 				return tk

 			if b == '+' or b == '>' or b == '(' or b == ')':
 				tk.value = b
 				tk.T = tokenType.SPLIT
 				return tk

 			return None

class atomMaker:
 	"""docstring for atomMaker"""
 	def newAtom(self,tk):
 		if tk.T == tokenType.ATOM:
 			atm = atom(tk)
 			pattern = re.compile(r'^[A-z]+[0-9]*')
 			atm.tag = pattern.match(tk.value).group(0)
 			# deal #
 			if tk.value.find("#") != -1 :
 				arr = tk.value.split("#")
 				atm.id = " id=\"" + pattern.match(arr[1]).group(0) + "\""
 			# deal .
 			if tk.value.find(".") != -1 :
 				arr = tk.value.split(".")
 				atm.cls = " class=\"" + pattern.match(arr[1]).group(0) + "\""
 			# deal *
 			if tk.value.find("*") != -1 :
 				arr = tk.value.split("*")
 				atm.num = string.atoi(arr[1])
 			return atm
 		else:
 			return None
 		
class atom:
	"""docstring for atom"""
	def __init__(self, tk):
		super(atom, self).__init__()
		self.me = tk
		self.children = []
		self.next = None
		self.tag = ""
		self.id = ""
		self.cls = ""
		self.num = 1

	def  addChild(self,tk):
		self.children.append(tk)

	def html(self):
		ret = "<" + self.tag + self.id + self.cls + ">"
		for child in self.children:
			ret = ret + child.html()
		ret = ret + "</" + self.tag + ">"

		tmp = ret 
		i = self.num
		while i > 1:
			ret = ret + tmp
			i = i - 1

		if self.next != None:
			ret = ret + self.next.html()

		return ret