from playwright.async_api import async_playwright
from lib import module_instance, openBrowser, Errors, urls
from dataclasses import fields
import json



async def get_timetable(sem_dates: dict, cookies: list[dict]) -> Errors:

    async with async_playwright() as pw:
        page, err = openBrowser(pw, cookies, urls.MYSAINT.url)
        if err != Errors.NONE:
            return err
        
        data = {}

        for j, i in enumerate(sem_dates):
            data[j] = []
            await page.goto(f"https://mysaint.st-andrews.ac.uk/uPortal/f/events/p/personal-timetable.u22l1n7110/normal/timetableWeek.resource.uP?week={i[2]}-{i[1]}-{i[0]}")
            await page.wait_for_url(f"https://mysaint.st-andrews.ac.uk/uPortal/f/events/p/personal-timetable.u22l1n7110/normal/timetableWeek.resource.uP?week={i[2]}-{i[1]}-{i[0]}", timeout=5000)

            days = await page.locator("div.day").all()

            for day in days:
                divs = await day.locator("div").all()
                event_day = await day.locator("h4.mobile-heading").inner_html()
                
                #only need every fourth div from divs, as the others are child elements
                count = 0
                for div in divs:
                    if count == 0:
                        modu = module_instance
                        modu.event_day = event_day.upper()
                        modu.event_info = await div.locator(".event-info").text_content()
                        modu.event_title = await div.locator(".event-title").text_content()
                        modu.event_time = await div.locator(".event-time").text_content()
                        modu.event_extra = await div.locator(".event-extra").text_content()

                        data[j].append([getattr(modu, val.name) for val in fields(modu)])
                        count = 5
                    count -= 1
        
        data_json = json.dumps(data, indent=4)

        with open("timetable.json", "w") as file:
            file.write(data_json)

    return Errors.NONE
            