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
           "price": article.find("div", {"class": "product-card-pricing__price"}).text.strip()}

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


def get_cars(make="BMW", model="5 SERIES", postcode="SW1A 0AA", radius=1500, min_year=1995, max_year=1995,
             include_writeoff="include", max_attempts_per_page=5, verbose=False):

    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(format='%(levelname)s:%(message)s', level=log_level)

    # To bypass Cloudflare protection
    scraper = cloudscraper.create_scraper()

    # Basic variables

    results = []
    n_this_year_results = 0

    url = "https://www.autotrader.co.uk/results-car-search"

    # Set up parameters for query to autotrader.co.uk

    params = {"sort": "relevance",
              "postcode": postcode,
              "radius": radius,
              "make": make,
              "model": model,
              "search-results-price-type": "total-price",
              "search-results-year": "select-year",
              }

    if include_writeoff == "include":
        params["writeoff-categories"] = "on"
    elif include_writeoff == "exclude":
        params["exclude-writeoff-categories"] = "on"
    elif include_writeoff == "writeoff-only":
        params["only-writeoff-categories"] = "on"

    year = min_year
    page = 1
    attempt = 1

    try:
        while year <= max_year:

            params["year-from"] = year
            params["year-to"] = year
            params["page"] = page

            try:
                r = scraper.get(url, params=params)
                logging.debug(f"Year:     {year}\nPage:     {page}\nResponse: {r}")

                if r.status_code != 200:  # if not successful (e.g. due to bot protection), log as an attempt
                    attempt = attempt + 1
                    if attempt <= max_attempts_per_page:
                        logging.debug(f"Exception. Starting attempt #{attempt} and keeping at page #{page}")

                    else:
                        page = page + 1
                        attempt = 1
                        logging.debug(f"Exception. All attempts exhausted for this page. Skipping to next page #{page}")

                else:

                    j = r.json()
                    s = BeautifulSoup(j["html"], features="html.parser")

                    articles = s.find_all("article", attrs={"data-standout-type": ""})

                    # if no results or reached end of results...
                    if len(articles) == 0 or r.url[r.url.find("page=") + 5:] != str(page):
                        logging.debug(
                                f"Found total {n_this_year_results} results for year {year} across {page - 1} pages")

                        # Increment year and reset relevant variables
                        year = year + 1
                        page = 1
                        attempt = 1
                        n_this_year_results = 0

                        if year <= max_year:
                            logging.debug(f"Moving on to year {year}")
                            logging.debug("---------------------------------")

                    else:
                        for article in articles:
                            car = get_car_details(article)
                            results.append(car)
                            n_this_year_results = n_this_year_results + 1

                        page = page + 1
                        attempt = 1

                        logging.debug(f"Car count: {len(results)}")
                        logging.debug("---------------------------------")

            except KeyboardInterrupt:
                break

            else:
                traceback.print_exc()
                attempt = attempt + 1
                if attempt <= max_attempts_per_page:
                    logging.debug(f"Exception. Starting attempt #{attempt} and keeping at page #{page}")

                else:
                    page = page + 1
                    attempt = 1
                    logging.debug(f"Exception. All attempts exhausted for this page. Skipping to next page #{page}")

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
