from playwright.async_api import async_playwright, expect
from lib import exercise_data, urls, coursework_data, openBrowser, Errors
from dataclasses import fields
import json
import aiofiles as aiof
import os



async def get_work(cookies: list[dict]) -> Errors:

    async with async_playwright() as pw:
        page, err = openBrowser(pw, cookies, urls.MMS.url)
        if err != Errors.NONE:
            return err

        data_dict = {"Coursework":{}, "Exercises":{}}

        modules = await page.locator(".card.card-primary").all()
        for mod in modules:
            course = mod.get_by_text("Coursework")
            exe = mod.get_by_text("Exercises")
            try:
                if await course.inner_text() != "":
                    data_dict = await get_data(course, page, "Coursework", data_dict)
            except:
                pass
            
            try:
                if await exe.inner_text() != "":
                    print("exe")
                    print(await exe.inner_text())
                    data_dict = await get_data(exe, page, "Exercises", data_dict)
            except:
                pass

        
        data_json = json.dumps(data_dict, indent=4)

        with open("exe_course.json", "w") as file:
            file.write(data_json)

    return Errors.NONE


async def get_data(exe_course, page, ctype, data_dict):
    module = await exe_course.inner_text()
    module = module.replace(f"{ctype}", "").strip()
    data_dict[ctype][module] = []

    await exe_course.click()
    await expect(page.get_by_text("Student Assignments")).to_be_visible()
    table = page.locator("#studentAssignmentsTable")
    rows = await table.get_by_role("row").all()

    for i, row in enumerate(rows):
        if i > 0:
            data_arr = await row.locator("td").all()
            
            if ctype == "Coursework":
                data = coursework_data
            else:
                data = exercise_data

            data.Assignment = await data_arr[0].inner_text()
            data.Due_Date = await data_arr[1].inner_text()
            data.Feedback_Date = await data_arr[2].inner_text()
            data.Date_Submitted = await data_arr[4].inner_text()

            if ctype == "Coursework":
                path = "./exe_course_data/"
                data.Feedback_Path = f"{path}feedback_{data.Assignment.replace(' ', '_')+'_'+module}.txt"

                lis = await data_arr[5].get_by_role("listitem").all()
                if len(lis) > 1:
                    try:
                        async with page.expect_download(timeout=3000) as download_info:
                            await lis[len(lis)-2].click(modifiers=["Alt", ])

                        download = await download_info.value
                        filename, file_extension = os.path.splitext(download.suggested_filename)
                        data.Feedback_Path = data.Feedback_Path.replace(".txt", "") + file_extension
                        await download.save_as(f"{data.Feedback_Path}")
                    
                    #feedback given in dialog box
                    except:
                        dialog = await page.locator("#comment_dialog").inner_text()
                        async with aiof.open(f"{data.Feedback_Path}", "w") as out:
                            await out.write(dialog)
                        await page.locator(".btn.btn-secondary").click()
                        
                #feedback not be given yet      
                else:
                    data.Feedback_Path = "None"
                
                
                grade = await data_arr[6].inner_text()
                try: 
                    data.Grade = float(grade)

                #grade may not be awarded yet
                except:
                    data.Grade = 0.0

                weight = await data_arr[7].inner_text()
                data.Weight = int(weight.replace(" %", ""))

                path = "./exe_course_data/"
                data.Chart_Path = f"{path}img_{data.Assignment.replace(' ', '_')+'_'+module}.png"

                #gets image bytes, through request, and writes them to file
                async with page.expect_request("https://mms.st-andrews.ac.uk/mms/module/*") as requ:
                    await data_arr[8].locator("a").click()
                
                requ_value = await requ.value
                resp = await requ_value.response()
                resp_body = await resp.body()
                async with aiof.open(f"{data.Chart_Path}", "wb") as out:
                    await out.write(resp_body)
                
                await page.go_back()


            data_dict[ctype][module].append([getattr(data, val.name) for val in fields(data)])
            
    await page.go_back()
    return data_dict