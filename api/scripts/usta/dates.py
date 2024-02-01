from playwright.async_api import async_playwright
from lib import urls, months, Errors, openBrowser
import json


 
async def get_dates(cookies: list[dict]) -> Errors:

    async with async_playwright() as pw:
        page, err = openBrowser(pw, cookies, urls.MYSAINT.url)
        if err != Errors.NONE:
            return err

        table = page.locator(".col-sm-12").nth(1)
        tables = await table.locator(".table").all()

        data_dict = {"weeks":[]}

        for tab in tables:
            rows = await tab.get_by_role("row").all()

            for i, row in enumerate(rows):
                if i > 1:
                    data_txt = await row.locator("td").nth(1).inner_text()
                    data_txt = data_txt.replace("Monday ", "")
                    data_arr = data_txt.split(" ")
#
                    if len(data_arr) > 3:
                        data_arr.pop(0)

                    if len(data_arr[0]) < 2:
                        data_arr[0] = "0" + data_arr[0]
                    elif len(data_arr) > 2:
                        data_arr[0] = data_arr[0][len(data_arr[0])-2:]
                    
                    data_arr[1] = months[data_arr[1].upper()].value

                    data_dict["weeks"].append(data_arr)

    data_json = json.dumps(data_dict, indent=4)

    with open("./dates.json", "w") as file:
            file.write(data_json)
