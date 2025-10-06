import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def scrape_carfax_cars(url, num_pages=3):
    all_cars = []

    headers = {
        "sec-ch-ua-platform": '"Windows"',
        "Referer": "https://www.carfax.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
        "DNT": "1",
        "sec-ch-ua-mobile": "?0",
    }

    for page in range(num_pages):
        if page == 0:
            page_url = url
        else:
            page_url = f"{url}?page={page + 1}"

        print(f"Scraping: {page_url}")
        response = requests.get(page_url, headers=headers)
        print(f"Status: {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")

        listings = soup.find_all("div", class_="srp-grid-list-item")
        print(f"Found {len(listings)} listings")

        if len(listings) == 0:
            print("First 500 chars of HTML:")
            print(response.text[:500])

        for listing in listings:
            title_elem = listing.find("h4", class_="srp-list-item-basic-info-model")
            title = title_elem.text.strip() if title_elem else None

            price_elem = listing.find("div", class_="srp-list-item__price")
            price_text = price_elem.text.strip() if price_elem else None

            mileage_elem = listing.find(
                "span", class_="srp-grid-list-item__mileage-address"
            )
            mileage_location = mileage_elem.text.strip() if mileage_elem else None

            year = None
            if title:
                year_match = re.search(r"\b(19|20)\d{2}\b", title)
                if year_match:
                    year = int(year_match.group())

            price = None
            if price_text:
                price_match = re.search(r"([\d,]+)", price_text)
                if price_match:
                    price = int(price_match.group(1).replace(",", ""))

            mileage = None
            if mileage_location:
                mileage_match = re.search(r"([\d,]+)", mileage_location)
                if mileage_match:
                    mileage = int(mileage_match.group(1).replace(",", ""))

            if price and year:
                all_cars.append(
                    {"title": title, "price": price, "year": year, "mileage": mileage}
                )

        print(f"Total collected: {len(all_cars)}\n")

    return pd.DataFrame(all_cars)


df = scrape_carfax_cars(
    "https://www.carfax.com/Used-Cars-in-Boston-MA_c4931", num_pages=1
)

print(f"\nScraped {len(df)} cars")
if len(df) > 0:
    print(df.head())
    df.to_csv("carfax_cars.csv", index=False)
