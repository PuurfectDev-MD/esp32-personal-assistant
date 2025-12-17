import ui_state
import ui_module
import assistant_module
import focus


from ui_pages.foucs_pg import FocusPage
from ui_pages.calendar_pg import CalendarPage
class HomePage:

    def __init__(self, engine=None):
        self.engine = engine
        ui_module.home()        # draw the home UI

    def handle_touch(self, x, y):
        """Handle all touch actions for the home screen."""
        
        print(f"x :{x} , y :{y}")

        # 1. Side panel toggle
        if ui_module.detect_circle_button_touch(25, 220, 20, x, y):
            if not ui_module.side_panel_open:
                ui_module.side_panel()
                ui_module.side_panel_open = True
            else:
                ui_module.home()
                ui_module.side_panel_button()
                ui_module.side_panel_open = False
            return

        # 2. If side panel is open → detect panel elements
        if ui_module.side_panel_open:
            menu = ui_module.panel_element_select(x, y)
            if menu == 1:
                ui_module.today_schedule()
            elif menu == 2:
                assistant_module.assistant_begin(self.engine)
            return

        # 3. Normal home page options
        option = ui_module.home_option_select(x, y)
        
        if option == 1:
            page = CalendarPage()
            ui_state.set_page("calendar", page)
        if option == 5:
            focus = FocusPage()
            ui_state.set_page("focus", focus)
            return
      
            

