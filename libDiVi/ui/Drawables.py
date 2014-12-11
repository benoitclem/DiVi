
import cairo
import math

from .Styles import Classic

gridSize = 1

class Block:
	def __init__(self,x = 0, y = 0,style = None):
		global gridSize
		if style == None:
			self.style = Classic()
		else:
			self.style = style
		self.movable = True
		self.focused = True
		# Tell the drawing surface block that direct selection is impossible.
		# Selection is ok by metablock mean only (like boxport)
		self.directSelectable = True; 
		self.selected = True
		# Some block are envolved in action so give them nice behavior when needed
		self.action = False
		# We don't apply the grid snapping when inserting block
		self.x = x
		self.y = y
		self.path = None
		self.error = None

		self.subBlocks = []

	def draw(self):
		print("Block object doesn't know how to draw itself")

	def relocate(self,x,y,method = "abs"):
		global gridSize
		if self.movable:
			if method == "rel":
				self.x += x
				self.y += y
				self.x = self.x - (self.x % gridSize)
				self.y = self.y - (self.y % gridSize)
			else:
				self.x = x - (x % gridSize)
				self.y = y - (y % gridSize)

	def getXY(self):
		return (self.x,self.y)

	def isInside(self,x,y,x0,y0):
		xM = max(x,x0)
		xm = min(x,x0)
		yM = max(y,y0)
		ym = min(y,y0)
		(x,y) = self.getXY()
		return (x<xM) and (xm<x) and (y<yM) and (ym<y)

	def adjustBlockSize(self,cr):
		pass

class Circle(Block):
	def __init__(self,radius,x,y,style = None):
		Block.__init__(self,x,y,style)
		self.radius = radius
		self.title = "CIR"

	def draw(self, cr):

		if self.focused:
			self.style.setFocusedLineWidth(cr)
		else:
			self.style.setLineWidth(cr)
		self.style.setLineColor(cr)
		
		cr.arc(self.x,self.y, self.radius, 0, 2*math.pi)
		cr.stroke_preserve()

		if self.selected:
			self.style.setSelectedFillColor(cr)
		else:
			self.style.setFillColor(cr)
		cr.fill()

		cr.select_font_facec("Cantarell", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)		
		cr.set_font_size(13)
		(x, y, width, height, dx, dy) = cr.text_extents(self.title)
		cr.move_to(self.x-width/2, self.y+height/2)   
		self.style.setTextColor(cr)
		cr.show_text(self.title)
		cr.fill()


	def isInside(self,x,y,x0 = None,y0 = None):
		if (x0 == None) or (y0 == None):
			return math.sqrt((x-self.x)*(x-self.x) + (y-self.y)*(y-self.y)) < self.radius
		else:
			return super(Circle,self).isInside(x,y,x0,y0)
		
class Box(Block):
	def __init__(self,xSize,ySize,x,y,style = None, name = None):
		Block.__init__(self,x,y,style)

		self.userxSize = xSize
		self.userySize = ySize
		self.xSize = self.userxSize
		self.ySize = self.userySize
		self.titleIsVisible = True
		if name:
			self.title = name
		else:
			self.title = "BOX"

	def setTitle(self, name):
		self.title = name

	def adjustBlockSize(self,cr):
		if self.titleIsVisible:
			cr.select_font_face("Cantarell", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)		
			cr.set_font_size(13)
			(x, y, width, height, dx, dy) = cr.text_extents(self.title)

			self.textWidth = width
			self.textHeight = height
		
			self.xSize = max(width + 20,self.userxSize)
			self.ySize = max(height + 20,self.userySize)
		else:
			self.xSize = self.userxSize
			self.ySize = self.userySize

	def draw(self, cr):

		if self.focused:
			self.style.setFocusedLineWidth(cr)
		else:
			self.style.setLineWidth(cr)
		self.style.setLineColor(cr)

		self.adjustBlockSize(cr)
		self.style.curvedRectangle(cr,self.x-self.xSize/2, self.y-self.ySize/2, self.xSize, self.ySize)
		cr.stroke_preserve()

		if self.selected:
			self.style.setSelectedFillColor(cr)
		else:
			self.style.setFillColor(cr)
		cr.fill()

		if self.titleIsVisible:
			cr.move_to(self.x-self.textWidth/2, self.y+self.textHeight/2)   
			self.style.setTextColor(cr)
			cr.show_text(self.title)
			cr.fill()

	def isInside(self,x,y,x0 = None,y0 = None):
		if (x0 == None) or (y0 == None):
			return (x < (self.x+self.xSize/2)) and  (x > (self.x-self.xSize/2)) and\
						(y < (self.y+self.ySize/2)) and  (y > (self.y-self.ySize/2))
		else:
			return super(Box,self).isInside(x,y,x0,y0)

