# GPU Stock Scraper

[![PyPI](https://img.shields.io/badge/Python-3.9-green.svg)]()

GPU Stock Scraper is a script to scrape various Canadian computer part supplier websites
and determine if stock exists for a given GPU.

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

## Usage

### Requirements
1. Download appropriate [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) to the `scraping/` folder
2. `pip3 install -r requirements.txt`
3. Create a .env file, using .env_sample as a guide, and input email information 
    * **NOTE**: This method is fairly insecure and Google will ask you to allow insecure apps to use this method
### Operation
`python3 main.py`

### Docker Usage
The docker image contains the chromedriver and python3, if you already have docker, you're good to go.
1. Build the image: `docker build -t gpu-stock-scraper .`
2. Run the image: `docker run --rm -t gpu-stock-scraper`
3. If you'd like email, mount in a a copy of the .env_sample called docker_env like so `docker run -v env:/usr/workspace/.env --rm -t gpu-stock-scraper`

### Optional customization
1. Modify search_canada_computers() to reflect your local stores
2. If using Windows, you can uncomment "import winsound" and beep() in scraping_functions.py to get 
a beep sound when stock is detected.
3. If you are receiving an error installing dotenv, try "pip3 install python-dotenv"


## Project Next Steps 
* Add model-specific filtering (meanwhile, filter via website then update URL)
* Improve ease of changing location
* Add pc-canada.com (currently receiving javascript errors with loading URL)
* Use a more secure method (potentially oauth) for sending emails
* Refine search_best_buy() to only return matches for select stores
* Incorporate functioning beep noise for both Linux and Windows when stock is detected


