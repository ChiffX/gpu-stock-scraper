"""This module contains the functions necessary to scan computer supplier webpages and send emails

Functions:
    initialize_webdriver()
    search_newegg()
    search_bestbuy()
    search_memoryexpress()
    search_canada_computers()
    send_email()
    beep()
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.mime.text import MIMEText
from fake_useragent import UserAgent
# import winsound   # Windows only
import smtplib


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

    # Operates as a random user agent in a headless browser
    chromeOptions = Options()
    ua = UserAgent()
    userAgent = ua.random
    chromeOptions.add_argument(f'user-agent={userAgent}')
    chromeOptions.headless = True

    try:
        driver = webdriver.Chrome(executable_path=WINDOWS_PATH, options=chromeOptions)
    except:
        driver = webdriver.Chrome(executable_path=LINUX_PATH, options=chromeOptions)
    driver.get('chrome://settings/clearBrowserData')

    return driver


def search_newegg(URL):
    """Scrapes a single newegg.ca webpage with multiple listings for any in-stock RTX 3080s.
    Sends an email with corresponding GPU details and link if stock is found.

    :param URL: a single newegg.ca webpage with multiple listings
    :return: none
    """
    # Title line
    vendor = "Newegg "
    while len(vendor) < 30:
        vendor += "-"
    print(vendor)

    # Check all GPU listings on page for stock
    stock_list = []

    driver = initialize_webdriver()
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
    if email_message != "":
        print("Sending email.")
        subject = "RTX 3080 in Stock at Newegg"
        send_email(subject, email_message)
    else:
        print("No stock found")
    driver.close()


def search_bestbuy(URL):
    """Scrapes a single bestbuy.ca webpage with multiple listings for any in-stock RTX 3080s.
    Sends an email with corresponding GPU details and link if stock is found.
    Differentiates in-store vs online vs backorder stock.

    :param URL: a single bestbuy.ca webpage with multiple listings
    :return: none
    """
    # Title line
    vendor = "Best Buy "
    while len(vendor) < 30:
        vendor += "-"
    print(vendor)

    # Check all GPU listings on page for stock
    stock_list = []
    stock_type = []

    driver = initialize_webdriver()
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
    if email_message != "":
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
    else:
        print("No stock found")

    driver.close()


def search_memory_express(URL):
    """Scrapes a single memoryexpress.com webpage with multiple listings for any in-stock RTX 3080s.
    Sends an email with corresponding GPU details and link if stock is found.

    :param URL: a single memoryexpress.com webpage with multiple listings
    :return: none
    """
    # Title line
    vendor = "Memory Express "
    while len(vendor) < 30:
        vendor += "-"
    print(vendor)

    # Check all GPU listings on page for stock
    stock_list = []

    driver = initialize_webdriver()
    driver.get(URL)
    driver.implicitly_wait(10)
    elements = driver.find_elements_by_class_name("c-shca-add-product-button")  # Contains stock information text
    for element in elements:
        # print(element.get_attribute('title'))
        if "Buy this item" in element.get_attribute('title'):
            stock_list.append("In stock")

    # If any on GPUs on page were found in stock, send an email
    if "In stock" in stock_list:
        print("Sending email.")
        subject = "RTX 3080 in Stock at Memory Express"
        message = f"In stock: {URL}"
        send_email(subject, message)

    else:
        print("No stock found")
    driver.close()


def search_canada_computers(URL):
    """Scrapes a single canadacomputers.com webpage with multiple listings for any in-stock RTX 3080s.
    Sends an email with corresponding GPU details and link if stock is found.
    Differentiates by in-store vs online.
    Searches for Richmond Hill or Markham in-store stock only.

    :param URL: a single canadacomputers.com webpage with multiple listings
    :return: none
    """
    # Title line
    vendor = "Canada Computers "
    while len(vendor) < 30:
        vendor += "-"
    print(vendor)

    # Stores all GPU models and respective online vs store stock status
    stock_dict = {}
    canada_computer_urls = []

    driver = initialize_webdriver()
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
                print(f"Online stock found: {URL}")
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
                    print(f"In-store stock found: {URL}")
                    stock_dict[item_name]["in store status"] = "In store"
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
            stock_summary.append(f"{model} is in stock IN STORE at Canada Computers:\n"
                                 f"{details['url']}\n")

    # Generates an email message from the summary list
    email_message = ""
    for items in stock_summary:
        email_message += items

    # If any on GPUs on page were found in stock, send an email, differentiating by stock type
    if email_message != "":
        print("Sending email.")
        if "online" in email_message.lower() and "in store" in email_message.lower():
            subject = "RTX 3080 in Stock ONLINE and IN STORE at Canada Computers"
        elif "online" in email_message.lower():
            subject = "RTX 3080 in Stock ONLINE at Canada Computers"
        elif "in store" in email_message.lower():
            subject = "RTX 3080 in Stock IN STORE at Canada Computers"
        send_email(subject, email_message)
    else:
        print("No stock found")
    driver.close()


def send_email(subject, message):
    """Sends an email containing the in-stock GPU model and link to the desired recipients

    :param subject: a string containing the in-stock status type and which website
    :param message: a string containing in-stock model details and website link
    :return: none
    """
    # Manually input login information here
    # beep()  # Windows only

    GMAIL_LOGIN = 'example_email@gmail.com'
    GMAIL_PASSWORD = 'password'

    from_addr = GMAIL_LOGIN
    to_addr = ["example_email1@gmail.com",
               "example_email2@gmail.com"
               ]
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