class Port(Block):
	DIR_UP 		= 1
	DIR_DOWN 	= 2
	DIR_LEFT	= 3
	DIR_RIGHT	= 4

	SHAPE_ARROW  = 0
	def __init__(self, x, y, size, direction, portType = None, portShape = SHAPE_ARROW, style = None, name = None, way = "out"):
		Block.__init__(self,x,y,style)
		self.directSelectable = False
		self.direction = direction
		self.shape = portShape
		self.type = portType
		self.way = way
		self.size = size
		self.name = name

	def getXY(self):
		return (self.x,self.y)

	def draw(self, cr):
		# For Port the line width don't come with style
		if self.focused:
			cr.set_line_width(3)
		else:
			cr.set_line_width(2)
		if self.action:
			self.style.setActionLineColor(cr)
		else:
			self.style.setLineColor(cr)
		(x,y) = self.getXY()
		if self.shape == self.SHAPE_ARROW:
			if self.direction == self.DIR_UP:
				cr.move_to(x-self.size/2,y)
				cr.line_to(x,y-self.size)
				cr.line_to(x+self.size/2,y)
			elif self.direction == self.DIR_DOWN:
				cr.move_to(x-self.size/2,y)
				cr.line_to(x,y+self.size)
				cr.line_to(x+self.size/2,y)
			elif self.direction == self.DIR_LEFT:
				cr.move_to(x,y-self.size/2)
				cr.line_to(x-self.size,y)
				cr.line_to(x,y+self.size/2)
			elif self.direction == self.DIR_RIGHT:
				cr.move_to(x,y-self.size/2)
				cr.line_to(x+self.size,y)
				cr.line_to(x,y+self.size/2)
			cr.close_path()
			cr.set_line_join(cairo.LINE_JOIN_ROUND)
			cr.stroke_preserve()

			if self.type:
				if self.type == int:
					if self.selected:
						self.style.setSelectedFillColorInt(cr)
					else:
						self.style.setFillColorInt(cr)
			else:
				if self.selected:
					self.style.setSelectedFillColor(cr)
				else:
					self.style.setFillColor(cr)
			cr.fill()
			
		else:
			print("PORT TYPE is not defined... draw nothing")

	def isInside(self,x,y,x0 = None,y0 = None):
		if (x0 == None) or (y0 == None):
			(selfx,selfy) = self.getXY()
			if self.direction == self.DIR_UP:
				return (x < (selfx + self.size/2)) and  (x > (selfx - self.size/2)) and\
						(y < selfy) and  (y > (selfy - self.size))
			elif self.direction == self.DIR_DOWN:
				return (x < (selfx + self.size/2)) and  (x > (selfx - self.size/2)) and\
						(y < (selfy + self.size)) and  (y > selfy)
			elif self.direction == self.DIR_LEFT:
				return (x < (selfx)) and (x > selfx - self.size) and\
						(y < (selfy + self.size/2)) and (y > (selfy - self.size/2))
			elif self.direction == self.DIR_RIGHT:
				return (x < (selfx + self.size)) and (x > selfx) and\
						(y < (selfy + self.size/2)) and (y > (selfy - self.size/2))
		else:
			return super(Port,self).isInside(x,y,x0,y0)

class BoxPort(Port):
	def __init__(self, box, direction, num, portType = None, \
					portShape = Port.SHAPE_ARROW, style = None,name = None, way = 'out'):
		self.num = num
		self.box = box
		self.direction = direction
		Port.__init__(self, box.x, box.y, box.ySize/5, \
						direction, portType, portShape, style, name, way)
		self.directSelectable = False

	def setNum(self, num):
		self.num = num

	def getXY(self):
		(i,n) = self.num
		if self.direction == self.DIR_UP:
			offsetX = -self.box.xSize/2 + (self.box.xSize/(n*2))*((i*2)-1)
			offsetY = -self.box.ySize/2
		if self.direction == self.DIR_DOWN:
			offsetX = -self.box.xSize/2 + (self.box.xSize/(n*2))*((i*2)-1)
			offsetY = +self.box.ySize/2
		if self.direction == self.DIR_LEFT:
			offsetX = -self.box.xSize/2 
			offsetY = -self.box.ySize/2 + (self.box.ySize/(n*2))*((i*2)-1)
		if self.direction == self.DIR_RIGHT:
			offsetX = +self.box.xSize/2
			offsetY = -self.box.ySize/2 + (self.box.ySize/(n*2))*((i*2)-1)
		return (self.box.x+offsetX,self.box.y+offsetY)

	def getConnectionPointXY(self):
		(x,y) = self.getXY()
		if self.direction == self.DIR_UP:
			y -= self.size
		if self.direction == self.DIR_DOWN:
			y += self.size
		if self.direction == self.DIR_LEFT:
			x -= self.size
		if self.direction == self.DIR_RIGHT:
			x += self.size
		return(x,y)

