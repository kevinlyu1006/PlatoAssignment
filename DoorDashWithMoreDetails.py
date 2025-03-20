"""
This script demonstrates how to use Scrapybara with Playwright to extract menu items from a DoorDash restaurant page.
It navigates to the specified URL, extracts menu item JSON data embedded in the page's HTML, and formats it as a list of dictionaries, each containing the following keys:
    name: The name of the menu item.
    price: The price of the menu item (if available).
    description: The description of the menu item (if available)
    other keys: Additional information extracted from the menu item JSON data.

To use this script:
    1. Replace "YOUR_API_KEY_HERE" with your actual Scrapybara API key.
    2. Run the script.
    3. The menuItems (a list of dictionaries) in the main function will contain the extracted menu items.
"""
import asyncio
import json
from scrapybara import Scrapybara
from undetected_playwright.async_api import async_playwright

async def get_scrapybara_browser():
    client = Scrapybara(api_key="YOUR_API_KEY_HERE")
    instance = client.start_browser()
    return instance


def extract_menu_page_item_jsons(html_content: str):
    indexes = []  # List to store the indexes of the found substrings
    start = 0
    itemID = set()
    while True:# Find all occurrences of the substring {"__typename":"MenuPageItem"
        
        index = html_content.find('{"__typename":"MenuPageItem"', start)
        if index == -1:
            break 
        indexes.append(index) 
        start = index + 1 
    
    results = []
    for idx in indexes:
        s = ""
        i = idx
        counter = 0
        while True:
            s += html_content[i]
            if html_content[i] == "{":
                counter += 1
            elif html_content[i] == "}":
                counter -= 1
            i += 1
            if counter == 0:
                break
        dictItem = json.loads(s)
        del dictItem['nextCursor']
        del dictItem['__typename']
        del dictItem['storeId']
        dictItem["displayPrice"] = dictItem["displayPrice"][1:]
        if(dictItem["id"] not in itemID):
            itemID.add(dictItem["id"])
            results.append(dictItem)
            
    return results
        


async def retrieve_menu_items(instance, start_url: str) -> list[dict]:
    """
    Navigates to {start_url} using the Scrapybara instance and extracts menu item JSON data,
    formatting it as a list of dictionaries with name, price, and description and much more.
    """
    cdp_url = instance.get_cdp_url().cdp_url
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(cdp_url)
        page = await browser.new_page()
        await page.goto(start_url)
        # Wait for 1 second to allow the page to load (adjust as needed)
        await asyncio.sleep(1)
        # get the full HTML content of the page
        html_content = await page.content()
        cleaned_string = html_content.replace("\\", "") # remove '\' from the string to make json extraction easier
        menuItems = extract_menu_page_item_jsons(cleaned_string)
        return menuItems
        
    
async def main():
    instance = await get_scrapybara_browser()

    try:
        menuItems = await retrieve_menu_items(
            instance,
            "https://www.doordash.com/store/tim-hortons-kitchener-30818511/",
        )
    finally:
        # Be sure to close the browser instance after you're done!
        instance.stop()

if __name__ == "__main__":
    asyncio.run(main())
