"""PDF generation service for the Book Creator module."""

import io
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from langflow.services.database.models.book import Book, BookCover, BookInterior, BookPage, BookTemplate


class BookPDFGenerator:
    """PDF generator for books."""

    def __init__(
        self,
        book: Book,
        cover: Optional[BookCover] = None,
        interior: Optional[BookInterior] = None,
        pages: List[BookPage] = None,
        templates: Dict[str, BookTemplate] = None,
    ):
        """Initialize the PDF generator.
        
        Args:
            book: The book to generate a PDF for
            cover: The book cover
            interior: The book interior
            pages: The book pages
            templates: A dictionary of templates by ID
        """
        self.book = book
        self.cover = cover
        self.interior = interior
        self.pages = pages or []
        self.templates = templates or {}
        
        # Register custom fonts
        self._register_fonts()
        
        # Set up page size
        self.page_size = self._get_page_size()
        
        # Set up styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _register_fonts(self):
        """Register custom fonts for use in the PDF."""
        # Standard fonts are already registered in ReportLab
        # For custom fonts, we would register them here
        # Example:
        # pdfmetrics.registerFont(TTFont('CustomFont', 'path/to/font.ttf'))
        pass

    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="BookTitle",
                parent=self.styles["Title"],
                fontSize=36,
                leading=44,
                alignment=1,  # Center
            )
        )
        
        # Author style
        self.styles.add(
            ParagraphStyle(
                name="BookAuthor",
                parent=self.styles["Normal"],
                fontSize=24,
                leading=30,
                alignment=1,  # Center
            )
        )
        
        # Header style
        self.styles.add(
            ParagraphStyle(
                name="Header",
                parent=self.styles["Normal"],
                fontSize=10,
                leading=12,
                alignment=1,  # Center
            )
        )
        
        # Footer style
        self.styles.add(
            ParagraphStyle(
                name="Footer",
                parent=self.styles["Normal"],
                fontSize=10,
                leading=12,
                alignment=1,  # Center
            )
        )

    def _get_page_size(self) -> Tuple[float, float]:
        """Get the page size based on book dimensions."""
        width = self.book.dimensions.get("width", 8.5)
        height = self.book.dimensions.get("height", 11)
        units = self.book.dimensions.get("units", "in")
        
        if units == "in":
            return (width * inch, height * inch)
        elif units == "mm":
            return (width * mm, height * mm)
        else:
            # Default to letter if units not recognized
            return letter

    def _create_document(self, buffer: io.BytesIO, include_bleed: bool = False) -> BaseDocTemplate:
        """Create a document template with the appropriate page size and margins.
        
        Args:
            buffer: The buffer to write the PDF to
            include_bleed: Whether to include bleed area
            
        Returns:
            A document template
        """
        page_width, page_height = self.page_size
        
        # Add bleed if requested
        if include_bleed:
            bleed = 0.125 * inch if self.book.dimensions.get("units") == "in" else 3 * mm
            page_width += 2 * bleed
            page_height += 2 * bleed
        
        # Get margins from interior settings
        if self.interior:
            margin_top = self.interior.layout_settings.get("margin_top", 0.5)
            margin_bottom = self.interior.layout_settings.get("margin_bottom", 0.5)
            margin_left = self.interior.layout_settings.get("margin_left", 0.5)
            margin_right = self.interior.layout_settings.get("margin_right", 0.5)
            units = self.interior.layout_settings.get("units", "in")
            
            if units == "in":
                margin_top *= inch
                margin_bottom *= inch
                margin_left *= inch
                margin_right *= inch
            elif units == "mm":
                margin_top *= mm
                margin_bottom *= mm
                margin_left *= mm
                margin_right *= mm
            else:
                # Default margins
                margin_top = 0.5 * inch
                margin_bottom = 0.5 * inch
                margin_left = 0.5 * inch
                margin_right = 0.5 * inch
        else:
            # Default margins
            margin_top = 0.5 * inch
            margin_bottom = 0.5 * inch
            margin_left = 0.5 * inch
            margin_right = 0.5 * inch
        
        # Create document
        doc = BaseDocTemplate(
            buffer,
            pagesize=(page_width, page_height),
            title=self.book.name,
            author=self.book.user_id,  # Should be username but we don't have access here
            leftMargin=margin_left,
            rightMargin=margin_right,
            topMargin=margin_top,
            bottomMargin=margin_bottom,
        )
        
        return doc

    def _create_page_templates(self, doc: BaseDocTemplate) -> List[PageTemplate]:
        """Create page templates for the document.
        
        Args:
            doc: The document template
            
        Returns:
            A list of page templates
        """
        page_templates = []
        
        # Get header and footer settings
        header_enabled = False
        header_text = ""
        footer_enabled = False
        footer_text = "{page_number}"
        
        if self.interior:
            header_settings = self.interior.layout_settings.get("header", {})
            header_enabled = header_settings.get("enabled", False)
            header_text = header_settings.get("text", "")
            
            footer_settings = self.interior.layout_settings.get("footer", {})
            footer_enabled = footer_settings.get("enabled", False)
            footer_text = footer_settings.get("text", "{page_number}")
        
        # Create frame for content
        content_frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id="content",
        )
        
        # Create page template with header and footer
        def header_footer(canvas, doc):
            canvas.saveState()
            
            # Draw header if enabled
            if header_enabled:
                header = header_text.replace("{page_number}", str(doc.page))
                canvas.setFont("Helvetica", 10)
                canvas.drawString(
                    doc.leftMargin,
                    doc.height + doc.topMargin - 12,
                    header
                )
            
            # Draw footer if enabled
            if footer_enabled:
                footer = footer_text.replace("{page_number}", str(doc.page))
                canvas.setFont("Helvetica", 10)
                canvas.drawString(
                    doc.leftMargin,
                    doc.bottomMargin - 12,
                    footer
                )
            
            canvas.restoreState()
        
        page_templates.append(
            PageTemplate(
                id="normal",
                frames=[content_frame],
                onPage=header_footer,
            )
        )
        
        return page_templates

    def _render_cover(self) -> List:
        """Render the book cover.
        
        Returns:
            A list of flowable elements for the cover
        """
        elements = []
        
        if not self.cover:
            return elements
        
        # Front cover
        front_design = self.cover.front_design
        
        # Title
        if "title" in front_design:
            title_style = ParagraphStyle(
                name="CoverTitle",
                parent=self.styles["BookTitle"],
                fontSize=front_design["title"].get("font_size", 36),
                textColor=front_design["title"].get("font_color", "#000000"),
                alignment=1,  # Center
            )
            elements.append(
                Paragraph(
                    f"<b>{front_design['title'].get('text', self.book.name)}</b>",
                    title_style
                )
            )
        
        # Author
        if "author" in front_design:
            author_style = ParagraphStyle(
                name="CoverAuthor",
                parent=self.styles["BookAuthor"],
                fontSize=front_design["author"].get("font_size", 24),
                textColor=front_design["author"].get("font_color", "#000000"),
                alignment=1,  # Center
            )
            elements.append(
                Paragraph(
                    front_design["author"].get("text", "Author Name"),
                    author_style
                )
            )
        
        # Add page break after cover
        elements.append(PageBreak())
        
        return elements

    def _render_lined_page(self, canvas_obj, page_content, page_width, page_height):
        """Render a lined page on the canvas.
        
        Args:
            canvas_obj: The canvas to draw on
            page_content: The page content
            page_width: The page width
            page_height: The page height
        """
        # Get line settings
        line_spacing = page_content.get("line_spacing", 1.5) * 12  # Convert to points
        line_color = page_content.get("line_color", "#CCCCCC")
        
        # Convert color from hex to RGB
        r, g, b = colors.HexColor(line_color).rgb()
        
        # Set line color
        canvas_obj.setStrokeColorRGB(r, g, b)
        canvas_obj.setLineWidth(0.5)
        
        # Calculate number of lines based on page height and spacing
        margin_top = self.interior.layout_settings.get("margin_top", 0.5) * inch
        margin_bottom = self.interior.layout_settings.get("margin_bottom", 0.5) * inch
        margin_left = self.interior.layout_settings.get("margin_left", 0.5) * inch
        margin_right = self.interior.layout_settings.get("margin_right", 0.5) * inch
        
        content_height = page_height - margin_top - margin_bottom
        num_lines = int(content_height / line_spacing)
        
        # Draw lines
        for i in range(num_lines):
            y = page_height - margin_top - (i * line_spacing)
            canvas_obj.line(margin_left, y, page_width - margin_right, y)

    def _render_grid_page(self, canvas_obj, page_content, page_width, page_height):
        """Render a grid page on the canvas.
        
        Args:
            canvas_obj: The canvas to draw on
            page_content: The page content
            page_width: The page width
            page_height: The page height
        """
        # Get grid settings
        grid_size = page_content.get("grid_size", 0.25) * inch  # Convert to points
        grid_color = page_content.get("grid_color", "#CCCCCC")
        
        # Convert color from hex to RGB
        r, g, b = colors.HexColor(grid_color).rgb()
        
        # Set line color
        canvas_obj.setStrokeColorRGB(r, g, b)
        canvas_obj.setLineWidth(0.5)
        
        # Calculate margins
        margin_top = self.interior.layout_settings.get("margin_top", 0.5) * inch
        margin_bottom = self.interior.layout_settings.get("margin_bottom", 0.5) * inch
        margin_left = self.interior.layout_settings.get("margin_left", 0.5) * inch
        margin_right = self.interior.layout_settings.get("margin_right", 0.5) * inch
        
        # Calculate grid dimensions
        content_width = page_width - margin_left - margin_right
        content_height = page_height - margin_top - margin_bottom
        
        # Draw vertical lines
        for x in range(int(margin_left), int(page_width - margin_right) + 1, int(grid_size)):
            canvas_obj.line(x, margin_bottom, x, page_height - margin_top)
        
        # Draw horizontal lines
        for y in range(int(margin_bottom), int(page_height - margin_top) + 1, int(grid_size)):
            canvas_obj.line(margin_left, y, page_width - margin_right, y)

    def _render_dot_grid_page(self, canvas_obj, page_content, page_width, page_height):
        """Render a dot grid page on the canvas.
        
        Args:
            canvas_obj: The canvas to draw on
            page_content: The page content
            page_width: The page width
            page_height: The page height
        """
        # Get dot grid settings
        dot_spacing = page_content.get("dot_spacing", 0.25) * inch  # Convert to points
        dot_size = page_content.get("dot_size", 0.5)  # Size in points
        dot_color = page_content.get("dot_color", "#CCCCCC")
        
        # Convert color from hex to RGB
        r, g, b = colors.HexColor(dot_color).rgb()
        
        # Set fill color
        canvas_obj.setFillColorRGB(r, g, b)
        
        # Calculate margins
        margin_top = self.interior.layout_settings.get("margin_top", 0.5) * inch
        margin_bottom = self.interior.layout_settings.get("margin_bottom", 0.5) * inch
        margin_left = self.interior.layout_settings.get("margin_left", 0.5) * inch
        margin_right = self.interior.layout_settings.get("margin_right", 0.5) * inch
        
        # Calculate grid dimensions
        content_width = page_width - margin_left - margin_right
        content_height = page_height - margin_top - margin_bottom
        
        # Draw dots
        for x in range(int(margin_left), int(page_width - margin_right) + 1, int(dot_spacing)):
            for y in range(int(margin_bottom), int(page_height - margin_top) + 1, int(dot_spacing)):
                canvas_obj.circle(x, y, dot_size, fill=1)

    def _render_planner_page(self, canvas_obj, page_content, page_width, page_height):
        """Render a planner page on the canvas.
        
        Args:
            canvas_obj: The canvas to draw on
            page_content: The page content
            page_width: The page width
            page_height: The page height
        """
        # Get planner settings
        planner_type = page_content.get("layout", "daily")
        
        # Calculate margins
        margin_top = self.interior.layout_settings.get("margin_top", 0.5) * inch
        margin_bottom = self.interior.layout_settings.get("margin_bottom", 0.5) * inch
        margin_left = self.interior.layout_settings.get("margin_left", 0.5) * inch
        margin_right = self.interior.layout_settings.get("margin_right", 0.5) * inch
        
        # Calculate content dimensions
        content_width = page_width - margin_left - margin_right
        content_height = page_height - margin_top - margin_bottom
        
        # Set line color
        canvas_obj.setStrokeColorRGB(0, 0, 0)
        canvas_obj.setLineWidth(0.5)
        
        if planner_type == "daily":
            # Draw title
            canvas_obj.setFont("Helvetica-Bold", 14)
            canvas_obj.drawString(margin_left, page_height - margin_top - 20, "Daily Planner")
            
            # Draw date field
            canvas_obj.setFont("Helvetica", 12)
            canvas_obj.drawString(margin_left, page_height - margin_top - 40, "Date: _________________")
            
            # Draw goals section
            canvas_obj.setFont("Helvetica-Bold", 12)
            canvas_obj.drawString(margin_left, page_height - margin_top - 70, "Today's Goals")
            
            # Draw goals box
            goals_top = page_height - margin_top - 75
            goals_height = 100
            canvas_obj.rect(margin_left, goals_top - goals_height, content_width, goals_height)
            
            # Draw schedule section
            canvas_obj.setFont("Helvetica-Bold", 12)
            canvas_obj.drawString(margin_left, goals_top - goals_height - 25, "Schedule")
            
            # Draw hourly schedule
            schedule_top = goals_top - goals_height - 30
            schedule_height = 300
            hour_height = schedule_height / 16  # 16 hours (6am-10pm)
            
            for i in range(17):  # 17 lines for 16 hour slots
                y = schedule_top - (i * hour_height)
                canvas_obj.line(margin_left, y, page_width - margin_right, y)
                
                if i < 16:
                    hour = i + 6  # Start at 6am
                    am_pm = "AM" if hour < 12 else "PM"
                    hour_12 = hour if hour <= 12 else hour - 12
                    canvas_obj.setFont("Helvetica", 10)
                    canvas_obj.drawString(margin_left + 5, y - hour_height + 5, f"{hour_12} {am_pm}")
            
            # Draw vertical line to separate time from content
            canvas_obj.line(margin_left + 50, schedule_top, margin_left + 50, schedule_top - schedule_height)
            
            # Draw notes section
            notes_top = schedule_top - schedule_height - 25
            canvas_obj.setFont("Helvetica-Bold", 12)
            canvas_obj.drawString(margin_left, notes_top, "Notes")
            
            # Draw notes box
            notes_height = 150
            canvas_obj.rect(margin_left, notes_top - notes_height, content_width, notes_height)
            
        elif planner_type == "weekly":
            # Draw title
            canvas_obj.setFont("Helvetica-Bold", 14)
            canvas_obj.drawString(margin_left, page_height - margin_top - 20, "Weekly Planner")
            
            # Draw week field
            canvas_obj.setFont("Helvetica", 12)
            canvas_obj.drawString(margin_left, page_height - margin_top - 40, "Week of: _________________")
            
            # Draw days of the week
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_width = content_width / len(days)
            day_height = content_height - 60  # Leave space for title and week field
            
            # Draw day boxes
            for i, day in enumerate(days):
                x = margin_left + (i * day_width)
                y = page_height - margin_top - 60
                
                # Draw day box
                canvas_obj.rect(x, y - day_height, day_width, day_height)
                
                # Draw day name
                canvas_obj.setFont("Helvetica-Bold", 10)
                canvas_obj.drawString(x + 5, y - 15, day)

    def _render_tracker_page(self, canvas_obj, page_content, page_width, page_height):
        """Render a habit tracker page on the canvas.
        
        Args:
            canvas_obj: The canvas to draw on
            page_content: The page content
            page_width: The page width
            page_height: The page height
        """
        # Get tracker settings
        rows = page_content.get("rows", 10)
        columns = page_content.get("columns", 31)
        
        # Calculate margins
        margin_top = self.interior.layout_settings.get("margin_top", 0.5) * inch
        margin_bottom = self.interior.layout_settings.get("margin_bottom", 0.5) * inch
        margin_left = self.interior.layout_settings.get("margin_left", 0.5) * inch
        margin_right = self.interior.layout_settings.get("margin_right", 0.5) * inch
        
        # Calculate content dimensions
        content_width = page_width - margin_left - margin_right
        content_height = page_height - margin_top - margin_bottom
        
        # Set line color
        canvas_obj.setStrokeColorRGB(0, 0, 0)
        canvas_obj.setLineWidth(0.5)
        
        # Draw title
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.drawString(margin_left, page_height - margin_top - 20, "Habit Tracker")
        
        # Draw month field
        canvas_obj.setFont("Helvetica", 12)
        canvas_obj.drawString(margin_left, page_height - margin_top - 40, "Month: _________________")
        
        # Calculate grid dimensions
        grid_top = page_height - margin_top - 60
        grid_height = content_height - 60
        row_height = grid_height / (rows + 1)  # +1 for header row
        column_width = content_width / (columns + 1)  # +1 for habit name column
        
        # Draw grid
        for i in range(rows + 2):  # +2 for header and bottom line
            y = grid_top - (i * row_height)
            canvas_obj.line(margin_left, y, page_width - margin_right, y)
        
        for i in range(columns + 2):  # +2 for left and right line
            x = margin_left + (i * column_width)
            canvas_obj.line(x, grid_top, x, grid_top - grid_height)
        
        # Draw day numbers in header row
        canvas_obj.setFont("Helvetica-Bold", 8)
        for i in range(columns):
            x = margin_left + column_width + (i * column_width) + (column_width / 2)
            y = grid_top - (row_height / 2)
            canvas_obj.drawCentredString(x, y, str(i + 1))
        
        # Draw "Habit" in first column header
        canvas_obj.setFont("Helvetica-Bold", 8)
        canvas_obj.drawCentredString(margin_left + (column_width / 2), grid_top - (row_height / 2), "Habit")

    def _render_page(self, page: BookPage) -> List:
        """Render a book page.
        
        Args:
            page: The page to render
            
        Returns:
            A list of flowable elements for the page
        """
        elements = []
        
        # Get page content
        page_content = page.content
        page_type = page_content.get("type", "blank")
        
        # Create a custom drawing function for this page
        def draw_page(canvas_obj, doc):
            canvas_obj.saveState()
            
            # Get page dimensions
            page_width, page_height = doc.pagesize
            
            # Draw page content based on type
            if page_type == "lined":
                self._render_lined_page(canvas_obj, page_content, page_width, page_height)
            elif page_type == "grid":
                self._render_grid_page(canvas_obj, page_content, page_width, page_height)
            elif page_type == "dot":
                self._render_dot_grid_page(canvas_obj, page_content, page_width, page_height)
            elif page_type == "planner":
                self._render_planner_page(canvas_obj, page_content, page_width, page_height)
            elif page_type == "tracker":
                self._render_tracker_page(canvas_obj, page_content, page_width, page_height)
            # Add more page types as needed
            
            canvas_obj.restoreState()
        
        # Add a spacer to trigger the page drawing
        elements.append(Spacer(1, 1))
        
        # Add a callback to draw the page
        elements.append(PageBreak())
        
        return elements, draw_page

    def generate_pdf(self, include_bleed: bool = False, quality: int = 300) -> io.BytesIO:
        """Generate a PDF for the book.
        
        Args:
            include_bleed: Whether to include bleed area
            quality: The quality of the PDF in DPI
            
        Returns:
            A BytesIO object containing the PDF
        """
        buffer = io.BytesIO()
        
        # Create document
        doc = self._create_document(buffer, include_bleed)
        
        # Create page templates
        page_templates = self._create_page_templates(doc)
        
        # Add page templates to document
        for template in page_templates:
            doc.addPageTemplates(template)
        
        # Create content
        elements = []
        page_callbacks = []
        
        # Add cover if available
        if self.cover:
            elements.extend(self._render_cover())
        
        # Add pages
        for page in sorted(self.pages, key=lambda p: p.page_number):
            page_elements, page_callback = self._render_page(page)
            elements.extend(page_elements)
            page_callbacks.append((page.page_number, page_callback))
        
        # Build the PDF
        doc.build(elements, canvasmaker=NumberedCanvas)
        
        # Reset buffer position
        buffer.seek(0)
        
        return buffer


class NumberedCanvas(canvas.Canvas):
    """A canvas that adds page numbers."""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """Draw the page number on the canvas."""
        # Page numbers are drawn by the header/footer function in the page template
        pass