class PortToPort(Block):
	def __init__(self,port1,port2,style = None,depth = None):
		Block.__init__(self,0,0,style)
		self.selected = False
		self.focused = False
		self.port1 = port1
		self.port2 = port2
		self.depth = depth

	def isValidConnection(self):
		return (self.port1.type != self.port2.type) or (self.port1.way == self.port2.way)

	def draw(self, cr):
		if self.selected or self.focused:
			self.style.setSelectedWireWidth(cr)
		else:
			self.style.setWireWidth(cr)
		self.error = self.isValidConnection()
		if not self.error:
			# for the connection we use the typed fill color
			if self.port1.type == int:
				self.style.setSelectedFillColorInt(cr)
			else:
				self.style.setLineColor(cr)
		else:
			self.style.setErrorColor(cr)
		# Compute nice curve points
		x0,y0 = self.port1.getConnectionPointXY()
		x3,y3 = self.port2.getConnectionPointXY()
		# Compute depth
		if self.depth == None:
			xM = max(x0,x3)
			yM = max(y0,y3)
			xm = min(x0,x3)
			ym = min(y0,y3)
			depth = math.sqrt((xM - xm) * (xM - xm) + (yM - ym) * (yM - ym))/1.5
		else:
			depth = self.depth
		if self.port1.direction == Port.DIR_UP:
			x1 = x0
			y1 = y0 - depth
		elif self.port1.direction == Port.DIR_DOWN:
			x1 = x0
			y1 = y0 + depth
		elif self.port1.direction == Port.DIR_LEFT:
			x1 = x0 - depth
			y1 = y0 
		elif self.port1.direction == Port.DIR_RIGHT:
			x1 = x0 + depth
			y1 = y0
		if self.port2.direction == Port.DIR_UP:
			x2 = x3
			y2 = y3 - depth
		elif self.port2.direction == Port.DIR_DOWN:
			x2 = x3
			y2 = y3 + depth
		elif self.port2.direction == Port.DIR_LEFT:
			x2 = x3 - depth
			y2 = y3 
		elif self.port2.direction == Port.DIR_RIGHT:
			x2 = x3 + depth
			y2 = y3
		cr.move_to(x0,y0)
		cr.curve_to(x1,y1,x2,y2,x3,y3)
		cr.stroke()

	def isInside(self,x,y,x0 = None,y0 = None):
		if (x0 == None) or (y0 == None):
			# don't know how to select a spline line with just one pixel
			return False
		else:
			return self.port1.isInside(x,y,x0,y0) and self.port2.isInside(x,y,x0,y0)
				

class Cartouche:
	TOP_LEFT = 0
	TOP_RIGHT = 1
	BOTTOM_LEFT = 2
	BOTTOM_RIGHT = 3

	# A cartouch is something that displays some useful information
	# xSize is the 
	def __init__(self, mode=TOP_LEFT, style = None):

		if style == None:
			self.style = Classic()
		else:
			self.style = style

		self.margin = 5
		self.mode = mode
		self.title = "CARTOUCHE"

	def computeRightPlace(self,width,height):
		if self.mode == self.TOP_LEFT:
			return (self.margin,height+self.margin)
		if self.mode == self.TOP_RIGHT:
			return (self.scrxSize-width-self.margin,height+self.margin)
		if self.mode == self.BOTTOM_LEFT:
			return (self.margin,self.scrySize-self.margin)
		if self.mode == self.BOTTOM_RIGHT:
			return (self.scrxSize-width-self.margin,self.scrySize-self.margin)
	
	def draw(self, cr, sxSize, sySize):
		self.scrxSize = sxSize
		self.scrySize = sySize

		cr.select_font_face("Cantarell", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)		
		cr.set_font_size(13)
		(x, y, width, height, dx, dy) = cr.text_extents(self.title)
		(x,y) = self.computeRightPlace(width,height)
		cr.move_to(x, y)   
		self.style.setTextColor(cr)
		cr.show_text(self.title)
		cr.fill()

class SelectionBox:
	def __init__(self, x0, y0, x1, y1, style = None):

		if style == None:
			self.style = Classic()
		else:
			self.style = style

		self.x0 = x0
		self.y0 = y0
		self.x1 = x1
		self.y1 = y1

	def draw(self, cr):
		self.style.setSelectionBoxLineWidth(cr)
		self.style.setSelectionBoxLineColor(cr)
		cr.rectangle(self.x0,self.y0,self.x1-self.x0,self.y1-self.y0)
		cr.stroke_preserve()
		self.style.setSelectionBoxFillColor(cr)
		cr.fill()
