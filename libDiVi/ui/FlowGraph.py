
from gi.repository import Gtk, Gdk

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

	MODE_BLOCK = 98
	MODE_CIRCLE = 99

	def __init__(self, name, parent = None, style = None):
		Gtk.DrawingArea.__init__(self)
		self.drag_dest_set(Gtk.DestDefaults.ALL, [Gtk.TargetEntry('STRING', Gtk.TargetFlags.SAME_APP, 0)], Gdk.DragAction.COPY)
		self.connect('drag-data-received', self.onDragDataReceived)
		
		if style == None:
			self.style = Classic()
		else:
			self.style = style

		self.name = name
		self.set_can_focus(True)
		self.myFocus = False

		self.blocks = []
		self.blockHovered = None
		self.flowGraphChanged = False

		self.cartouches = []
		for i in range(4):
			c = Cartouche(i)
			c.title = "cartouche %d" %i
			self.cartouches.append(c)

		self.selectionBox = None

		self.mode = 0

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
		# BackGround Drawing
		self.drawBackground(cr)
		# Block Drawing
		for block in self.blocks:
			block.draw(cr)
		# Cartouches Drawing
		for cartouche in self.cartouches:
			cartouche.draw(cr, self.get_allocation().width,self.get_allocation().height)
		# SelectionBox Drawing if available
		if self.selectionBox != None:
			self.selectionBox.draw(cr)

	def keyboardEvent(self, widget, event):
		if event.type == Gdk.EventType.KEY_PRESS:
			if self.myFocus:
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
				# We are idle and with BLOCK or CICLE activated
				if self.currentState == self.STATE_IDLE and\
					 (self.mode == self.MODE_BLOCK or self.mode == self.MODE_CIRCLE):
					block = None
					if self.mode == self.MODE_BLOCK:			
						block = Box(45,40,event.x,event.y,self.style)
					elif self.mode == self.MODE_CIRCLE:
						block = Circle(20,event.x,event.y,self.style)
					self.blocks.append(block)
					self.flowGraphChanged = True
					self.currentState |= self.STATE_BLOCK_HOVER + self.STATE_BLOCK_ADDED
					self.blockHovered = block
				# We are in BLOCK_HOVER State so click = selection
				elif self.currentState == self.STATE_BLOCK_HOVER:
					#self.unSelectAll()
					self.blockHovered.selected = True
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
							block.selected = True
					self.selectionBox = None
					self.flowGraphChanged = True
				# Remove flags
				else:
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
				for block in self.blocks:
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
			elif self.currentState == self.STATE_BLOCK_HOVER:
				# Moving out a block => deHOVER
				if not self.blockHovered.isInside(event.x,event.y):
					self.blockHovered.focused = False
					self.flowGraphChanged = True
					self.currentState &= ~(self.STATE_BLOCK_HOVER)
					self.blockHovered = None
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

	def haveFocus(self):
		for block in self.blocks:
			if block.focus:
				return block
		return None

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
