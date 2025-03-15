"""
This script demonstrates how to use Scrapybara with Playwright to extract menu items from a DoorDash restaurant page.
It navigates to the specified URL, extracts menu item JSON data embedded in the page's HTML, and formats it as a list of dictionaries, each containing the following keys:
    name: The name of the menu item.
    price: The price of the menu item (if available).
    description: The description of the menu item (if available)

To use this script:
    1. Replace "YOUR_API_KEY_HERE" with your actual Scrapybara API key.
    2. Run the script.
    3. The menuItems (a list of dictionaries) in the main function will contain the extracted menu items.
"""

import asyncio
import json
import re
from scrapybara import Scrapybara
from undetected_playwright.async_api import async_playwright

async def get_scrapybara_browser():
    client = Scrapybara(api_key="YOUR_API_KEY_HERE")
    instance = client.start_browser()
    return instance

async def retrieve_menu_items(instance, start_url: str) -> list[dict]:
    """
    Navigates to {start_url} using the Scrapybara instance and extracts menu item JSON data,
    formatting it as a list of dictionaries with name, price, and description.
    Example: [{"name": "Sprite", "price": "$3.00", "description": "Yummy drink"}, ...]
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
        # Define a regex pattern to match JSON objects from HTML
        pattern = r'{"@type":"MenuItem","name":"[^"]+",(?:"description":"[^"]*",)?"offers":{"@type":"Offer"(?:,"price":"[^"]*")?}}'
        matches = re.findall(pattern, html_content)
        formatted_items = []
        
        for match in matches:
            try:
                item_data = json.loads(match)
                name = item_data.get("name", "")
                description = item_data.get("description", "")
                price = ""
                # Check if the "offers" key exists and is a dictionary
                if isinstance(item_data.get("offers", {}), dict):
                    price = item_data["offers"].get("price", "")
                new_item = {"name": name, "price": price, "description": description}
                # Check if an item with the same name already exists in the list
                existing_item = next((item for item in formatted_items if item["name"] == name), None)
                if existing_item:
                    # If the existing item has less information (e.g., missing description or price),
                    # replace it with the new item
                    if (not existing_item["description"] and description) or (not existing_item["price"] and price):
                        formatted_items.remove(existing_item)
                        formatted_items.append(new_item)
                else:
                    # If the name is not in the list, add the new item
                    formatted_items.append(new_item)  
            except json.JSONDecodeError:
                # Handle json parsing errors by printing a warning
                print(f"Failed to parse JSON: {match[:50]}...")
        return formatted_items
    
    
async def main():
    instance = await get_scrapybara_browser()

    try:
        menuItems = await retrieve_menu_items(
            instance,
            "https://www.doordash.com/store/panda-express-san-francisco-980938/12722988/?event_type=autocomplete&pickup=false",
        )
        # Print the extracted menu items        
    finally:
        # Be sure to close the browser instance after you're done!
        instance.stop()

if __name__ == "__main__":
    asyncio.run(main())