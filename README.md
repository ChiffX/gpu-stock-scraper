# GPU Stock Scraper

[![PyPI](https://img.shields.io/badge/Python-3.9-green.svg)]()

GPU Stock Scraper is a script to scrape various Canadian computer part supplier websites
and determine if stock exists for a given item.

#### Data Source Websites ####

At the time of this script, RTX 3080 are being scanned across:
* Newegg.ca
    * Checks online stock
* Bestbuy.ca
    * Differentiates online vs backorder vs nearby-store stock
* Memoryexpress.com
    * Differentiates online vs in-store stock
    * Allows selection of specific stores
* Canadacomputers.com
    * Differentiates online vs in-store stock
    * Allows selection of specific stores
* Amazon.ca
    * Checks online stock
* PC-canada.com
    * Checks online stock

## Usage

### Requirements
1. Download appropriate [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) to the `scraping/` folder
2. `pip3 install -r requirements.txt`

### Enabling Gmail
* **NOTE**: This method is fairly insecure and Google will ask you to allow insecure apps to use this method
1. Go to the [Less secure app access section of your Google Account](https://myaccount.google.com/lesssecureapps). You might need to sign in.
2. Turn Allow less secure apps on.
3. Create a .env file, using .env_sample as a guide, and input email information 

### Enabling Discord Messages
1. Acquire your webhook URL from your Discord server for your selected channel
    * See here for an explanation: https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
2. Assign your webhook URL to DISCORD_WEBHOOK in your .env file
3. Set discord_message_enabled to True

### Operation
`python3 main.py`

### Docker Usage
The docker image contains the chromedriver and python3, if you already have docker, you're good to go.
1. Build the image: `docker build -t gpu-stock-scraper .`
2. Run the image: `docker run --rm -t gpu-stock-scraper`
3. If you'd like email, set these environment variables `docker run -e EMAIL=${EMAIL} -e PASSWORD=${PASSWORD} -e RECIPIENT1=${RECIPIENT1} -e RECIPIENT2=${RECIPIENT2} --rm -t gpu-stock-scraper`
4. If you'd like to change the base interval frequency, add the INTERVAL environment variable `docker run -e INTERVAL=60 --rm -t gpu-stock-scraper`

### Optional customization
1. Modify stores_to_check in scrape_canada_computers() and scrape_memory_express() to reflect your local stores
2. If you are receiving an error installing dotenv, try "pip3 install python-dotenv"


## Project Next Steps 
* Add model-specific filtering (meanwhile, filter via website then update URL)
* Use a more secure method (potentially oauth) for sending emails
* Refine search_best_buy() to only return matches for select stores
* Build a config file


