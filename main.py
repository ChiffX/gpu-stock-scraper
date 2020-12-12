"""Scrapes computer part supplier websites for detecting stock of desired item.
Generates and sends email with link and details to in-stock item when detected.
"""

import random
import datetime
import time
import os
from scraping.scraping_functions import scrape_vendors, initialize_webdriver

# Comment/uncomment vendors and change URLs as needed, but keep the same webpage structure for each vendor.
vendors_to_scrape = {
    "Newegg": "https://www.newegg.ca/p/pl?d=Rtx+3080&N=50001402%2050001312%2050001315%2050012150%2050001314%20601357282%20100007708&LeftPriceRange=0+1300",
    "Best Buy": "https://www.bestbuy.ca/en-ca/collection/rtx-30-series-graphic-cards/316108?path=category%253AComputers%2B%2526%2BTablets%253Bcategory%253APC%2BComponents%253Bcategory%253AGraphics%2BCards%253Bcustom0graphicscardtype%253AGeForce%2BRTX%2B3080",
    "Memory Express": "https://www.memoryexpress.com/Category/VideoCards?FilterID=fdd27ae5-da44-3d27-95bc-3076cc5fc8f3",
    "Canada Computers": "https://www.canadacomputers.com/index.php?cPath=43_557_559&sf=:3_5&mfr=&pr=",
    "Amazon": "https://www.amazon.ca/stores/GeForce/RTX3080_GEFORCERTX30SERIES/page/6B204EA4-AAAC-4776-82B1-D7C3BD9DDC82",
    "PC Canada": "https://www.pc-canada.com/p/go/go.asp?CATID=10074&OPTID=111116290%2C1596338%7C%2C111114984%2C19789374",
}

# Used for email subject line only. URLs in vendors_to_scrape must be updated to actually scrape for it.
item = "RTX 3080"

def main():
    # Initial email message states. Prevents email spamming later.
    email_bodies = {
        "Newegg": "",
        "Best Buy": "",
        "Memory Express": "",
        "Canada Computers": "",
        "Amazon": "",
        "PC Canada": "",
    }

    userdefined_interval = os.getenv("INTERVAL")
    if userdefined_interval is not None:
        print(f"Using user defined interval of {userdefined_interval} (+random 15) seconds .\n")

    while True:
        # Timestamp for scan
        now = datetime.datetime.now()
        print(now.strftime("%Y-%m-%d %H:%M:%S"))

        try:
            driver = initialize_webdriver()
            # Scrapes all specified vendors
            for vendor_name, URL in vendors_to_scrape.items():
                email_body = scrape_vendors(vendor_name, URL, driver, item, email_bodies)
                email_bodies[vendor_name] = email_body
            driver.close()
        except Exception as e:
            print("Error: " + str(e))

        random_interval = random.randrange(15, 30)
        if userdefined_interval is None:
            # Waits 15 to 30 seconds before attempting next scan
            print(f"\nNext scan in {random_interval} seconds.\n")
            time.sleep(random_interval)
        else:
            interval = int(userdefined_interval) + random_interval
            print(f"\nNext scan in {interval} seconds.\n")
            time.sleep(interval)
        random.random()


if __name__ == "__main__":
    main()
