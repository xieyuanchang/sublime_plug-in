import sublime, sublime_plugin
#自动补分号
#view.run_command("append_mark")
class Append_markCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		rs = self.view.sel()
		for region in rs:
			str = self.view.substr(self.view.line(region)).rstrip()
			if str:
				if str[len(str)-1] != ";":
					str = str + ";"
				self.view.replace(edit, self.view.line(region), str)
				if self.view.line(region).end() < self.view.size():
					self.view.run_command("move",{"by": "lines","forward": True})
				else:
					self.view.run_command("insert",{"characters": "\n"})