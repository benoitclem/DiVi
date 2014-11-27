
from gi.repository import Gtk, Gdk
import os

class Library(Gtk.Paned):
	def __init__(self,path):

		self.path = path

		Gtk.Paned.__init__(self,orientation=Gtk.Orientation.VERTICAL)
		currentSize = self.get_allocation()
		self.set_position(400)

		browser = self.buildBrowser(path)
		self.browserTreeView.connect("row-activated", self.treeSelection)
		self.add(browser)

		editor = self.buildEditor()
		self.add(editor)

		self.populate(path)

	def populate(self, path, elem = None):
		name = os.path.basename(path)
		ldir = os.listdir(path)
		for e in ldir:
			subpath = path+'/'+e
			if os.path.isdir(subpath):
				subElem = self.browserStore.append(elem,[e,""])
				self.populate(subpath,subElem)
			else:
				self.browserStore.append(elem,[e,"desc"])

	def treeSelection(self, widget, row, col):
		# Recover the path from tremmodelrow
		path = self.getPathFromRow(row)
		print(path)
		# Display in editor
		self.displayInEditor(path)

	def getPathFromIter(self,base):
		path = []
		baseRow = base
		while True:
			name = self.browserStore.get_value(baseRow.iter,0)
			path.insert(0,name)
			parentRow = baseRow.parent
			if parentRow == None:
				break;
			else:
				baseRow = parentRow
		return self.path+'/'+os.path.join(*path)

	def getPathFromRow(self,row):
		path = []
		return self.getPathFromIter(self.browserStore[row])

	def displayInEditor(self,path):
		try:
			f = open(path,"r")
			self.editorTextBuffer.set_text(f.read())
			f.close()
			self.editorButtonSave.set_sensitive(True)
		except:
			self.editorButtonSave.set_sensitive(False)
			self.editorTextBuffer.set_text(">> This is a directory <<")

	def saveEditorToFile(self,path):
		f = open(path,"w")
		sIter = self.editorTextBuffer.get_start_iter()
		eIter = self.editorTextBuffer.get_end_iter()
		f.write(self.editorTextBuffer.get_text(sIter,eIter,False))
		f.close()

	def buildBrowser(self,path):
		self.browserGrid = Gtk.Grid()

		self.browserToolbar = Gtk.Toolbar()
		self.browserGrid.attach(self.browserToolbar,0,0,1,1)

		self.browserButtonNewFolder = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
		self.browserButtonNewCode = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
		self.browserToolbar.insert(self.browserButtonNewFolder,0)
		self.browserToolbar.insert(self.browserButtonNewCode,1)

		self.browserScrolledWindow = Gtk.ScrolledWindow()
		self.browserScrolledWindow.set_hexpand(True)
		self.browserScrolledWindow.set_vexpand(True)
		self.browserGrid.attach(self.browserScrolledWindow,0,1,1,1)

		self.browserStore = Gtk.TreeStore(str,str) # name / description
		self.browserTreeView = Gtk.TreeView(self.browserStore)
		self.browserTreeView.set_headers_visible(False)

		nameRenderer = Gtk.CellRendererText()
		nameColumn = Gtk.TreeViewColumn("name", nameRenderer, text = 0)
		self.browserTreeView.append_column(nameColumn)

		descRenderer = Gtk.CellRendererText()
		descColumn = Gtk.TreeViewColumn("description", descRenderer, text = 1)
		self.browserTreeView.append_column(descColumn)

		self.browserScrolledWindow.add(self.browserTreeView)

		return self.browserGrid


	def saveButtonClicked(self,widget):
		treeSelection = self.browserTreeView.get_selection()
		(model, i) = treeSelection.get_selected()
		print(model[i][0])
		path = self.getPathFromIter(model[i])
		print("saving now to " + path)
		self.saveEditorToFile(path)

	def buildEditor(self):
		self.editorGrid = Gtk.Grid()

		self.editorToolbar = Gtk.Toolbar()
		self.editorGrid.attach(self.editorToolbar,0,0,1,1)

		self.editorButtonSave = Gtk.ToolButton.new_from_stock(Gtk.STOCK_APPLY)
		self.editorButtonSave.set_sensitive(False)
		self.editorButtonSave.connect("clicked", self.saveButtonClicked)
		self.editorToolbar.insert(self.editorButtonSave,0)

		self.editorScrolledWindow = Gtk.ScrolledWindow()
		self.editorGrid.attach(self.editorScrolledWindow,0,1,1,1)

		self.editorScrolledWindow.set_hexpand(True)
		self.editorScrolledWindow.set_vexpand(True)
		self.editorTextView = Gtk.TextView()
		self.editorTextBuffer = self.editorTextView.get_buffer()
		self.editorTextBuffer.set_text("Test")
		self.editorScrolledWindow.add(self.editorTextView)

		return self.editorGrid

