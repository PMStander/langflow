"""Book templates for the Book Creator module."""

from uuid import uuid4

from langflow.services.database.models.book import BookTemplate


def get_system_book_templates():
    """Get system book templates."""
    templates = []

    # Lined Journal Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Lined Journal",
            description="A simple lined journal template",
            category="interior",
            template_type="lined",
            is_system=True,
            content={
                "line_spacing": 1.5,
                "line_color": "#CCCCCC",
                "margin_top": 1,
                "margin_bottom": 1,
                "margin_left": 1,
                "margin_right": 1,
                "units": "in",
                "header": {"enabled": False, "text": ""},
                "footer": {"enabled": True, "text": "{page_number}"},
            },
        )
    )

    # Grid Journal Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Grid Journal",
            description="A grid journal template",
            category="interior",
            template_type="grid",
            is_system=True,
            content={
                "grid_size": 0.25,
                "grid_color": "#CCCCCC",
                "margin_top": 0.5,
                "margin_bottom": 0.5,
                "margin_left": 0.5,
                "margin_right": 0.5,
                "units": "in",
                "header": {"enabled": False, "text": ""},
                "footer": {"enabled": True, "text": "{page_number}"},
            },
        )
    )

    # Dot Grid Journal Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Dot Grid Journal",
            description="A dot grid journal template",
            category="interior",
            template_type="dot",
            is_system=True,
            content={
                "dot_spacing": 0.25,
                "dot_size": 0.5,
                "dot_color": "#CCCCCC",
                "margin_top": 0.5,
                "margin_bottom": 0.5,
                "margin_left": 0.5,
                "margin_right": 0.5,
                "units": "in",
                "header": {"enabled": False, "text": ""},
                "footer": {"enabled": True, "text": "{page_number}"},
            },
        )
    )

    # Blank Journal Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Blank Journal",
            description="A blank journal template",
            category="interior",
            template_type="blank",
            is_system=True,
            content={
                "margin_top": 0.5,
                "margin_bottom": 0.5,
                "margin_left": 0.5,
                "margin_right": 0.5,
                "units": "in",
                "header": {"enabled": False, "text": ""},
                "footer": {"enabled": True, "text": "{page_number}"},
            },
        )
    )

    # Simple Book Cover Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Simple Book Cover",
            description="A simple book cover template",
            category="cover",
            template_type="simple",
            is_system=True,
            content={
                "background_color": "#FFFFFF",
                "title": {
                    "text": "Book Title",
                    "font": "Arial",
                    "font_size": 36,
                    "font_color": "#000000",
                    "position": {"x": "center", "y": "center"},
                },
                "author": {
                    "text": "Author Name",
                    "font": "Arial",
                    "font_size": 24,
                    "font_color": "#000000",
                    "position": {"x": "center", "y": "bottom"},
                },
                "spine": {
                    "text": "Book Title",
                    "font": "Arial",
                    "font_size": 18,
                    "font_color": "#000000",
                    "direction": "vertical",
                },
                "back": {
                    "text": "Book Description",
                    "font": "Arial",
                    "font_size": 14,
                    "font_color": "#000000",
                    "position": {"x": "center", "y": "center"},
                },
            },
        )
    )

    # Gradient Book Cover Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Gradient Book Cover",
            description="A gradient book cover template",
            category="cover",
            template_type="gradient",
            is_system=True,
            content={
                "gradient": {
                    "type": "linear",
                    "start_color": "#3498db",
                    "end_color": "#2c3e50",
                    "direction": "top-to-bottom",
                },
                "title": {
                    "text": "Book Title",
                    "font": "Arial",
                    "font_size": 36,
                    "font_color": "#FFFFFF",
                    "position": {"x": "center", "y": "center"},
                },
                "author": {
                    "text": "Author Name",
                    "font": "Arial",
                    "font_size": 24,
                    "font_color": "#FFFFFF",
                    "position": {"x": "center", "y": "bottom"},
                },
                "spine": {
                    "text": "Book Title",
                    "font": "Arial",
                    "font_size": 18,
                    "font_color": "#FFFFFF",
                    "direction": "vertical",
                },
                "back": {
                    "text": "Book Description",
                    "font": "Arial",
                    "font_size": 14,
                    "font_color": "#FFFFFF",
                    "position": {"x": "center", "y": "center"},
                },
            },
        )
    )

    return templates
