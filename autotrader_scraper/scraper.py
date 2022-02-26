import json
import csv
import logging
from bs4 import BeautifulSoup
import traceback
import cloudscraper

keywords = {"mileage": ["miles"],
            "BHP": ["BHP"],
            "transmission": ["Automatic", "Manual"],
            "fuel": ["Petrol", "Diesel", "Electric", "Hybrid – Diesel/Electric Plug-in", "Hybrid – Petrol/Electric",
                     "Hybrid – Petrol/Electric Plug-in"],
            "owners": ["owners"],
            "body": ["Coupe", "Convertible", "Estate", "Hatchback", "MPV", "Pickup", "SUV", "Saloon"],
            "ULEZ": ["ULEZ"],
            "year": [" reg)"],
            "engine": ["engine"]}


def get_car_details(article):
    car = {"name": article.find("h3", {"class": "product-card-details__title"}).text.strip(),
           "link": "https://www.autotrader.co.uk" + \
                   article.find("a", {"class": "tracking-standard-link"})["href"][
                   : article.find("a", {"class": "tracking-standard-link"})["href"].find("?")],
           "price": article.find("div", {"class": "product-card-pricing__price"}).text.strip().replace(",", "")}

    key_specs_bs_list = article.find("ul", {"class": "listing-key-specs"}).find_all("li")

    for key_spec_bs_li in key_specs_bs_list:

        key_spec_bs = key_spec_bs_li.text

        if any(keyword in key_spec_bs for keyword in keywords["mileage"]):
            car["mileage"] = int(key_spec_bs[:key_spec_bs.find(" miles")].replace(",", ""))
        elif any(keyword in key_spec_bs for keyword in keywords["BHP"]):
            car["BHP"] = int(key_spec_bs[:key_spec_bs.find("BHP")])
        elif any(keyword in key_spec_bs for keyword in keywords["transmission"]):
            car["transmission"] = key_spec_bs
        elif any(keyword in key_spec_bs for keyword in keywords["fuel"]):
            car["fuel"] = key_spec_bs
        elif any(keyword in key_spec_bs for keyword in keywords["owners"]):
            car["owners"] = int(key_spec_bs[:key_spec_bs.find(" owners")])
        elif any(keyword in key_spec_bs for keyword in keywords["body"]):
            car["body"] = key_spec_bs
        elif any(keyword in key_spec_bs for keyword in keywords["ULEZ"]):
            car["ULEZ"] = key_spec_bs
        elif any(keyword in key_spec_bs for keyword in keywords["year"]):
            car["year"] = key_spec_bs
        elif key_spec_bs[1] == "." and key_spec_bs[3] == "L":
            car["engine"] = key_spec_bs

    return car


def get_page_html(url, scraper, params={}, max_attempts_per_page=5):

    attempt = 1
    while attempt <= max_attempts_per_page:

        r = scraper.get(url, params=params)
        logging.info(f"Response: {r}")

        if r.status_code == 200:
            first_character = r.text[0]
            if first_character == '{':
                page_html = r.json()["html"]
            elif first_character == '<':
                page_html = r.text
            else:
                raise Exception(f'Unknown start to reponse from {r.url}: {r.text[:100]}')
            s = BeautifulSoup(page_html, features="html.parser")
            return s

        else:  # if not successful (e.g. due to bot protection), log as an attempt
            attempt = attempt + 1
            logging.info(f"Exception. Starting attempt #{attempt} ")

    logging.info(f"Exception. All attempts exhausted for this page. Skipping to next page")

    return None


def get_cars(make="BMW", model="5 SERIES", postcode="SW1A 0AA", radius=1500, min_year=1995, max_year=1995,
             include_writeoff="include", max_attempts_per_page=5, verbose=False):
    if verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    logging.basicConfig(format='%(levelname)s:%(message)s', level=log_level)

    # To bypass Cloudflare protection
    scraper = cloudscraper.create_scraper()

    # Basic variables

    results = []
    n_this_year_results = 0

    url_default = "https://www.autotrader.co.uk/car-search"

    # Set up parameters for query to autotrader.co.uk

    search_params = {"sort": "relevance",
                     "postcode": postcode,
                     "radius": radius,
                     "make": make,
                     "model": model,
                     "search-results-price-type": "total-price",
                     "search-results-year": "select-year",
                     }

    if include_writeoff == "include":
        search_params["writeoff-categories"] = "on"
    elif include_writeoff == "exclude":
        search_params["exclude-writeoff-categories"] = "on"
    elif include_writeoff == "writeoff-only":
        search_params["only-writeoff-categories"] = "on"

    year = min_year
    page = 1

    try:
        while year <= max_year:

            search_params["year-from"] = year
            search_params["year-to"] = year
            logging.info(f"Year:     {year}\nPage:     {page}")

            url = url_default
            params = search_params

            try:
                while url:
                    s = get_page_html(url, scraper, params=params, max_attempts_per_page=max_attempts_per_page)
                    if s:
                        articles = s.find_all("article", attrs={"data-standout-type": ""})
                        next_page_object = s.find(attrs={"class": "pagination--right__active"})
                    else:
                        articles = []
                        next_page_object = None

                    for article in articles:
                        car = get_car_details(article)
                        results.append(car)
                        n_this_year_results = n_this_year_results + 1

                    if next_page_object:
                        page = page + 1
                        url = next_page_object['href']
                        params = {}
                        logging.info(f"Car count: {len(results)}")
                        logging.info("---------------------------------")
                    else:
                        url = None
                        logging.info(f"Found total {n_this_year_results} results for year {year} across {page} pages")

            except KeyboardInterrupt:
                break

            # Increment year and reset relevant variables
            year = year + 1
            page = 1
            n_this_year_results = 0

            if year <= max_year:
                logging.info(f"Moving on to year {year}")
                logging.info("---------------------------------")

    except KeyboardInterrupt:
        pass

    return results


### Output functions ###

def save_csv(results=None, filename="scraper_output.csv"):
    csv_columns = ["name", "link", "price", "mileage", "BHP", "transmission", "fuel", "owners", "body", "ULEZ",
                   "engine", "year"]
    if results:
        with open(filename, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            for data in results:
                writer.writerow(data)


def save_json(results=None, filename="scraper_output.json"):
    if results:
        with open(filename, 'w') as f:
            json.dump(results, f, sort_keys=True, indent=4, separators=(',', ': '))
