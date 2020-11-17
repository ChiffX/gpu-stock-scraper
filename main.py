"""Scrapes computer part supplier websites for detecting stock of desired item.
Generates and sends email with link and details to in-stock item when detected.
"""

import random
import datetime
import time
from scraping_functions import search_newegg, search_bestbuy, search_memory_express, search_canada_computers


def main():
    while True:
        # Timestamp for scan
        now = datetime.datetime.now()
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        try:
            search_newegg(
                "https://www.newegg.ca/p/pl?d=Rtx+3080&N=50001402%2050001312%2050001315%2050012150%2050001314%20601357282%20100007708&LeftPriceRange=0+1300")
            search_bestbuy(
                "https://www.bestbuy.ca/en-ca/collection/rtx-30-series-graphic-cards/316108?path=category%253AComputers%2B%2526%2BTablets%253Bcategory%253APC%2BComponents%253Bcategory%253AGraphics%2BCards%253Bcustom0graphicscardtype%253AGeForce%2BRTX%2B3080")
            search_memory_express(
                "https://www.memoryexpress.com/Category/VideoCards?FilterID=fdd27ae5-da44-3d27-95bc-3076cc5fc8f3")
            search_canada_computers('https://www.canadacomputers.com/index.php?cPath=43_557_559&sf=:3_5&mfr=&pr=')
        except:
            print("Error")

        # Waits 30 to 90 seconds before attempting next scan
        random_interval = random.randrange(30, 90)
        print(f"\nNext scan in {random_interval} seconds.\n")
        time.sleep(random_interval)
        random.random()


if __name__ == "__main__":
    main()
