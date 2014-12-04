
class Classic:	

	def setFocusedLineWidth(self,cr):
		cr.set_line_width(6)

	def setLineWidth(self,cr):
		cr.set_line_width(4)

	def setFocusedLineColor(self,cr):
		cr.set_source_rgb(0.5, 0.2, 0.0)

	def setLineColor(self,cr):
		cr.set_source_rgb(0.7, 0.2, 0.0)

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

