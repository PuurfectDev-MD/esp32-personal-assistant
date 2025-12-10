import ui_state
import ui_module
import focus

class FocusPage:
    """UI for Focus mode, including subject selection and circle timer."""

    def __init__(self):
        # Draw the Focus UI when page is created
        self.draw_ui()

    def draw_ui(self):
        """Draw the focus selection UI on screen."""
        ui_module.display.fill_hrect(0, 0, 320, 240, ui_module.BLACK)

        # Draw focus subjects
        for i, item in enumerate(ui_module.focus_tags):
            ui_module.display.draw_text(10, 20 + (i * 60), item, ui_module.font, ui_module.WHITE)

        # Draw large circle timer
        ui_module.display.fill_circle(230, 120, 80, ui_module.WHITE)
        ui_module.display.draw_text(190, 105, "0 : 00", ui_module.font, ui_module.BLACK, ui_module.WHITE)

    def handle_touch(self, x, y):
        """Handle touch events for Focus page."""
        # Check if any of the focus tags are pressed
        for i, item in enumerate(ui_module.focus_tags):
            if ui_module.detect_rect_touch(10, 20 + (i * 60), 200, 40, x, y):
                print(f"Selected focus: {item}")
                focus.focused = True
                focus.begin_focus()
                return

        # Optional: handle circle timer touches if needed
        if ui_module.detect_circle_button_touch(230, 120, 80, x, y):
            print("Circle timer touched")
            # You can add pause/resume logic here
            




