#!/usr/bin/env python3

from gi.repository import Gtk, Gdk, Gio, GObject

from libDiVi.ui.Styles import *
from libDiVi.ui.Drawables import *
from libDiVi.ui.Library import *
from libDiVi.ui.Project import *
from libDiVi.ui.FlowGraph import *

from libDiVi.lang.lang import *

import os

'''
class DirReader:
	def __init__(self, path):
		self.path:
'''

class TabLabel(Gtk.Box):
	__gsignals__ = {
		"close-clicked": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
	}

	def __init__(self, label_text):
		Gtk.Box.__init__(self)
		self.set_orientation(Gtk.Orientation.HORIZONTAL)
		self.set_spacing(5) # spacing: [label|5px|close] 

		# label 
		label = Gtk.Label(label_text)
		self.pack_start(label, True, True, 0)

		# close button
		button = Gtk.Button()
		button.set_relief(Gtk.ReliefStyle.NONE)
		button.set_focus_on_click(False)
		button.add(Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU))
		button.connect("clicked", self.button_clicked)
		self.pack_start(button, False, False, 0)

		self.show_all()

	def button_clicked(self, button, data=None):
		self.emit("close-clicked")

class DiVi(Gtk.Window):

	def __init__(self, parent=None):
		Gtk.Window.__init__(self)
		try:
			self.set_screen(parent.get_screen())
		except AttributeError:
			self.connect('destroy', lambda *w: Gtk.main_quit())
			
			# The Header Bar Stuffs
			hb = Gtk.HeaderBar()
			hb.set_show_close_button(True)
			hb.props.title = self.__class__.__name__
			self.set_titlebar(hb)

			box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
			Gtk.StyleContext.add_class(box.get_style_context(), "linked")

			button = Gtk.Button()
			button.add(Gtk.Label("  Open  "))
			box.add(button)

			button = Gtk.Button()
			button.add(Gtk.Arrow(Gtk.ArrowType.DOWN, Gtk.ShadowType.NONE))
			box.add(button)

			hb.pack_start(box)
			# end
			
			self.set_border_width(0)

			self.wSize = 1080
			self.hSize = 800 

			self.set_size_request(self.wSize, self.hSize)

			self.hpanpro = Gtk.Paned()
			self.hpanpro.set_position(self.wSize/4)
			self.add(self.hpanpro)

			pro = Project("./project")
			pro.connect("file-selected",self.projectFileSelected)
			self.hpanpro.add(pro)

			self.hpanlib = Gtk.Paned()
			self.hpanlib.set_position(self.wSize*2/4)
			self.hpanpro.add(self.hpanlib)

			self.fgs = Gtk.Notebook()
			self.lib = Library("lib")
			self.language = c()
			self.hpanlib.add(self.fgs)
			self.hpanlib.add(self.lib)

			self.show_all()

	def confUi():
		self.set_app_paintable(True)  
		screen = self.get_screen()

		visual = screen.get_rgba_visual()       
		if visual != None and screen.is_composited():
			self.set_visual(visual)

	def projectFileSelected(self,widget,path):
		if os.path.isfile(path):
			fg = FlowGraph(path,library=self.lib,language = self.language)
			tab = TabLabel(fg.name)
			tab.connect("close-clicked",self.closeTab,self.fgs,fg)
			self.fgs.append_page(fg,tab)
			self.fgs.show_all()

	def closeTab(self, label, notebook, widget):
		notebook.remove_page(notebook.page_num(widget))
		print('Close')

def main():
	DiVi()
	Gtk.main()

if __name__ == '__main__':
	main()
