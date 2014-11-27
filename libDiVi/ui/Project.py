
from gi.repository import Gtk, Gdk

class Project(Gtk.TreeView):
	def __init__(self,name,path):
		self.name = name
		self.store = Gtk.TreeStore(str,str) # name / description
		self.path = path

		Gtk.TreeView.__init__(self,self.store)
		self.set_headers_visible(False)

		pixbufRenderer = Gtk.CellRendererPixbuf()
		pixbufColumn = Gtk.TreeViewColumn("image", pixbufRenderer, stock_id=0)
		self.append_column(pixbufColumn)

		nameRenderer = Gtk.CellRendererText()
		nameColumn = Gtk.TreeViewColumn("name", nameRenderer, text=1)
		self.append_column(nameColumn)

		self.populate()

	def populate(self):
		i = self.store.append(None,[Gtk.STOCK_HARDDISK,self.name])
		self.store.append(i,[Gtk.STOCK_FILE,"file1"])
		self.store.append(i,[Gtk.STOCK_FILE,"file1"])
