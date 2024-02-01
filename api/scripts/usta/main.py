from work import get_dates
import asyncio
from lib import get_cookies, scripts, session_details, urls, Errors
import sys


async def handler(cookies: list[dict], cmd: str) -> None:

    try:
        func = scripts[cmd].func
    except:
        Errors.INVALID_CMD.throw()
    # try:

    # session.mms_cookies = await get_cookies(urls.MMS)
    # session.set_save()

    await func(cookies)
    # except:
    #     Errors.TIMETABLE.throw()
    #     session.mms_cookies = await get_cookies(urls.MMS)
    #     session.set_save()
        

if __name__ == "__main__":
    session = session_details

    if not session.get_save():
        Errors.SESSION_JSON.throw()

    asyncio.run(handler(session.mms_cookies, sys.argv[1]))