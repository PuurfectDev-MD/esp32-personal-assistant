import uasyncio as asyncio
import ui_state
from setup import touch

async def touch_loop():
    """Reads touch and sends events to the current page handler."""
    while True:
        coords = touch.get_touch()

        if coords:
            x, y = coords

            # get current page object
            page = ui_state.current_page_obj

            # call its own handler
            if page and hasattr(page, "handle_touch"):
                page.handle_touch(x, y)

        await asyncio.sleep_ms(20)

