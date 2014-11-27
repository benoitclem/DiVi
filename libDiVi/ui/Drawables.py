
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
		self.selected = True
		# We don't apply the grid snapping when inserting block
		self.x = x
		self.y = y

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

	def isInside(self,x,y,x0,y0):
		xM = max(x,x0)
		xm = min(x,x0)
		yM = max(y,y0)
		ym = min(y,y0)
		return (self.x<xM) and (xm<self.x) and (self.y<yM) and (ym<self.y)

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

		cr.select_font_face("Cantarell", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)		
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
	def __init__(self,xSize,ySize,x,y,style = None):
		Block.__init__(self,x,y,style)
		self.xSize = xSize
		self.ySize = ySize
		self.title = "BOX"

	def draw(self, cr):

		if self.focused:
			self.style.setFocusedLineWidth(cr)
		else:
			self.style.setLineWidth(cr)
		self.style.setLineColor(cr)

		cr.rectangle(self.x-self.xSize/2, self.y-self.ySize/2, self.xSize, self.ySize)
		cr.stroke_preserve()

		if self.selected:
			self.style.setSelectedFillColor(cr)
		else:
			self.style.setFillColor(cr)
		cr.fill()

		cr.select_font_face("Cantarell", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)		
		cr.set_font_size(13)
		(x, y, width, height, dx, dy) = cr.text_extents(self.title)
		cr.move_to(self.x-width/2, self.y+height/2)   
		self.style.setTextColor(cr)
		cr.show_text(self.title)
		cr.fill()

	def isInside(self,x,y,x0 = None,y0 = None):
		if (x0 == None) or (y0 == None):
			return (x < (self.x+self.xSize/2)) and  (x > (self.x-self.xSize/2)) and\
					(y < (self.y+self.ySize/2)) and  (y > (self.y-self.ySize/2))
		else:
			return super(Box,self).isInside(x,y,x0,y0)

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
