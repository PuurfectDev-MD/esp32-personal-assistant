import ui_module
import focus

focus_tags = ["Study", "Research", "Brainstorm", "Chill"]

class FocusPage:

    def __init__(self):
        self.draw_ui()

    def draw_ui(self):
        ui_module.display.fill_hrect(0, 0, 320, 240, ui_module.BLACK)

        for i, item in enumerate(focus_tags):
            ui_module.display.draw_text(
                10, 20 + (i * 60),
                item,
                ui_module.font,
                ui_module.WHITE
            )

        ui_module.display.fill_circle(230, 120, 80, ui_module.WHITE)
        ui_module.display.draw_text(
            190, 105,
            "0 : 00",
            ui_module.font,
            ui_module.BLACK,
            ui_module.WHITE
        )

    def handle_touch(self, x, y):
        # subject selection
        for i, item in enumerate(focus_tags):
            if ui_module.detect_rect_touch(10, 20 + (i * 60), 200, 40, x, y):
                print("Selected focus:", item)
                return

        # timer toggle
        if ui_module.detect_circle_button_touch(230, 120, 80, x, y):
            if not focus.focused:
                focus.start_focus()
            else:
                focus.stop_focus()

