
from gi.repository import Gtk, Gdk
import pickle

from .Styles import Classic
from .Drawables import *

DRAG_ACTION = Gdk.DragAction.COPY


class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3

class FlowGraph(Gtk.DrawingArea):

	STATE_IDLE = 0x00
	STATE_BLOCK_HOVER = 0x01
	STATE_BLOCK_ADDED = 0x02
	STATE_BLOCK_MOVED = 0x04
	STATE_WIRE_EDIT   = 0x08

	MODE_BLOCK = 98
	MODE_CIRCLE = 115
	MODE_CONNECTION = 99
	MODE_PORT = 112
	MODE_LIBRARY = 108

	BOX_MASK = 0x01
	CIRCLE_MASK = 0x02
	WIRE_MASK = 0x04
	POINT_MASK = 0x08
	PORT_MASK = 0x10

	ALL_MASK = 0x1F
	WE_MASK = PORT_MASK 	# WireEdition

	def __init__(self, name, parent = None, style = None, library = None, language = None, fgdata = None):
		Gtk.DrawingArea.__init__(self)
		
		#self.drag_dest_set(Gtk.DestDefaults.ALL, [Gtk.TargetEntry('STRING', Gtk.TargetFlags.SAME_APP, 0)], Gdk.DragAction.COPY)
		#self.connect('drag-data-received', self.onDragDataReceived)
		
		if style == None:
			self.style = Classic()
		else:
			self.style = style

		self.name = name
		self.set_can_focus(True)
		self.myFocus = False

		if fgdata:
			self.blocks = pickle.loads(fgdata)
		else:
			self.blocks = []
		self.blockHovered = None
		self.flowGraphChanged = False

		self.cartouches = []
		for i in range(4):
			c = Cartouche(i)
			c.title = "cartouche %d" %i
			self.cartouches.append(c)

		self.boxSelected = False
		self.selectionBox = None
		self.wireEditionCurrentWire = None

		self.mode = 0

		self.library = library
		self.language = language

		self.currentState = self.STATE_IDLE
		self.leftClickState = 0
		self.leftClickWhere = None

		self.connect("draw", self.draw)
		self.connect("motion_notify_event", self.mouseEvent)

		self.connect("leave_notify_event", self.focusEvent)		
		self.connect("enter_notify_event", self.focusEvent)
		
		self.connect("button_press_event", self.mouseEvent)
		self.connect("button_release_event", self.mouseEvent)
		
		self.connect("key_press_event", self.keyboardEvent)
		self.connect("key_release_event", self.keyboardEvent)

		self.set_events(Gdk.EventMask.EXPOSURE_MASK
		| Gdk.EventMask.ENTER_NOTIFY_MASK
		| Gdk.EventMask.LEAVE_NOTIFY_MASK
		| Gdk.EventMask.BUTTON_PRESS_MASK
		| Gdk.EventMask.BUTTON_RELEASE_MASK
		| Gdk.EventMask.KEY_PRESS_MASK
		| Gdk.EventMask.KEY_RELEASE_MASK
		| Gdk.EventMask.POINTER_MOTION_MASK
		| Gdk.EventMask.POINTER_MOTION_HINT_MASK)

	def save(self):
		data = pickle.dumps(self.blocks)
		return data

	def setParser(self,parser):
		self.parser = parser

	def onDragDataReceived(self, widget, drag_context, x,y, data,info, time):
		print(widget, drag_context, x,y, data,info, time)

	def refresh(self):
		if self.flowGraphChanged:
			self.flowGraphChanged = False
			self.queue_draw()

	def drawBackground(self, cr):
		currentSize = self.get_allocation()
		cr.rectangle(0,0, currentSize.width,currentSize.height)
		cr.stroke_preserve()
		self.style.setBackGroundColor(cr)
		cr.fill()

	def draw(self, widget, cr):
		# Request the block to adjust their sizes
		for block in self.blocks:
			block.adjustBlockSize(cr)
		# BackGround Drawing
		self.drawBackground(cr)
		# Block Drawing (connections)
		for block in self.blocks:
			t = type(block)
			if (t ==  PortToPort):
				block.draw(cr)
		# Block Drawing (ports)
		for block in self.blocks:
			t = type(block)
			if (t ==  BoxPort) or (t == Port):
				block.draw(cr)
		# Block Drawing (Boxes)
		for block in self.blocks:
			t = type(block)
			if (t !=  BoxPort) and (t != Port) and (t !=  PortToPort):
				block.draw(cr)
		# Cartouches Drawing
		for cartouche in self.cartouches:
			cartouche.draw(cr, self.get_allocation().width,self.get_allocation().height)
		# SelectionBox Drawing if available
		if self.selectionBox != None:
			self.selectionBox.draw(cr)

	def update(self,path):
		if path:
			for i in range(len(self.blocks)):
				print(self.blocks[i].path)
				if self.blocks[i].path == path:
					self.flowGraphChanged = True
					print("Matched a block")
					# Get Block Parameters
					self.updateBlock(path,self.blocks[i])
			self.refresh()

	def updateBlock(self,path,block):
		func = self.getPrototype(path)
		if func:
			block.title = func[0]['name']
			print(len(block.subBlocks))
		
	def getPrototype(self,path):
		if path:
			f = open(path)
			data = f.read()
			f.close()
			if self.language:
				funcs = self.language.getFunctions(data)
				return funcs
		return None

	def code2block(self,path,x,y):
		funcs = self.getPrototype(path)
		if funcs:
			for func in funcs:
				print(func)
				b = self.buildBlock(x,y,func['name'],func['return'],func['args'])
				b[0].path = path
				return b

	# Use primitives to build a block
	def buildBlock(self,x,y,name,ret,args):
		b = Box(40,40,x,y,self.style, name = name)

		iPointers = []
		iNormals = []
		ap = []

		if args:
			# Compute number of inputing pointers
			for i in range(len(args)):
				if args[i]["pointer"]:
					iPointers.append(i)
				else:
					iNormals.append(i)
		
		# If pointers make the block orientation UP/DOWN
		#else RIGHT/LEFT (UP/DOWN used by pointers)
		if len(iPointers):
			orientInputs = Port.DIR_UP
			orientReturn = Port.DIR_DOWN
		else:
			orientInputs = Port.DIR_LEFT
			orientReturn = Port.DIR_RIGHT

		print(ret)
		if ret != 'void':
			# Put the return port
			p = BoxPort(b,orientReturn,(1,1),portType = ret, style = self.style, name = 'return',way = 'out')
			b.subBlocks.append(p)
			ap.append(p)
		
		if args:
			# Put the input ports (not pointers)
			for i in range(len(iNormals)):
				a = BoxPort(b,orientInputs,(i+1,len(iNormals)),portType = args[i]["type"],style=self.style,name=args[i]["name"], way = 'in')
				b.subBlocks.append(a)
				ap.append(a)

			# Put the input ports (pointers)
			for i in range(len(iPointers)):
				a = BoxPort(b,Port.DIR_LEFT,(i+1,len(iPointers)),portType = args[i]["type"],style=self.style,name=args[i]["name"],way = 'in')
				b.subBlocks.append(a)
				ap.append(a)
				a = BoxPort(b,Port.DIR_RIGHT,(i+1,len(iPointers)),portType = args[i]["type"],style=self.style,name=args[i]["name"],way = 'out')
				b.subBlocks.append(a)
				ap.append(a)

		return [b,ap]

	def keyboardEvent(self, widget, event):
		if event.type == Gdk.EventType.KEY_PRESS:
			if self.myFocus:
				# print(event.keyval)
				if event.keyval == 65535:		# ESC
					print("Delete")
					self.deleteSelectedBlocks()
				elif event.keyval == 65307:		# SUP
					self.mode = 0
					self.cartouches[3].title = "No Mode"
					self.flowGraphChanged = True
				else:
					self.mode = event.keyval
					self.cartouches[3].title = "Mode is %c" %event.keyval
					self.flowGraphChanged = True

			self.refresh()

	def focusEvent(self, widget, event):
		if event.type == Gdk.EventType.ENTER_NOTIFY:
			#print("entering :"+self.name)
			self.myFocus = True
			self.grab_focus()
		else: # this is probably useless
			self.myFocus = False

	def mouseEvent(self, widget, event):
		# print(event.type)
		# We press the mouse
		if event.type == Gdk.EventType.BUTTON_PRESS:
			if event.button == MouseButtons.LEFT_BUTTON:
				# Modify some internal variables relative to click
				self.leftClickState = 1
				self.leftClickWhere = [event.x, event.y]
				self.leftClickWhereBegin = [event.x, event.y]
				# We are idle and with BLOCK | CICLE | PORT | CONNECTION activated
				if self.currentState == self.STATE_IDLE and\
					 (self.mode == self.MODE_BLOCK or \
						self.mode == self.MODE_CIRCLE or\
						self.mode == self.MODE_CONNECTION or\
						self.mode == self.MODE_PORT or \
						self.mode == self.MODE_LIBRARY):
					block = None
					if self.mode == self.MODE_BLOCK:			
						block = Box(45,40,event.x,event.y,self.style)
					elif self.mode == self.MODE_CIRCLE:
						block = Circle(20,event.x,event.y,self.style)
					elif self.mode == self.MODE_CONNECTION:
						block = Connection(event.x,event.y,event.x+10,event.y-60,self.style)
					elif self.mode == self.MODE_PORT:
						block = Port(event.x,event.y,5,Port.DIR_UP,portType = int, style=self.style)
					elif self.mode == self.MODE_LIBRARY:
						if self.library:
							path = self.library.getSelectedPath()
							print(path)
							block = self.code2block(path,event.x,event.y);
					if block:
						# This is a meta block made of different blocks
						if type(block) == list:
							self.blocks.append(block[0])
							self.blockHovered = block[0]
							for ports in block[1]:
								self.blocks.append(ports)
						else:
							self.blocks.append(block)
							self.blockHovered = block
						self.flowGraphChanged = True
						self.currentState |= self.STATE_BLOCK_HOVER + self.STATE_BLOCK_ADDED

				# Well we are in Wire Edit mode
				if self.currentState & self.STATE_WIRE_EDIT:
					# When Hoverin something (in wire edit only port could be selected)
					# So we know here is a port that is hovered
					if self.currentState & self.STATE_BLOCK_HOVER:
						self.wireEditionCurrentWire.finish(self.blockHovered)
						# We did make the last connection
						self.currentState &= ~(self.STATE_WIRE_EDIT)
					else:
						p0 = Point(event.x,event.y)
						self.wireEditionCurrentWire.addPoint(p0)
						self.blocks.append(p0)
						p1 = Point(event.x,event.y)
						self.wireEditionCurrentWire.addPoint(p1)
						self.blocks.append(p1)
					self.flowGraphChanged = True

				# We are in BLOCK_HOVER State so click = selection
				elif self.currentState & self.STATE_BLOCK_HOVER:
					if not self.boxSelected:
						self.unSelectAll()
					# This is the part responsible for BoxPort unable to be selected
					# But allow it to create PortToPort connection
					if (type(self.blockHovered) == BoxPort) and \
							not (self.currentState & self.STATE_WIRE_EDIT):
						print("Entering WireEdition")
						block = Wire(self.blockHovered,self.style)
						self.wireEditionCurrentWire = block
						self.blocks.append(block)
						self.blocks += self.wireEditionCurrentWire.points
						self.currentState |= self.STATE_WIRE_EDIT
					else :
						self.recursiveSelect(self.blockHovered)
						"""
						self.blockHovered.selected = True
						for hoveredSubBlock in self.blockHovered.subBlocks:
							hoveredSubBlock.selected = True
						"""
					self.flowGraphChanged = True
				# Unselect all blocks when clicking with no mode activated			
				else:
					self.unSelectAll()


		# We release the mouse
		elif event.type == Gdk.EventType.BUTTON_RELEASE:
			if event.button == MouseButtons.LEFT_BUTTON:	
				# Modify some internal variables relative to click
				self.leftClickState = 0
				self.leftClickWhere = None
				self.leftClickWhereBegin = None
				# If we had a selection box, do the selection and clear the box
				if self.selectionBox != None:
					for block in self.blocks:
						if block.isInside(self.selectionBox.x0,self.selectionBox.y0,\
											self.selectionBox.x1,self.selectionBox.y1):
							if block.directSelectable:
								self.recursiveSelect(block)
					self.boxSelected = True
					self.selectionBox = None
					self.flowGraphChanged = True
				# Remove flags
				else:
					self.boxSelected = False
					if self.currentState & self.STATE_BLOCK_ADDED:
						self.currentState &= ~(self.STATE_BLOCK_ADDED)
					if self.currentState & self.STATE_BLOCK_MOVED:
						self.currentState &= ~(self.STATE_BLOCK_MOVED)
				"""
				elif not (self.currentState & self.STATE_BLOCK_ADDED) and\
					not  (self.currentState & self.STATE_BLOCK_MOVED):
					if self.currentState & self.STATE_BLOCK_HOVER:
						pass
				"""
		# We are moving
		elif event.type == Gdk.EventType.MOTION_NOTIFY:
			# ==== STATE TRANSITIONS ====
			if self.currentState == self.STATE_IDLE:
				# We begin a Selection box
				if (self.leftClickState == 1):
					x0 = self.leftClickWhereBegin[0]
					y0 = self.leftClickWhereBegin[1]
					self.selectionBox = SelectionBox(x0,y0,event.x,event.y,self.style)
					self.flowGraphChanged = True
				# We are idle search if we are not going to HOVER somethin'
				self.isHovering(event,self.ALL_MASK)
			if self.currentState & self.STATE_BLOCK_HOVER:
				# Moving out a block => deHOVER
				if not self.blockHovered.isInside(event.x,event.y):
					self.blockHovered.focused = False
					self.flowGraphChanged = True
					self.currentState &= ~(self.STATE_BLOCK_HOVER)
					self.blockHovered = None
			if self.currentState & self.STATE_WIRE_EDIT:
				lp = self.wireEditionCurrentWire.getLast3Points()
				# lp[0] never moves
				if(type(lp[0]) == BoxPort):
					(x,y) = lp[0].getConnectionPointXY()
				else:
					(x,y) = lp[0].getXY()
				dx = x - event.x
				dy = y - event.y
				if abs(dx) > abs(dy):
					lp[1].relocate(x-dx,y)
					lp[2].relocate(x-dx,y-dy)
				else:
					lp[1].relocate(x,y-dy)
					lp[2].relocate(x-dx,y-dy)
				# These 1 and 2 can move
				print(lp[1],lp[2])
				self.flowGraphChanged = True
				# Wile Wire edition, the hovering feature should work
				self.isHovering(event,self.WE_MASK)
			# ==== ACTIONS ====
			# We do the block move
			if self.leftClickState:
				dx = event.x-self.leftClickWhere[0]
				dy = event.y-self.leftClickWhere[1]
				self.leftClickWhere = [event.x,event.y]
				for block in self.blocks:
					if block.selected:
						block.relocate(dx,dy,"rel")
						self.currentState |= self.STATE_BLOCK_MOVED
						self.flowGraphChanged = True
			# We do the selectionBox Move
			if self.selectionBox:
				x0 = self.leftClickWhereBegin[0]
				y0 = self.leftClickWhereBegin[1]
				self.selectionBox = SelectionBox(x0,y0,event.x,event.y)
				self.flowGraphChanged = True

		self.refresh()

	def isHovering(self,event,mask):
		for block in self.blocks:
			if self.blockAuthorized(block,mask):
				if block.isInside(event.x,event.y):
					block.focused = True
					self.flowGraphChanged = True
					self.up(block)
					self.currentState |= self.STATE_BLOCK_HOVER
					self.blockHovered = block
					# only one block is hovered at a time 
					# this break is important as we are messing 
					# with blocks order in up() method
					break

	def blockAuthorized(self,block,mask):
		#print(block,"%02x"%mask)
		if (type(block) == Box) and (mask & self.BOX_MASK):
			return True
		elif (type(block) == Circle) and (mask & self.CIRCLE_MASK):
			return True
		elif (type(block) == Wire) and (mask & self.WIRE_MASK):
			return True
		elif (type(block) == Point) and (mask & self.POINT_MASK):
			return True
		elif ((type(block) == Port) or (type(block) == BoxPort)) and (mask & self.PORT_MASK):
			return True
		else:
			return False

	def haveFocus(self):
		for block in self.blocks:
			if block.focus:
				return block
		return None

	def recursiveSelect(self,block):
		# Since some of subblocks are no direct selectable,
		# select them by subblock mean
		block.selected = True
		for subBlock in block.subBlocks:
			self.recursiveSelect(subBlock)

	def isSelected(self):
		for block in self.blocks:
			if block.selected:
				return block
		return None

	def unSelectAll(self):
		for block in self.blocks:
			block.selected = False
		self.flowGraphChanged = True

	def up(self,block):
		self.blocks.append(self.blocks.pop(self.blocks.index(block)))

	def deleteSelectedBlocks(self):
		toDel = []
		for block in self.blocks:
			if block.selected:
				toDel.append(block)
		# print("Going to del %d blocks" %len(toDel))
		self.deleteBlocks(toDel)

	def deleteBlocks(self,toDel):
		for block in toDel:
			self.blocks.remove(block)
			self.flowGraphChanged = True

	def setLibrary(self,lib):
		self.library = lib

	def renderCode(self):
		for block in self.blocks:
			if block.directSelectable:
				print(block)




