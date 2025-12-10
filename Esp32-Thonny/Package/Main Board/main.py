import uasyncio as asyncio
import time
from machine import Pin
from setup import display, rtc, font, font2, rtc_power, spi, touch
import ui_module
import calendar_module as cal
import assistant_module
import comm_config
import schedule_track_sys
import focus

from ui_pages.home import HomePage
# from ui_pages.todo import TodoPage
from ui_pages.focus import FocusPage
# etc.

WHITE = 0xFFFF
BLACK = 0x0000

working = False
main_button = Pin(13, Pin.IN, Pin.PULL_UP)  # active LOW
current_page = None  # Holds the active page instance


# -----------------------------------------------------------
#  BOOT + INIT SECTION
# -----------------------------------------------------------

async def wait_for_power_button():
    """Wait for user to press the main button to activate device."""
    global working
    while not working:
        if main_button.value() == 0:
            working = True
            print("Device activated")
            await asyncio.sleep_ms(300)  # debounce
            break
        await asyncio.sleep_ms(50)


async def async_init():
    """Connect WiFi, draw home UI, init engine, get calendar."""
    schedule_track_sys.reset_tasks_file()
    rtc_power.value(1)

    cal.connect_wifi()
    cal.get_calendar_events_today()

    # init engine (MQTT or similar)
    engine = comm_config.init_mqtt()  

    # Create page instances
    global current_page
    current_page = HomePage(engine)  # active page at boot

    return engine


# -----------------------------------------------------------
#  ASYNC TASKS
# -----------------------------------------------------------

async def power_monitor():
    """Monitor power button to shut down device."""
    global working
    while True:
        if main_button.value() == 0:
            print("Power OFF triggered.")
            working = False
            display.fill_hrect(0, 0, 320, 240, BLACK)
            await asyncio.sleep_ms(300)
            break
        await asyncio.sleep_ms(200)


async def touch_loop():
    """Send touch events to the current page."""
    while True:
        coords = touch.get_touch()
        if coords and current_page:
            x, y = coords
            current_page.handle_touch(x, y)
        await asyncio.sleep_ms(30)


async def rtc_update_loop():
    """Update RTC time on display every 30s."""
    while True:
        ui_module.update_time()
        await asyncio.sleep(30)


async def task_checker_loop():
    """Check scheduled tasks in background."""
    while True:
        schedule_track_sys.check_for_tasks()
        schedule_track_sys.notification_cooldown()
        await asyncio.sleep(2)


# -----------------------------------------------------------
#  MAIN EXECUTION LOOP
# -----------------------------------------------------------

async def main():
    await wait_for_power_button()
    engine = await async_init()

    # Start background tasks
    asyncio.create_task(touch_loop())
    asyncio.create_task(rtc_update_loop())
    asyncio.create_task(task_checker_loop())
    asyncio.create_task(power_monitor())

    # Main loop — idle, everything handled by tasks
    while working:
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
