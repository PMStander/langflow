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

    # Daily Planner Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Daily Planner",
            description="A daily planner template with hourly schedule",
            category="interior",
            template_type="planner",
            is_system=True,
            content={
                "margin_top": 0.75,
                "margin_bottom": 0.75,
                "margin_left": 0.75,
                "margin_right": 0.75,
                "units": "in",
                "header": {"enabled": True, "text": "Daily Planner - {date}"},
                "footer": {"enabled": True, "text": "{page_number}"},
                "sections": [
                    {"name": "Today's Goals", "height": 2, "type": "list"},
                    {"name": "Schedule", "height": 8, "type": "hourly", "start_hour": 6, "end_hour": 22},
                    {"name": "Notes", "height": 3, "type": "lined"},
                ],
            },
        )
    )

    # Weekly Planner Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Weekly Planner",
            description="A weekly planner template with daily sections",
            category="interior",
            template_type="planner",
            is_system=True,
            content={
                "margin_top": 0.75,
                "margin_bottom": 0.75,
                "margin_left": 0.75,
                "margin_right": 0.75,
                "units": "in",
                "header": {"enabled": True, "text": "Week of {week_start} - {week_end}"},
                "footer": {"enabled": True, "text": "{page_number}"},
                "layout": "weekly",
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            },
        )
    )

    # Habit Tracker Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Habit Tracker",
            description="A monthly habit tracker template",
            category="interior",
            template_type="tracker",
            is_system=True,
            content={
                "margin_top": 0.75,
                "margin_bottom": 0.75,
                "margin_left": 0.75,
                "margin_right": 0.75,
                "units": "in",
                "header": {"enabled": True, "text": "Habit Tracker - {month} {year}"},
                "footer": {"enabled": True, "text": "{page_number}"},
                "layout": "grid",
                "rows": 10,  # Number of habits
                "columns": 31,  # Days in month
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

    # Minimalist Cover Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Minimalist Cover",
            description="A minimalist book cover template with clean typography",
            category="cover",
            template_type="minimalist",
            is_system=True,
            content={
                "background_color": "#F5F5F5",
                "accent_color": "#FF5252",
                "title": {
                    "text": "Book Title",
                    "font": "Helvetica",
                    "font_size": 42,
                    "font_color": "#333333",
                    "position": {"x": "center", "y": "center"},
                    "uppercase": True,
                },
                "author": {
                    "text": "Author Name",
                    "font": "Helvetica",
                    "font_size": 18,
                    "font_color": "#666666",
                    "position": {"x": "center", "y": "bottom"},
                },
                "spine": {
                    "text": "Book Title",
                    "font": "Helvetica",
                    "font_size": 16,
                    "font_color": "#333333",
                    "direction": "vertical",
                },
                "back": {
                    "text": "Book Description",
                    "font": "Helvetica",
                    "font_size": 14,
                    "font_color": "#666666",
                    "position": {"x": "center", "y": "center"},
                },
                "elements": [
                    {
                        "type": "line",
                        "color": "#FF5252",
                        "width": 2,
                        "position": {"x": "center", "y": "top", "offset": 1},
                        "length": 3,
                    }
                ],
            },
        )
    )

    # Photo Cover Template
    templates.append(
        BookTemplate(
            id=uuid4(),
            name="Photo Cover",
            description="A book cover template with a background image",
            category="cover",
            template_type="photo",
            is_system=True,
            content={
                "background_image": "placeholder.jpg",
                "overlay_color": "rgba(0, 0, 0, 0.5)",
                "title": {
                    "text": "Book Title",
                    "font": "Georgia",
                    "font_size": 48,
                    "font_color": "#FFFFFF",
                    "position": {"x": "center", "y": "center"},
                    "shadow": {"color": "#000000", "blur": 5, "offset": 2},
                },
                "author": {
                    "text": "Author Name",
                    "font": "Georgia",
                    "font_size": 24,
                    "font_color": "#FFFFFF",
                    "position": {"x": "center", "y": "bottom"},
                    "shadow": {"color": "#000000", "blur": 3, "offset": 1},
                },
                "spine": {
                    "text": "Book Title",
                    "font": "Georgia",
                    "font_size": 18,
                    "font_color": "#FFFFFF",
                    "direction": "vertical",
                    "background_color": "#333333",
                },
                "back": {
                    "text": "Book Description",
                    "font": "Georgia",
                    "font_size": 14,
                    "font_color": "#FFFFFF",
                    "position": {"x": "center", "y": "center"},
                    "background_color": "rgba(0, 0, 0, 0.7)",
                    "padding": 20,
                },
            },
        )
    )

    return templates
