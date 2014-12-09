
from gi.repository import Gtk, Gdk, GObject
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

class Project(Gtk.Grid):

	__gsignals__ = {
		"file-selected": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
	}

	def __init__(self,path):
		Gtk.Grid.__init__(self)
		self.path = path

		self.buildBrowser()
		
		BaseProject = self.ProjectStore.append(None,[Gtk.STOCK_OPEN,self.path])
		self.populateFolder(self.path,BaseProject)

	def populateFolder(self, path, elem = None):
		name = os.path.basename(path)
		ldir = os.listdir(path)
		for e in ldir:
			subpath = path+'/'+e		
			if os.path.isdir(subpath):
				subElem = self.ProjectStore.append(elem,[Gtk.STOCK_OPEN,e])
				self.populateFolder(subpath,subElem)
			else:
				subElem = self.ProjectStore.append(elem,[Gtk.STOCK_FILE,e])

	def buttonPressEvent(self, treeview, event):
		if event.button == 3: # right click
			print(int(event.x), int(event.y))
		    # do something with the selected path

	def buildBrowser(self):
		self.ProjectToolbar = Gtk.Toolbar()
		self.attach(self.ProjectToolbar,0,0,1,1)

		self.ProjectButtonNewFolder = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
		self.ProjectButtonNewFolder.connect("clicked", self.NewFolder)
		self.ProjectToolbar.insert(self.ProjectButtonNewFolder,0)

		self.ProjectButtonNewCode = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
		self.ProjectButtonNewCode.connect("clicked", self.NewCode)
		self.ProjectToolbar.insert(self.ProjectButtonNewCode,1)

		self.ProjectButtonRemove = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REMOVE)
		self.ProjectButtonRemove.connect("clicked", self.Remove)
		self.ProjectToolbar.insert(self.ProjectButtonRemove,2)

		self.ProjectScrolledWindow = Gtk.ScrolledWindow()
		self.ProjectScrolledWindow.set_hexpand(True)
		self.ProjectScrolledWindow.set_vexpand(True)
		self.attach(self.ProjectScrolledWindow,0,1,1,1)

		self.ProjectStore = Gtk.TreeStore(str,str)
		self.ProjectTreeView = Gtk.TreeView(self.ProjectStore)
		self.ProjectTreeView.set_headers_visible(False)
		self.ProjectTreeView.connect("row-activated", self.treeSelection)
		self.ProjectTreeView.connect('button-press-event' , self.buttonPressEvent)
		self.ProjectScrolledWindow.add(self.ProjectTreeView)

		pixbufRenderer = Gtk.CellRendererPixbuf()
		pixbufColumn = Gtk.TreeViewColumn("image", pixbufRenderer, stock_id=0)
		self.ProjectTreeView.append_column(pixbufColumn)

		nameRenderer = Gtk.CellRendererText()
		nameColumn = Gtk.TreeViewColumn("name", nameRenderer, text=1)
		self.ProjectTreeView.append_column(nameColumn)

	def treeSelection(self, widget, row, col):
		# Recover the path from tremmodelrow
		path = self.getPathFromRow(row)
		self.emit("file-selected",path)

	def getPathFromIter(self,base):
		path = []
		baseRow = base
		while True:
			name = self.ProjectStore.get_value(baseRow.iter,1)
			path.insert(0,name)
			parentRow = baseRow.parent
			if parentRow == None:
				break;
			else:
				baseRow = parentRow
		return os.path.join(*path)

	def getPathFromRow(self,row):
		path = []
		return self.getPathFromIter(self.ProjectStore[row])

	def getSelectedIter(self):
		treeSelection = self.ProjectTreeView.get_selection()
		return treeSelection.get_selected()

	def getSelectedPath(self):
		(model, i) = self.getSelectedIter()
		if i:
			# print(model[i][0])
			return self.getPathFromIter(model[i])
		else:
			return None

	def deleteSelectedItem(self):
		(model, i) = self.getSelectedIter()
		if i:
			self.ProjectStore.remove(i)

	def NewFolder(self,widget):
		# Get the Selected Path and check Existence/File/Folder
		path = self.getSelectedPath()
		if path == None:
			path = self.path
		if os.path.isdir(path):
			# Give opportunity to user give a name
			newFolderName = self.GiveName("folder")
			if newFolderName:
				# Create the Folder
				os.mkdir(path+"/"+newFolderName)
				# Add The folder to the treeStore
				(model,elem) = self.getSelectedIter()
				self.ProjectStore.append(elem,[Gtk.STOCK_OPEN,newFolderName])
				print("Folder add to path:" + path)
		else:
			print("Select a Folder to add Folder")

	def NewCode(self,widget):
		path = self.getSelectedPath()
		if path == None:
			path = self.path
		if os.path.isdir(path):
			# Give opportunity to user give a name
			newFileName = self.GiveName("file") + ".v"
			if newFileName:
				# Create the file
				f = open(path+'/'+newFileName,'w')
				#f.write("New " + newFileName +" ready to be edited")
				f.close()
				# Add The file to the treeStore
				(model,elem) = self.getSelectedIter()
				self.ProjectStore.append(elem,[Gtk.STOCK_FILE,newFileName])
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

	def GiveName(self,what):
		entry = Gtk.Entry()
		chooserDialog = NameChooserDialog(None,"Chooser","Give a name to you new " + what,entry)
		response = chooserDialog.run()
		newName = entry.get_text()
		chooserDialog.destroy()
		return newName
