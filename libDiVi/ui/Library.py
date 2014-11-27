
from gi.repository import Gtk, Gdk
import os

class NameChooserDialog(Gtk.Dialog):

	def __init__(self, parent, title, text, textBox):
		Gtk.Dialog.__init__(self, title, parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

		self.set_size_request(500, 100)

		label = Gtk.Label(text)
		box = self.get_content_area()
		box.add(label)
		textBox.set_alignment(0.5)
		box.add(textBox)
		self.show_all()


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

		self.populate(self.path)

	def populate(self, path, elem = None):
		
		name = os.path.basename(path)
		ldir = os.listdir(path)
		for e in ldir:
			subpath = path+'/'+e
			if os.path.isdir(subpath):
				subElem = self.browserStore.append(elem,[e,"Folder"])
				self.populate(subpath,subElem)
			else:
				self.browserStore.append(elem,[e,"Function"])

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

	def getSelectedIter(self):
		treeSelection = self.browserTreeView.get_selection()
		return treeSelection.get_selected()

	def getSelectedPath(self):
		(model, i) = self.getSelectedIter()
		if i:
			print(model[i][0])
			return self.getPathFromIter(model[i])
		else:
			return None

	def deleteSelectedItem(self):
		(model, i) = self.getSelectedIter()
		if i:
			self.browserStore.remove(i)

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

	def GiveName(self,what):
		entry = Gtk.Entry()
		chooserDialog = NameChooserDialog(None,"Chooser","Give a name to you new " + what,entry)
		response = chooserDialog.run()
		newName = entry.get_text()
		chooserDialog.destroy()
		return newName

	def NewFolder(self,widget):
		# Get the Selected Path and check Existence/File/Folder
		path = self.getSelectedPath()
		if path == None:
			path = self.path
		if os.path.isdir(path):
			# Give opportunity to user give a name
			newFolderName = self.GiveName("folder")
			# Create the Folder
			os.mkdir(path+"/"+newFolderName)
			# Add The folder to the treeStore
			(model,elem) = self.getSelectedIter()
			self.browserStore.append(elem,[newFolderName,"Folder"])
			print("Folder add to path:" + path)
		else:
			print("Select a Folder to add Folder")

	def NewCode(self,widget):
		path = self.getSelectedPath()
		if path == None:
			path = self.path
		if os.path.isdir(path):
			# Give opportunity to user give a name
			newFileName = self.GiveName("file")
			# Create the file
			f = open(path+'/'+newFileName,'w')
			f.write("New " + newFileName +" ready to be edited")
			f.close()
			# Add The file to the treeStore
			(model,elem) = self.getSelectedIter()
			self.browserStore.append(elem,[newFileName,"Function"])
			print("File add to path:" + path)

	def Remove(self,widget):
		# Get the selected path
		path = self.getSelectedPath()
		if path:
			# Warn user about deletion
			dialogWarning = Gtk.MessageDialog(None, 1, Gtk.MessageType.WARNING,Gtk.ButtonsType.OK_CANCEL,"You are about to delete the folowing object: " + path)
			dialogWarning.set_title("Warning")			
			response = dialogWarning.run()
			dialogWarning.destroy()
			# The user knowns what is about to appen
			if response == Gtk.ResponseType.OK:
				deleted = False
				# Check if we delete a directory or a file
				if os.path.isdir(path):
					try:
						# Try to remove the directory
						print("Removing path:" + path)
						os.rmdir(path)
						deleted = True
					except OSError as e:
						# Tell user that a not empty directory cannot be removed
						dialogWarning = Gtk.MessageDialog(None, 1, Gtk.MessageType.WARNING,Gtk.ButtonsType.OK,"Could not delete a directory that is not empty" + path)
						dialogWarning.set_title("Error")			
						dialogWarning.run()
						dialogWarning.destroy()
				else:
					# Remove file
					print("Removing path:" + path)
					os.remove(path)
					deleted = True
				# Remove from Store
				if deleted:
					self.deleteSelectedItem()
			elif response == Gtk.ResponseType.CANCEL:
				print("Aborting Remove")
		else:
			print("Select something to remove")
		pass

	def RefreshBrowser(self):
		self.browserStore.clear()
		self.populate(self.path)

	def buildBrowser(self,path):
		self.browserGrid = Gtk.Grid()

		self.browserToolbar = Gtk.Toolbar()
		self.browserGrid.attach(self.browserToolbar,0,0,1,1)

		self.browserButtonNewFolder = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
		self.browserButtonNewFolder.connect("clicked", self.NewFolder)
		self.browserButtonNewCode = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
		self.browserButtonNewCode.connect("clicked", self.NewCode)
		self.browserButtonRemove = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REMOVE)
		self.browserButtonRemove.connect("clicked", self.Remove)
		self.browserToolbar.insert(self.browserButtonNewFolder,0)
		self.browserToolbar.insert(self.browserButtonNewCode,1)
		self.browserToolbar.insert(self.browserButtonRemove,2)

		self.browserScrolledWindow = Gtk.ScrolledWindow()
		self.browserScrolledWindow.set_hexpand(True)
		self.browserScrolledWindow.set_vexpand(True)
		self.browserGrid.attach(self.browserScrolledWindow,0,1,1,1)

		self.browserStore = Gtk.TreeStore(str,str) # name / description
		self.browserTreeView = Gtk.TreeView(self.browserStore)
		self.browserTreeView.set_headers_visible(False)
		self.browserTreeView.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,\
														[('text/plain', 0, 0)],\
														Gdk.DragAction.DEFAULT | Gdk.DragAction.MOVE)
		self.browserTreeView.connect("drag-data-get", self.dragDataGetCb)

		nameRenderer = Gtk.CellRendererText()
		nameColumn = Gtk.TreeViewColumn("name", nameRenderer, text = 0)
		self.browserTreeView.append_column(nameColumn)

		descRenderer = Gtk.CellRendererText()
		descColumn = Gtk.TreeViewColumn("description", descRenderer, text = 1)
		self.browserTreeView.append_column(descColumn)

		self.browserScrolledWindow.add(self.browserTreeView)

		return self.browserGrid

	def dragDataGetCb(self,treeview, context, selection, info, timestamp):
		print(treeview, context, selection, info, timestamp)

	def saveButtonClicked(self,widget):
		path = self.getSelectedPath()
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

