from enum import Enum, auto, unique
from playwright.async_api import async_playwright, Playwright, Page
from dataclasses import dataclass, field, fields
import json
from pathlib import Path
from collections.abc import Callable
import sys

#scripts
from dates import get_dates
from timetable import get_timetable
from work import get_work

class Level_Functions(Enum):
    """*args used to ignore excess arguements passed in"""

    def null() -> None:
        pass

    def log(cls, data: tuple = ()) -> None:
        """appends error message to log file"""

        Path("logs/").mkdir(parents=True, exist_ok=True)
        with open("logs/log_error.txt", "a") as f:
            f.write(f'{cls.err_msg}\n' % data)

    def warn(cls, data: tuple = ()) -> None:
        """prints error message to cli"""

        print(cls.err_msg % data)

    def exit(*args) -> None:
        """exits the program"""
        
        sys.exit(0)    

@dataclass
class Error_Level_Mixin:
    id: int
    order: int
    func: Callable

@unique
class Error_Level(Error_Level_Mixin, Level_Functions):
    NIL = auto(), 0, Level_Functions.null
    LOG = auto(), 1, Level_Functions.log
    WARN = auto(), 2, Level_Functions.warn
    EXIT = auto(), 3, Level_Functions.exit

    # to get Error_Level by order
    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.order == value:
                return member

        return None

@dataclass
class Errors_Mixin:
    id: int
    lvl: Error_Level
    err_msg: str

@unique
class Errors(Errors_Mixin, Enum):
    NONE = auto(), Error_Level.NIL, ""
    COMMAND = auto(), Error_Level.WARN, "Invalid command, type 'list_cmd' to see list of valid commands."
    NAVIGATION = auto(), Error_Level.WARN, "Navigation to url failed"
    DOWNLOAD = auto(), Error_Level.LOG, "File download unsuccessful. | Path: %s | File: %s"
    MODULE_NAV = auto(), Error_Level.WARN, "Couldn't find module/cookies failed. Please re-type module code."
    SESSION_JSON = auto(), Error_Level.WARN, "session.json file not in correct format"
    TIMETABLE = auto(), Error_Level.WARN, "Error in tableScraper.py"
    INVALID_CMD = auto(), Error_Level.EXIT, "Doesn't exist"

    def throw(cls, data: tuple = ()) -> None:
        """throws each error of a lower order until lvl.order is met"""
        
        for i in range(1, cls.lvl.order+1):
            Error_Level(i).func(cls, data)


@dataclass
class coursework_data:
    Assignment: str
    Due_Date: str
    Feedback_Date: str
    Date_Submitted: str
    Feedback_Path: str
    Grade: float
    Weight: int
    Chart_Path: str

@dataclass
class exercise_data:
    Assignment: str
    Due_Date: str
    Feedback_Date: str
    Date_Submitted: str

class months(Enum):
    JANUARY = "01"
    FEBRUARY = "02"
    MARCH = "03"
    APRIL = "04"
    MAY = "05"
    JUNE = "06"
    JULY = "07"
    AUGUST = "08"
    SEPTEMBER = "09"
    OCTOBER = "10"
    NOVEMBER = "11"
    DECEMBER = "12"

@dataclass
class module_instance:
    event_day: str
    event_info: str
    event_title: str
    event_time: str
    event_extra: str


@dataclass
class urls_mixin:
    id: int
    url: str

@unique
class urls(urls_mixin, Enum):
    STUDRES = auto(), "https://studres.cs.st-andrews.ac.uk/"
    MYSAINT = auto(), "https://mysaint.st-andrews.ac.uk/uPortal/f/events/normal/render.uP"
    MMS = auto(), "https://mms.st-andrews.ac.uk/mms/user/me/Modules"


@dataclass
class session_details:
    studres_cookies: list[dict()] = field(default_factory=list[dict()])
    mysaint_cookies: list[dict()] = field(default_factory=list[dict()])
    mms_cookies: list[dict()] = field(default_factory=list[dict()])

    @classmethod
    def set_save(cls) -> None:
        sesh = {val.name:getattr(cls, val.name) for val in fields(cls) if hasattr(cls, val.name)}

        print(sesh)
        session_json = json.dumps(sesh, indent=4)
        print(session_json)

        with open("./session_data.json", "w") as file:
            file.write(session_json)

    @classmethod
    def get_save(cls) -> bool:
        with open("session_data.json", "r") as file:
            try:
                session_json = json.load(file)
            except:
                return False

        for cookie_name in session_json:
            setattr(cls, cookie_name, session_json[cookie_name])

        return True


@dataclass
class scripts_mixin:
    id: int
    func: Callable

class scripts(Enum):
    DATES = auto(), get_dates
    TIMETABLE = auto(), get_timetable
    WORK = auto(), get_work
    FILES = auto(), get_files

async def openBrowser(pw: Playwright, cookies: list[dict], nav_url: str) -> tuple(Page, Errors):
    browser = await pw.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()
    await context.add_cookies(cookies)
    
    try:
        await page.goto(f"{nav_url}")
        await page.wait_for_url(f"{nav_url}", timeout=5000)
    except:
        return (None, Errors.NAVIGATION)
    
    return (Page, Errors.NONE)


async def get_cookies(page_url: urls) -> list[dict]:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False
        )

        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(page_url.url)
        
        # Interact with login form
        await page.get_by_placeholder("Email address, phone number or Skype").fill("hb233@st-andrews.ac.uk")
        await page.locator("#idSIButton9").click()
        await page.get_by_placeholder("Password").fill("#Harris20052007")
        await page.locator("#idSIButton9").click()
        
        #wait for user to authenticate
        await page.wait_for_url(page_url.url, timeout=300000)
        cookies = await context.cookies()
        return cookies