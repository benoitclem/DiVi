#!/usr/bin/env python3

from gi.repository import Gtk, Gdk, Gio

from libDiVi.ui.Styles import *
from libDiVi.ui.Drawables import *
from libDiVi.ui.Library import *
from libDiVi.ui.Project import *
from libDiVi.ui.FlowGraph import *

from libDiVi.lang.lang import *

'''
class DirReader:
	def __init__(self, path):
		self.path:
'''

class DiVi(Gtk.Window):

	def __init__(self, parent=None):
		Gtk.Window.__init__(self)
		try:
			self.set_screen(parent.get_screen())
		except AttributeError:
			self.connect('destroy', lambda *w: Gtk.main_quit())
			
			hb = Gtk.HeaderBar()
			hb.set_show_close_button(True)
			hb.props.title = self.__class__.__name__
			self.set_titlebar(hb)

			self.set_border_width(0)

			self.wSize = 1080
			self.hSize = 800 

			self.set_size_request(self.wSize, self.hSize)

			self.hpanpro = Gtk.Paned()
			self.hpanpro.set_position(self.wSize/4)
			self.add(self.hpanpro)

			pro = Project("Mon Projet","../project")
			self.hpanpro.add(pro)

			self.hpanlib = Gtk.Paned()
			self.hpanlib.set_position(self.wSize*2/4)
			self.hpanpro.add(self.hpanlib)

			self.fgs = Gtk.Notebook()
			lib = Library("lib")
			fg0 = FlowGraph("ONE",library=lib,language = c())
			fg1 = FlowGraph("TWO",library=lib,language = c())

			self.fgs.append_page(fg0,Gtk.Label(fg0.name))
			self.fgs.append_page(fg1,Gtk.Label(fg1.name))

			self.hpanlib.add(self.fgs)
			self.hpanlib.add(lib)

			self.show_all()

	def confUi():
		self.set_app_paintable(True)  
		screen = self.get_screen()

		visual = screen.get_rgba_visual()       
		if visual != None and screen.is_composited():
			self.set_visual(visual)      
			

def main():
	DiVi()
	Gtk.main()

if __name__ == '__main__':
	main()
