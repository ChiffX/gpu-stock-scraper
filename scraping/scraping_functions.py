"""This module contains the functions necessary to scan computer supplier webpages and send emails

Functions:
    initialize_webdriver()
    search_newegg()
    search_bestbuy()
    search_memoryexpress()
    search_canada_computers()
    search_pc_canada()
    send_email()
    beep()
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.mime.text import MIMEText
from fake_useragent import UserAgent
import os.path
from os import path
# import winsound   # Windows only
import smtplib
import dotenv
import os


def initialize_webdriver():
    """Initializes a chrome webdriver for use in the scraping functions.
    Generates a random user agent and run in a headless browser.
    Compatible with both Windows and Linux once chromedriver paths are set.

    :return: the initialized webdriver, ready to accept URLs
    """
    # Manually set the paths to Windows and/or Linux chromedriver location
    # Chrome Drivers fstockound here: https://sites.google.com/a/chromium.org/chromedriver/downloads
    WINDOWS_PATH = './chromedriver.exe'
    LINUX_PATH = './chromedriver'
    DOCKER_PATH = '/usr/local/bin/chromedriver'

    # Operates as a random user agent in a headless browser
    chromeOptions = Options()
    ua = UserAgent()
    userAgent = ua.random
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


def search_newegg(URL, previous_message, driver):
    """Scrapes a single newegg.ca webpage with multiple listings for any in-stock RTX 3080s.
    Sends an email with corresponding GPU details and link if stock is found.

    :param URL: a single newegg.ca webpage with multiple listings
    :param driver: an initialized webdriver
    :return: the email message body
    """
    # Title line
    vendor = "Newegg "
    while len(vendor) < 30:
        vendor += "-"
    print(vendor)

    # Check all GPU listings on page for stock
    stock_list = []

    driver.get(URL)
    driver.implicitly_wait(10)
    elements = driver.find_elements_by_class_name("item-operate")  # Contains stock information text
    for element in elements:
        if "OUT OF STOCK" not in element.text and "SOLD OUT" not in element.text:
            link_element = element.find_element_by_xpath('./../../div[1]/a')
            link = link_element.get_attribute("href")
            model = link_element.text
            stock_list.append(f"{model} is in stock at Newegg:\n"
                              f"{link}\n")
            print(link)

    # Generates an email message from the summary list
    email_message = ""
    for items in stock_list:
        email_message += items

    # If any on GPUs on page were found in stock, send an email
    if email_message != "" and email_message[:20] not in previous_message:
        print("Sending email.")
        subject = "RTX 3080 in Stock at Newegg"
        send_email(subject, email_message)
    elif email_message != "":
        print("Previous email items still in stock.")
    else:
        print("No stock found")

    return email_message


def search_bestbuy(URL, previous_message, driver):
    """Scrapes a single bestbuy.ca webpage with multiple listings for any in-stock RTX 3080s.
    Sends an email with corresponding GPU details and link if stock is found.
    Differentiates in-store vs online vs backorder stock.

    :param URL: a single bestbuy.ca webpage with multiple listings
    :param driver: an initialized webdriver
    :return: the email message body
    """
    # Title line
    vendor = "Best Buy "
    while len(vendor) < 30:
        vendor += "-"
    print(vendor)

    # Check all GPU listings on page for stock
    stock_list = []
    stock_type = []

    driver.get(URL)
    driver.implicitly_wait(10)
    elements = driver.find_elements_by_class_name("availabilityMessageSearch_23ZLw")  # Contains stock information text
    for element in elements:
        link_element = element.find_element_by_xpath('./../../../..')
        link = link_element.get_attribute("href")
        model = (element.find_element_by_xpath('./../div[1]')).text
        if "Available to ship" in element.text:
            stock_list.append(f"{model} is in stock online at Bestbuy:\n"
                              f"{link}\n")
            stock_type.append("online")
            print(link)
        elif "Available at nearby stores" in element.text:
            stock_list.append(f"{model} is available in store at Bestbuy:\n"
                              f"{link}\n")
            stock_type.append("store")
            print(link)
        elif "Available for backorder" in element.text:
            stock_list.append(f"{model} is available for backorder at Bestbuy:\n"
                              f"{link}\n")
            stock_type.append("backorder")
            print(link)

    # Generates an email message from the summary list
    email_message = ""
    for items in stock_list:
        email_message += items

    # If any on GPUs on page were found in stock, send an email
    if email_message != "" and email_message[:20] not in previous_message:
        print("Sending email.")
        if "online" in stock_type and "store" in stock_type:
            subject = "RTX 3080 in Stock ONLINE and IN STORE at Best Buy"
        elif "online" in stock_type:
            subject = "RTX 3080 in Stock ONLINE at Best Buy"
        elif "store" in stock_type:
            subject = "RTX 3080 in Stock IN STORE at Best Buy"
        elif "backorder" in stock_type:
            subject = "RTX 3080 available for BACKORDER at Best Buy"
        send_email(subject, email_message)
    elif email_message != "":
        print("Previous email items still in stock.")
    else:
        print("No stock found")


    return email_message


def search_memory_express(URL, previous_message, driver):
    """Scrapes a single memoryexpress.com webpage with multiple listings for any in-stock RTX 3080s.
    Sends an email with corresponding GPU details and link if stock is found.

    :param URL: a single memoryexpress.com webpage with multiple listings
    :param driver: an initialized webdriver
    :return: the email message body
    """
    # Title line
    vendor = "Memory Express "
    while len(vendor) < 30:
        vendor += "-"
    print(vendor)

    # Check all GPU listings on page for stock
    stock_dict = {}
    memory_express_urls = []
    store_to_check = "Vancouver"

    driver.get(URL)
    driver.implicitly_wait(10)
    elements = driver.find_elements_by_class_name("c-shca-add-product-button")  # Contains stock information text
    for element in elements:
        if "Buy this item" in element.get_attribute('title'):
            model_xpath = element.find_element_by_xpath('./../../../div[1]/div[2]/div[2]/a')
            link = model_xpath.get_attribute("href")
            memory_express_urls.append(link)

    # Iterates through individual pages for where stock may have been detected
    for URL in memory_express_urls:
            driver.get(URL)
            driver.implicitly_wait(10)

            # Stores GPU and link details
            item_name = driver.title.rstrip("- Memory Express Inc.")
            stock_dict[item_name] = {}
            stock_dict[item_name]["url"] = URL
            
            # Checks online stock status before proceeding
            stores_inventory = driver.find_elements_by_class_name('c-capr-inventory-store__name')
            for store_location in stores_inventory:
                if "Online Store" in store_location.text:
                    store_stock = (store_location.find_element_by_xpath('./../span[2]')).text
                    if store_stock != "Out of Stock" and int(store_stock.rstrip("+")) > 0:
                        print(f"Online stock found: \n{URL}")
                        stock_dict[item_name]["online stock status"] = "In stock"
                    else:
                        stock_dict[item_name]["online stock status"] = "Out of stock"

            # Expand the stores availability frame
            all_stores_toggle = driver.find_element_by_css_selector(".c-capr-inventory-selector__toggle")
            driver.execute_script("arguments[0].setAttribute('class','c-capr-inventory-selector__toggle c-capr-inventory-selector__toggle--opened')", all_stores_toggle)
            second_stores_toggle = driver.find_element_by_css_selector(".c-capr-inventory-selector__dropdown-container")
            driver.execute_script("arguments[0].setAttribute('class','c-capr-inventory-selector__dropdown-container')", second_stores_toggle)
            stores_inventory = driver.find_elements_by_class_name('c-capr-inventory-store__name')

            # Checks and stores local store stock status for GPU model
            stock_dict[item_name]["in store status"] = "No store stock"
            for store_location in stores_inventory:
                store_stock = (store_location.find_element_by_xpath('./../span[2]')).text
                if store_stock != "Out of Stock" and int(store_stock.rstrip("+")) > 0:
                    store_in_stock = (store_location.text).rstrip(':')
                    if store_to_check.lower() in store_in_stock.lower():
                        stock_dict[item_name]["in store status"] = "In store"
                        stock_dict[item_name]["store location"] = store_to_check
                    

    # Creates a summary list of items in stock, differentiating online vs in store
    stock_summary = []
    for model, details in stock_dict.items():
        if details["online stock status"] == "In stock":
            stock_summary.append(f"{model} is in stock ONLINE at Memory Express:\n"
                                 f"{details['url']}\n")
        if details["in store status"] == "In store":
            stock_summary.append(f"{model} is in stock IN STORE at Memory Express\n"
                                 f"{details['store location'].upper()}\n"
                                 f"{details['url']}\n")

    # Generates an email message from the summary list
    email_message = ""
    for items in stock_summary:
        email_message += items
        
    # If any on GPUs on page were found in stock, send an email, differentiating by stock type
    if email_message != "" and email_message[:20] not in previous_message:
        print("Sending email.")
        if "online" in email_message.lower() and "in store" in email_message.lower():
            subject = "RTX 3080 in Stock ONLINE and IN STORE at Memory Express"
        elif "online" in email_message.lower():
            subject = "RTX 3080 in Stock ONLINE at Memory Express"
        elif "in store" in email_message.lower():
            subject = "RTX 3080 in Stock IN STORE at Memory Express"
        send_email(subject, email_message) 
    elif email_message != "":
        print("Previous email items still in stock.")
    else:
        print("No stock found")

    return email_message


def search_canada_computers(URL, previous_message, driver):
    """Scrapes a single canadacomputers.com webpage with multiple listings for any in-stock RTX 3080s.
    Sends an email with corresponding GPU details and link if stock is found.
    Differentiates by in-store vs online.
    Searches for Richmond Hill or Markham in-store stock only.

    :param URL: a single canadacomputers.com webpage with multiple listings
    :param driver: an initialized webdriver
    :return: the email message body
    """
    # Title line
    vendor = "Canada Computers "
    while len(vendor) < 30:
        vendor += "-"
    print(vendor)

    # Stores all GPU models and respective online vs store stock status
    stock_dict = {}
    canada_computer_urls = []

    driver.get(URL)
    driver.implicitly_wait(10)
    stock_elements = driver.find_elements_by_class_name('pq-hdr-bolder')  # Contains stock information text
    for element in stock_elements:
        if "not available" not in element.text.lower() and "back order" not in element.text.lower():
            model_xpath = element.find_element_by_xpath('./../../../../../../div[1]/div/div[2]/span[1]/a')
            model = model_xpath.get_attribute("href")
            canada_computer_urls.append(model)

    # Iterates through individual pages for where stock may have been detected
    for URL in canada_computer_urls:
        driver.get(URL)
        driver.implicitly_wait(10)
        # Looks for items in stock online vs in store
        for elements in driver.find_elements_by_class_name('pi-prod-availability'):
            item_name = driver.title.rstrip("| Canada Computers & Electronics")
            stock_dict[item_name] = {}
            stock_dict[item_name]["url"] = URL
            # Checks and stores online stock status for GPU model
            if "Online In Stock" in elements.text:
                print(f"Online stock found: \n{URL}")
                stock_dict[item_name]["online stock status"] = "In stock"
            else:
                stock_dict[item_name]["online stock status"] = "Out of stock"

            # Checks and stores local store stock status for GPU model
            if "Available In Stores" in elements.text:
                # Opens inventory view for all stores
                other_stores = driver.find_element_by_css_selector(".stocklevel-pop")
                driver.execute_script("arguments[0].setAttribute('class','stocklevel-pop d-block')", other_stores)

                # Determines Richmond Hill Stock
                try:  # Sometimes the stock location changes
                    richmond_hill_stock = driver.find_element_by_xpath(
                        '//*[@id="pi-form"]/div[4]/div[3]/div[3]/div[20]/div/div[2]/div/p/span').text
                except:
                    richmond_hill_stock = driver.find_element_by_xpath(
                        '//*[@id="pi-form"]/div[2]/div[3]/div[3]/div[20]/div/div[2]/div/p/span').text
                if richmond_hill_stock == "-":
                    richmond_hill_stock = 0
                else:
                    richmond_hill_stock = int(richmond_hill_stock[0:1])  # Truncates 5+ to 5

                # Determine Markham Stock
                try:  # Sometimes the stock location changes
                    markham_stock = driver.find_element_by_xpath(
                        '//*[@id="pi-form"]/div[4]/div[3]/div[3]/div[13]/div/div[2]/div/p/span').text
                except:
                    markham_stock = driver.find_element_by_xpath(
                        '//*[@id="pi-form"]/div[2]/div[3]/div[3]/div[13]/div/div[2]/div/p/span').text
                if markham_stock == "-":
                    markham_stock = 0
                else:
                    markham_stock = int(markham_stock[0:1])  # Truncates 5+ to 5

                # Checks stock at chosen locations
                if richmond_hill_stock > 0 or markham_stock > 0:
                    print(f"In-store stock found: \n{URL}")
                    stock_dict[item_name]["in store status"] = "In store"
                    if richmond_hill_stock > 0:
                        stock_dict[item_name]["store location"] = "Richmond Hill"
                    elif markham_stock > 0:
                        stock_dict[item_name]["store location"] = "Markham Unionville"
                else:
                    stock_dict[item_name]["in store status"] = "No store stock"
            else:
                stock_dict[item_name]["in store status"] = "No store stock"

    # Creates a summary list of items in stock, differentiating online vs in store
    stock_summary = []
    for model, details in stock_dict.items():
        if details["online stock status"] == "In stock":
            stock_summary.append(f"{model} is in stock ONLINE at Canada Computers:\n"
                                 f"{details['url']}\n")
        if details["in store status"] == "In store":
            stock_summary.append(f"{model} is in stock IN STORE at Canada Computers\n"
                                 f"{details['store location'].upper()}\n"
                                 f"{details['url']}\n")

    # Generates an email message from the summary list
    email_message = ""
    for items in stock_summary:
        email_message += items

    # If any on GPUs on page were found in stock, send an email, differentiating by stock type
    if email_message != "" and email_message[:20] not in previous_message:
        print("Sending email.")
        if "online" in email_message.lower() and "in store" in email_message.lower():
            subject = "RTX 3080 in Stock ONLINE and IN STORE at Canada Computers"
        elif "online" in email_message.lower():
            subject = "RTX 3080 in Stock ONLINE at Canada Computers"
        elif "in store" in email_message.lower():
            subject = "RTX 3080 in Stock IN STORE at Canada Computers"
        send_email(subject, email_message) 
    elif email_message != "":
        print("Previous email items still in stock.")
    else:
        print("No stock found")

    return email_message


def search_pc_canada(URL, previous_message, driver):
    """Scrapes a single pc-canada.com webpage with multiple listings for any in-stock RTX 3080s.
    Sends an email with corresponding GPU details and link if stock is found.

    :param URL: a single pc-canada.com webpage with multiple listings
    :param driver: an initialized webdriver
    :return: the email message body
    """
    # Title line
    vendor = "PC Canada "
    while len(vendor) < 30:
        vendor += "-"
    print(vendor)

    # Check all GPU listings on page for stock
    stock_list = []

    driver.get(URL)
    driver.implicitly_wait(10)
    elements = driver.find_elements_by_class_name("text-theme-shipping")  # Contains stock information text
    for element in elements:
        if "On Backorder" not in element.text:
            link_element = element.find_element_by_xpath('./../../../../div[5]/div[1]/p/a')
            link = link_element.get_attribute("href")
            model = link_element.text
            stock_list.append(f"{model} is in stock at PC Canada:\n"
                              f"{link}\n")
            print(link)

    # Generates an email message from the summary list
    email_message = ""
    for items in stock_list:
        email_message += items

    # If any on GPUs on page were found in stock, send an email
    if email_message != "" and email_message[:20] not in previous_message:
        print("Sending email.")
        subject = "RTX 3080 in Stock at PC Canada"
        send_email(subject, email_message)
    elif email_message != "":
        print("Previous email items still in stock.")
    else:
        print("No stock found")

    return email_message


def send_email(subject, message):
    """Sends an email containing the in-stock GPU model and link to the desired recipients

    :param subject: a string containing the in-stock status type and which website
    :param message: a string containing in-stock model details and website link
    :return: none
    """
    # Manually input login information here
    # beep()  # Windows only

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
    
    msg = MIMEText(message)
    msg['Subject'] = subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(GMAIL_LOGIN, GMAIL_PASSWORD)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.close()


# Windows only
# def beep():
#     duration = 1000
#     freq = 1000
#     winsound.Beep(freq, duration)
