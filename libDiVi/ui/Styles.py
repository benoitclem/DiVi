
class Classic:	

	def setFocusedLineWidth(self,cr):
		cr.set_line_width(6)

	def setLineWidth(self,cr):
		cr.set_line_width(4)

	def setSelectedWireWidth(self,cr):
		cr.set_line_width(4)

	def setFocusedWireWidth(self,cr):
		cr.set_line_width(4)

	def setWireWidth(self,cr):
		cr.set_line_width(2)

# LINE Color
	def setActionLineColor(self,cr):
		cr.set_source_rgb(0.2, 0.7, 0.0)

	def setFocusedLineColor(self,cr):
		cr.set_source_rgb(0.5, 0.2, 0.0)

	def setLineColor(self,cr):
		cr.set_source_rgb(0.289, 0.562, 0.847)
# END LINE

	def setSelectedFillColor(self,cr):
		cr.set_source_rgb(0.6, 0.6, 0.6)

	def setFillColor(self,cr):
		cr.set_source_rgb(0.8, 0.8, 0.8)

# TYPE Color

	def setSelectedFillColorInt(self,cr):
		cr.set_source_rgb(0.1, 0.6, 0.1)

	def setFillColorInt(self,cr):
		cr.set_source_rgb(0.2, 0.6, 0.2)

# END TYPE

	def setTextColor(self,cr):
		cr.set_source_rgb(0.1, 0.1, 0.1)

	def setSelectionBoxLineWidth(self,cr):
		cr.set_line_width(1)

	def setSelectionBoxLineColor(self,cr):
		cr.set_source_rgb(0.4, 0.4, 0.4)

	def setSelectionBoxFillColor(self,cr):
		cr.set_source_rgba(0.9, 0.9, 0.9, 0.3)

	def setBackGroundColor(self,cr):
		cr.set_source_rgb(1,1,1)

	def setErrorColor(self,cr):
		cr.set_source_rgba(0.9,0.1,0.2,0.6)

	def curvedRectangle(self,cr,x0,y0,width,height,radius=102):
		x1 = x0+width;
		y1 = y0+height;
		if (width/2)<radius:
			if (height/2)<radius:
				cr.move_to(x0, (y0 + y1)/2);
				cr.curve_to(x0 ,y0, x0, y0, (x0 + x1)/2, y0);
				cr.curve_to(x1, y0, x1, y0, x1, (y0 + y1)/2);
				cr.curve_to(x1, y1, x1, y1, (x1 + x0)/2, y1);
				cr.curve_to(x0, y1, x0, y1, x0, (y0 + y1)/2);
			else:
				cr.move_to(x0, y0 + radius);
				cr.curve_to(x0 ,y0, x0, y0, (x0 + x1)/2, y0);
				cr.curve_to(x1, y0, x1, y0, x1, y0 + radius);
				cr.line_to(x1 , y1 - radius);
				cr.curve_to(x1, y1, x1, y1, (x1 + x0)/2, y1);
				cr.curve_to(x0, y1, x0, y1, x0, y1- radius);
		else:
			if (height/2)<radius:
				cr.move_to(x0, (y0 + y1)/2);
				cr.curve_to(x0 , y0, x0 , y0, x0 + radius, y0);
				cr.line_to(x1 - radius, y0);
				cr.curve_to(x1, y0, x1, y0, x1, (y0 + y1)/2);
				cr.curve_to(x1, y1, x1, y1, x1 - radius, y1);
				cr.line_to(x0 + radius, y1);
				cr.curve_to(x0, y1, x0, y1, x0, (y0 + y1)/2);
			else:
				cr.move_to(x0, y0 + radius);
				cr.curve_to(x0 , y0, x0 , y0, x0 + radius, y0);
				cr.line_to(x1 - radius, y0);
				cr.curve_to(x1, y0, x1, y0, x1, y0 + radius);
				cr.line_to(x1 , y1 - radius);
				cr.curve_to(x1, y1, x1, y1, x1 - radius, y1);
				cr.line_to(x0 + radius, y1);
				cr.curve_to(x0, y1, x0, y1, x0, y1- radius);
		cr.close_path();

