from playwright.async_api import async_playwright, expect, Locator, Page
from dataclasses import dataclass, field
from pathlib import Path
from lib import Errors, openBrowser, urls

@dataclass
class file_folder:
    name_folder: str = field(default_factory=str)
    file_names: list = field(default_factory=list)
    folder_names: list = field(default_factory=list)

@dataclass
class module_structure:
    folders: dict = field(default_factory=dict)
    current_folder: str = field(default_factory=str)


#recursively gets the path of a file
def get_parents(module: module_structure, current_folder: str, path: str) -> str:
    for folder in module.folders.keys():
        for i in module.folders[folder].folder_names:
            if current_folder == i:
                path = get_parents(module, folder, path) + folder
                return path
    
    return ""

#gets the right folder when the script attempts to navigate backwards
async def get_correct_folder(page: Page) -> str:
    heading = page.get_by_role("heading")
    heading_arr = await heading.inner_text()
    head = heading_arr.split("/")
    return head[len(head)-1] + "/"



async def get_files(session_year: str, module: str, cookies: list[dict]) -> Errors:

    async with async_playwright() as pw:
        page, err = openBrowser(pw, cookies, f"{urls.STUDRES.url}{session_year}/{module}/")
        if err != Errors.NONE:
            return err
        

        mod_sys = module_structure()
        mod_sys.current_folder = module+"/" #sets current folder to module name
        year_num = module.replace("CS", "") #gets yearX for file system

        await get_files(page, mod_sys, year_num[0], session_year)
    
    return Errors.NONE



async def get_files(page: Page, mod_sys: module_structure, year_num: str, session_year: str) -> None:
    table_rows: Locator = page.locator('tr')
    row_count: int = await table_rows.count()
    
    folder = file_folder()
    folder.name_folder = mod_sys.current_folder


    #loop through each relevant row
    for i in range(3, row_count-1):
        row: Locator = table_rows.nth(i)
        row_text: str = await row.inner_text()

        if row_text != '':
            row_text: str = row_text.split("\t")[1] #name of file/folder
            row_element: Locator = page.get_by_text(f"{row_text}", exact=True)
            
            #if the element is a folder
            if row_text[len(row_text)-1] == "/":
                
                folder.folder_names.append(row_text)
                mod_sys.current_folder = row_text #updates current folder

                #to get accurate path tracing when downloading (for get_parents)
                mod_sys.folders[folder.name_folder] = folder

                await row_element.click()
                await get_files(page, mod_sys, year_num, session_year)

            #if the element is a file
            else:

                #attempts to download the file
                try:
                    async with page.expect_download(timeout=30000) as download_info:
                        await page.get_by_text(f"{row_text}").click(modifiers=["Alt", ])
                        pathy = get_parents(mod_sys, mod_sys.current_folder, '') + mod_sys.current_folder

                    download = await download_info.value
                    await download.save_as(Path.home().joinpath(f"Documents\Programming\{session_year}\Year{year_num}\{pathy}", download.suggested_filename))
                
                #if download fails
                except:
                    if pathy is None:
                        pathy = "path_not_discovered"

                    Errors.DOWNLOAD.throw((pathy, row_text))


                folder.file_names.append(row_text) #add file to folder's file array

    mod_sys.folders[folder.name_folder] = folder #after folder is scraped, add the dataclass containing it's data to mod_sys
    
    #attempts to navigate back after all relevant rows are completed
    try:
        await expect(page.get_by_text("Parent Directory")).to_be_visible(timeout=5000)
        await page.get_by_text("Parent Directory").click()

        mod_sys.current_folder = await get_correct_folder(page)

    #if item is actually a html page (probably not needed)
    except:
        await page.go_back()
        mod_sys.current_folder = await get_correct_folder(page)