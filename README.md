# Autotrader Scraper
Scrape AutoTrader.co.uk by specifying search criteria, with results returned as a dictionary.


## Installation
   
Python 3:

    $ pip3 install autotrader-scraper

To update from an older version, the best way is to run `pip3 uninstall autotrader-scraper` before running the above command.

(Note: Python 2 is no longer supported as this package now uses **cloudscraper** to bypass CloudFlare protection, which in turn doesn't support Python 2)

## Usage

**Step 1:** Import the package

    >>> from autotrader_scraper import get_cars, save_csv, save_json

**Step 2:** Call `get_cars()` with your [criteria _(full list below)_](#criteria) and store the returned dictionary

    >>> results = get_cars(
            make = "Audi",
            model = "A5",
            postcode = "SW1A 0AA",
            radius = 1500,
            min_year = 2005,
            max_year = 2020,
            include_writeoff = "include",
            max_attempts_per_page = 5,
            verbose = False
        )

**Step 3:** Call `save_csv()` or `save_json()` with your results dictionary to output as a csv or json

    >>> save_csv(results)
    >>> save_json(results)
    
(You can chain these functions together to do everything in one line)

    >>> save_csv(get_cars(make = "Audi", model = "A5", ...))
    
## Criteria

| Criteria / Argument | Type | Description | Values | Default Value |
|-|-|-|-|-|
| make | String | Make of the car | Get these from autotrader.co.uk\*. Examples are "Audi", "BMW", "Jaguar" |"BMW"|
| model | String | Model of the car | Get these from autotrader.co.uk\*. Examples are "A3", "A4", "A4" for Audi |"5 SERIES"|
| postcode | String | Postcode where you are searching | Example: "CB2 1TN", "NW1 2BH" | "SW1A 0AA" |
| radius | Integer | Radius of your search from the postcode | Can be any positive integer. Use 1500 for nation-wide search | 1500 (i.e. nation-wide) |
| min_year | Integer | Minimum year of the car's manufacture | Can be any positive integer | 1995 |
| max_year | Integer | Maximum year of the car's manufacture | Can be any positive integer | 1995 |
| include_writeoff | String | Whether or not to include insurance write-off categories (i.e. Cat S/C/D/N) | "include", "exclude", "writeoff-only" | "include" |
| max_attempts_per_page | Integer | Maximum times to attempt scraping a page. A request may fail due to connectivity issues, server response issues, etc. and so in the event of a failure, the request will be retried a number of times specified by this argument | Can be any positive integer | 5 |
| verbose | Boolean | Whether or not to print progress on the console. Good for debugging | True, False | False |

\* When doing a search on the autotrader.co.uk website, look at the URL of the search results page to get an idea of what string to pass in here. Ignore URL encoding characters such as "%20" (replacement for a space) and type it how you normally would e.g. use `"SERIES 5"` rather than `"SERIES%205"`


## Contributing

Contributions are welcome!  For bug reports or requests please [submit an issue](https://github.com/suhailidrees/autotrader_scraper/issues).

## Donations

If you feel like showing your love and/or appreciation for this project, you can do so below:

<a href="https://buymeacoff.ee/suhailidrees" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

## Contact info

Feel free to contact me to discuss any issues, questions, or comments.

* Email: [idrees.suhail@gmail.com](mailto:idrees.suhail@gmail.com)
* LinkedIn: [Suhail Idrees](https://www.linkedin.com/in/suhail-idrees-926657a8/)
* Website: [suhailidrees.com](https://suhailidrees.com/?gh)
