"""This module contains the functions necessary to scan computer supplier webpages and send emails

Functions:
    initialize_webdriver()
    scrape_vendors()
    scrape_newegg()
    scrape_bestbuy()
    scrape_memoryexpress()
    scrape_canada_computers()
    scrape_amazon()
    scrape_pc_canada()
    maybe_send_email()
    send_email()
    send_discord_message()
    title_line()
    beep()
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.mime.text import MIMEText
from fake_useragent import UserAgent
import os.path
from os import path
import requests
from discord import Webhook, RequestsWebhookAdapter, Embed
# import winsound   # Windows only
import smtplib
import dotenv
import os


# Optional use of send_discord_message() and send_email() functions. Set to True for on
discord_enabled = True
email_enabled = True


def initialize_webdriver():
    """Initializes a chrome webdriver for use in the scraping functions.
    Generates a random user agent and run in a headless browser.
    Compatible with both Windows and Linux once chromedriver paths are set.

    :return: the initialized webdriver, ready to accept URLs
    """
    # Manually set the paths to Windows and/or Linux chromedriver location
    # Chrome Drivers found here: https://sites.google.com/a/chromium.org/chromedriver/downloads
    WINDOWS_PATH = './chromedriver.exe'
    LINUX_PATH = './chromedriver'
    DOCKER_PATH = '/usr/local/bin/chromedriver'

    # Operates as a random user agent in a headless browser
    chromeOptions = Options()
    ua = UserAgent()
    userAgent = ua.random
    chromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])
    chromeOptions.add_argument(f'user-agent={userAgent}')
    chromeOptions.headless = True

    if (path.exists(WINDOWS_PATH)):
        driver = webdriver.Chrome(executable_path=WINDOWS_PATH, options=chromeOptions)
    elif (path.exists(LINUX_PATH)):
        driver = webdriver.Chrome(executable_path=LINUX_PATH, options=chromeOptions)
    else:
        chromeOptions.add_argument('--no-sandbox')
        chromeOptions.add_argument('--headless')
        chromeOptions.add_argument('--disable-gpu')
        driver = webdriver.Chrome(executable_path=DOCKER_PATH, options=chromeOptions)
        
    driver.get('chrome://settings/clearBrowserData')

    return driver


def scrape_vendors(vendor_name, URL, driver, item, email_bodies):
    """Scrapes respective vendor URL to detect any stock for the given item

    :param vendor_name: a given vendor name, specified in main.py
    :param URL: a respective URL to scrape, attached to vendor_name
    :param driver: an initialized webdriver
    :param item: the name of the item to check stock for
    :param email_bodies: the email body from the previous email sent, "" if no previous body
    :return: email_body if vendor_name is valid
    """
    title_line(vendor_name)

    driver.get(URL)
    driver.implicitly_wait(10)

    # Scrape all vendors specified in main.py. Sends email if stock is detected.
    if vendor_name.lower().strip() == "newegg":
        email_body = scrape_newegg(driver, vendor_name)
        maybe_send_email(item, email_body, email_bodies, vendor_name)
        return email_body
    elif vendor_name.lower().strip() == "best buy":
        email_body = scrape_bestbuy(driver, vendor_name)
        maybe_send_email(item, email_body, email_bodies, vendor_name)
        return email_body
    elif vendor_name.lower().strip() == "memory express":
        email_body = scrape_memory_express(driver, vendor_name)
        maybe_send_email(item, email_body, email_bodies, vendor_name)
        return email_body
    elif vendor_name.lower().strip() == "canada computers":
        email_body = scrape_canada_computers(driver, vendor_name)
        maybe_send_email(item, email_body, email_bodies, vendor_name)
        return email_body
    elif vendor_name.lower().strip() == "amazon":
        email_body = scrape_amazon(driver, vendor_name)
        maybe_send_email(item, email_body, email_bodies, vendor_name)
        return email_body
            
    elif vendor_name.lower().strip() == "pc canada":
        email_body = scrape_pc_canada(driver, vendor_name)
        maybe_send_email(item, email_body, email_bodies, vendor_name)
        return email_body
    else:
        raise ValueError("Vendor specified does not match existing vendors.")


def scrape_newegg(driver, vendor_name):
    """Scrapes a single newegg.ca webpage with multiple listings for any in-stock items.

    :param driver: an initialized webdriver
    :param vendor_name: the name of the vendor for the respective webpage
    :return: email_body
    """
    # Check all listings on page for stock
    stock_dict = {}

    stock_status_elements = driver.find_elements_by_class_name("item-operate")  # Contains stock information text
    for stock_status in stock_status_elements:
        if "OUT OF STOCK" not in stock_status.text and "SOLD OUT" not in stock_status.text:
            # Secondary check to prevent false-positives for auto notify button
            secondary_stock_status_element = (stock_status.find_element_by_xpath('./../../div[2]/div/div[1]/button')).text
            if "AUTO NOTIFY" not in secondary_stock_status_element:
                item_URL_element = stock_status.find_element_by_xpath('./../../div[1]/a')
                item_URL = item_URL_element.get_attribute("href")
                item_name = item_URL_element.text
                stock_dict[item_name] = {}
                stock_dict[item_name]["url"] = item_URL
                print(f"Online stock found: \n{item_URL}")
                stock_dict[item_name]["online stock status"] = "In stock"
                stock_dict[item_name]["in store status"] = "Not checked"
                stock_dict[item_name]["backorder status"] = "Not checked"

    email_body = generate_email_body(stock_dict, vendor_name)

    return email_body


def scrape_bestbuy(driver, vendor_name):
    """Scrapes a single bestbuy.ca webpage with multiple listings for any in-stock items.

    :param vendor_name: the name of the webpage vendor
    :param driver: an initialized webdriver
    :return: the email message body
    """
    # Check all listings on page for stock
    stock_dict = {}

    stock_status_elements = driver.find_elements_by_class_name("availabilityMessageSearch_23ZLw")  # Contains stock information text
    for stock_status in stock_status_elements:
        item_URL_element = stock_status.find_element_by_xpath('./../../../..')
        item_URL = item_URL_element.get_attribute("href")
        item_name = (stock_status.find_element_by_xpath('./../div[1]')).text
        if ("Available to ship" in stock_status.text
            or "Available online only" in stock_status.text
            or "Available at nearby stores" in stock_status.text
            or "Available for backorder" in stock_status.text):
            stock_dict[item_name] = {}
            stock_dict[item_name]["url"] = item_URL
        
            # Online
            if "Available to ship" in stock_status.text or "Available online only" in stock_status.text:
                print(f"Online stock found: \n{item_URL}")
                stock_dict[item_name]["online stock status"] = "In stock"
            else:
                stock_dict[item_name]["online stock status"] = "Out of stock"

            # In store    
            if "Available at nearby stores" in stock_status.text:
                stock_dict[item_name]["in store status"] = "In store"
                stock_dict[item_name]["store location"] = "Store location unspecified"
            else:
                stock_dict[item_name]["in store status"] = "Unavailable in store"

            # Backorder
            if "Available for backorder" in stock_status.text:
                print(f"Backorder stock found: \n{item_URL}")
                stock_dict[item_name]["backorder status"] = "Available for backorder"
            else:
                stock_dict[item_name]["backorder status"] = "Unavailable for backorder"

    email_body = generate_email_body(stock_dict, vendor_name)

    return email_body


def scrape_memory_express(driver, vendor_name):
    """Scrapes a single memoryexpress.com webpage with multiple listings for any in-stock items.

    :param vendor_name: the name of the webpage vendor
    :param driver: an initialized webdriver
    :return: email_body
    """
    # Add or comment/uncomment desired store location names here, case sensitive
    stores_to_check = [
        "Vancouver",
        "Victoria",
        "Burnaby",
        "Richmond",
    ]

    # Check all listings on page for stock
    memory_express_urls = []
    
    stock_status_elements = driver.find_elements_by_class_name("c-shca-add-product-button")  # Contains stock information text
    for stock_status in stock_status_elements:
        if "Buy this item" in stock_status.get_attribute('title'):
            item_URL_element = stock_status.find_element_by_xpath('./../../../div[1]/div[2]/div[2]/a')
            item_URL = item_URL_element.get_attribute("href")
            memory_express_urls.append(item_URL)

    # Iterates through individual pages for where stock may have been detected
    stock_dict = {}
    for URL in memory_express_urls:
        driver.get(URL)
        driver.implicitly_wait(10)

        # Stores item and link details
        item_name = driver.title.rstrip("- Memory Express Inc.")
        stock_dict[item_name] = {}
        stock_dict[item_name]["url"] = URL
        
        # Checks online stock status before proceeding
        stores_inventory = driver.find_elements_by_class_name('c-capr-inventory-store__name')
        for store_location in stores_inventory:
            if "Online Store" in store_location.text:
                store_stock = (store_location.find_element_by_xpath('./../span[2]')).text
                if (store_stock != "Out of Stock" 
                    and store_stock != "Backorder"
                    and int(store_stock.rstrip("+")) > 0):
                    print(f"Online stock found: \n{URL}")
                    stock_dict[item_name]["online stock status"] = "In stock"
                else:
                    stock_dict[item_name]["online stock status"] = "Out of stock"

        if len(stores_to_check) != 0:
            # Expand the stores availability frame
            all_stores_toggle = driver.find_element_by_css_selector(".c-capr-inventory-selector__toggle")
            driver.execute_script("arguments[0].setAttribute('class','c-capr-inventory-selector__toggle c-capr-inventory-selector__toggle--opened')", all_stores_toggle)
            second_stores_toggle = driver.find_element_by_css_selector(".c-capr-inventory-selector__dropdown-container")
            driver.execute_script("arguments[0].setAttribute('class','c-capr-inventory-selector__dropdown-container')", second_stores_toggle)
            stores_inventory = driver.find_elements_by_class_name('c-capr-inventory-store__name')

            # Checks and stores local store stock status for item
            stock_dict[item_name]["in store status"] = "No store stock"
            for store_location in stores_inventory:
                store_stock = (store_location.find_element_by_xpath('./../span[2]')).text
                if (store_stock != "Out of Stock" 
                    and store_stock != "Backorder" 
                    and int(store_stock.rstrip("+")) > 0):
                    store = (store_location.text).rstrip(':')
                    if store in stores_to_check:
                        print(f"In-store stock found at {store}: \n{URL}")
                        stock_dict[item_name]["in store status"] = "In store"
                        if "store location" in stock_dict[item_name]:
                            stock_dict[item_name]["store location"] += f", {store}"
                        else:
                            stock_dict[item_name]["store location"] = store 
        else:
            stock_dict[item_name]["in store status"] = "Not checked" 

        stock_dict[item_name]["backorder status"] = "Not checked"
        
    email_body = generate_email_body(stock_dict, vendor_name)

    return email_body


def scrape_canada_computers(driver, vendor_name):
    """Scrapes a single canadacomputers.com webpage with multiple listings for any in-stock items.

    :param vendor_name: the name of the webpage vendor
    :param driver: an initialized webdriver
    :return: email_body
    """
    # Add or comment/uncomment desired store location names here, case sensitive
    stores_to_check = [
        "Markham Unionville",
        "Midtown Toronto",
        "Richmond Hill",
        "Toronto 284",
        "Vancouver Broadway",
        "East Vancouver",
        "Burnaby",
        "Richmond",
    ]

    # Check all listings on page for stock
    canada_computer_urls = []

    stock_status_elements = driver.find_elements_by_class_name('pq-hdr-bolder')  # Contains stock information text
    for stock_status in stock_status_elements:
        if "not available" not in stock_status.text.lower() and "back order" not in stock_status.text.lower():
            item_URL_element = stock_status.find_element_by_xpath('./../../../../../../div[1]/div/div[2]/span[1]/a')
            item_URL = item_URL_element.get_attribute("href")
            canada_computer_urls.append(item_URL)

    # Iterates through individual pages for where stock may have been detected
    stock_dict = {}
    for URL in canada_computer_urls:
        driver.get(URL)
        driver.implicitly_wait(10)
        # Looks for items in stock online vs in store
        for elements in driver.find_elements_by_class_name('pi-prod-availability'):
            item_name = driver.title.rstrip("| Canada Computers & Electronics")
            stock_dict[item_name] = {}
            stock_dict[item_name]["url"] = URL
            # Checks and stores online stock status for item
            if "Online In Stock" in elements.text:
                print(f"Online stock found: \n{URL}")
                stock_dict[item_name]["online stock status"] = "In stock"
            else:
                stock_dict[item_name]["online stock status"] = "Out of stock"

            # Checks and stores local store stock status for item
            if len(stores_to_check) != 0:
                if "Available In Stores" in elements.text:
                    # Opens inventory view for all stores
                    other_stores = driver.find_element_by_css_selector(".stocklevel-pop")
                    driver.execute_script("arguments[0].setAttribute('class','stocklevel-pop d-block')", other_stores)

                    # Only changes if stock at desired store is detected
                    stock_dict[item_name]["in store status"] = "No store stock"

                    for store in stores_to_check:
                        # Finds store's name on webpage
                        store_element = driver.find_element_by_link_text(store)
                        # Finds stock value by xpath relative to store name
                        stock = store_element.find_element_by_xpath('./../../../div[2]/div/p/span').text

                        # Converts stock value into integer
                        if stock == "-":
                            stock = 0
                        else:
                            stock = int(stock[0:1])  # Truncates 5+ to 5
                        
                        if stock > 0:
                            print(f"In-store stock found at {store}: \n{URL}")
                            stock_dict[item_name]["in store status"] = "In store"
                            if "store location" in stock_dict[item_name]:
                                stock_dict[item_name]["store location"] += f", {store}"
                            else:
                                stock_dict[item_name]["store location"] = store 
                else:
                    stock_dict[item_name]["in store status"] = "No store stock"
            else:
                stock_dict[item_name]["in store status"] = "Not checked"
            
            stock_dict[item_name]["backorder status"] = "Not checked"
            
    email_body = generate_email_body(stock_dict, vendor_name)

    return email_body


def scrape_amazon(driver, vendor_name):
    """Scrapes a single amazon.ca webpage with multiple listings for any in-stock items.

    :param driver: an initialized webdriver
    :param vendor_name: the name of the vendor for the respective webpage
    :return: email_body
    """
    # Check all listings on page for stock
    stock_dict = {}

    stock_status_elements = driver.find_elements_by_class_name("style__whole__3EZEk")  # Contains price information if in stock
    for stock_status in stock_status_elements:
        price = float((stock_status.text).replace(",", ""))
        # Set price limit here
        if price < 1300:
            item_URL_element = stock_status.find_element_by_xpath('./../../../../../../../div[1]/a')
            item_URL = item_URL_element.get_attribute("href")
            item_name_element = stock_status.find_element_by_xpath('./../../../../div[1]/a')
            item_name = item_name_element.text
            stock_dict[item_name] = {}
            stock_dict[item_name]["url"] = item_URL
            print(f"Online stock found: \n{item_URL}")
            stock_dict[item_name]["online stock status"] = "In stock"
            stock_dict[item_name]["in store status"] = "Not checked"
            stock_dict[item_name]["backorder status"] = "Not checked"

    email_body = generate_email_body(stock_dict, vendor_name)

    return email_body


def scrape_pc_canada(driver, vendor_name):
    """Scrapes a single pc-canada.com webpage with multiple listings for any in-stock items.

    :param vendor_name: the name of the webpage vendor
    :param driver: an initialized webdriver
    :return: email_body
    """

    # Check all listings on page for stock
    stock_dict = {}

    stock_status_elements = driver.find_elements_by_css_selector("p.text-theme-shipping")  # Contains stock information text
    for stock_status in stock_status_elements:
        if "On Backorder" not in stock_status.text and "" != stock_status.text:
            item_URL_element = stock_status.find_element_by_xpath('./../../../../div[5]/div[1]/p/a')
            item_URL = item_URL_element.get_attribute("href")
            item_name = item_URL_element.text
            print(item_name)
            stock_dict[item_name] = {}
            stock_dict[item_name]["url"] = item_URL
            print(f"Online stock found: \n{item_URL}")
            stock_dict[item_name]["online stock status"] = "In stock"
            stock_dict[item_name]["in store status"] = "Not checked"
            stock_dict[item_name]["backorder status"] = "Not checked"

    email_body = generate_email_body(stock_dict, vendor_name)

    return email_body


def generate_email_body(stock_dict, vendor_name):
    """Generates an email body based on passed stock dictionary and vendor

    :param stock_dict: a stock summary dictionary created in the scraping function
    :param vendor_name: the name of the vendor that was scraped
    """
    # Creates a summary list of items in stock, differentiating online vs in store
    stock_summary = []
    for item, details in stock_dict.items():
        if details["online stock status"] == "In stock":
            stock_summary.append(f"{item} is in stock ONLINE at {vendor_name}\n"
                                 f"{details['url']}\n\n")
        if details["in store status"] == "In store":
            stock_summary.append(f"{item} is in stock IN STORE at {vendor_name}\n"
                                 f"{details['store location'].upper()}\n"
                                 f"{details['url']}\n\n")
        if details["backorder status"] == "Available for backorder":
            stock_summary.append(f"{item} is AVAILABLE FOR BACKORDER at {vendor_name}\n"
                                 f"{details['url']}\n\n")                        

    # Generates an email message from the summary list
    email_body = ""
    for hits in stock_summary:
        email_body += hits

    return email_body


def maybe_send_email(item, email_body, email_bodies, vendor_name):
    """Sends an email if the email body is not blank and is not the same as the previous email body
    Prevents spamming emails. Optionally sends a discord message too.

    :param email_body: a string containing in-stock items
    :return: none
    """
    if email_body != "" and email_body[:20] not in email_bodies[vendor_name]:
        print("Sending email.")
        if "online" in email_body.lower() and "in store" in email_body.lower():
            subject = f"{item} in Stock ONLINE and IN STORE at {vendor_name}"
        elif "online" in email_body.lower():
            subject = f"{item} in Stock ONLINE at {vendor_name}"
        elif "in store" in email_body.lower():
            subject = f"{item} in Stock IN STORE at {vendor_name}"
        elif "backorder" in email_body.lower():
            subject = f"{item} available for BACKORDER at {vendor_name}"
        if discord_enabled:
            try:
                send_discord_message(subject, email_body)
            except:
                print("Error with sending discord message.")
        if send_email:
            send_email(subject, email_body) 
    elif email_body != "":
        print("Previous email items still in stock.")
    else:
        print("No stock found")


def send_email(subject, email_body):
    """Sends an email containing the in-stock item details and link to the desired recipients

    :param subject: a string containing the in-stock status type and which website
    :param email_body: a string containing in-stock model details and website link
    :return: none
    """
    # Load sensitive login data from local .env file
    dotenv.load_dotenv()
    GMAIL_LOGIN = os.getenv('EMAIL')
    GMAIL_PASSWORD = os.getenv('PASSWORD')
    RECIPIENTS = []
    if os.getenv("RECIPIENT1") is not None:
        RECIPIENTS.append(os.getenv("RECIPIENT1"))
    if os.getenv("RECIPIENT2") is not None:
        RECIPIENTS.append(os.getenv("RECIPIENT2"))
    
    to_addr = RECIPIENTS
    from_addr = GMAIL_LOGIN
    
    msg = MIMEText(email_body)
    msg['Subject'] = subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(GMAIL_LOGIN, GMAIL_PASSWORD)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.close()


def title_line(vendor_name):
    """Prints the vendor name surrounded by "---" for readability in terminal"""
    vendor_name = vendor_name + " "
    while len(vendor_name) < 30:
        vendor_name += "-"
    print(vendor_name)


def send_discord_message(subject, email_body):
    """Sends an embedded message to your specific discord channel
    
    :param subject: the subject line of an email message
    :param email_body: the email body of an email message
    """
    dotenv.load_dotenv()
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    webhook = Webhook.from_url(webhook_url, adapter=RequestsWebhookAdapter())
    embed = Embed(title=subject, description=email_body)
    webhook.send(embed=embed)

# Windows only
# def beep():
#     duration = 1000
#     freq = 1000
#     winsound.Beep(freq, duration)