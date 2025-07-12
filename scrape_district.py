import requests
from bs4 import BeautifulSoup
import json
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

city_urls = {
    "dhaka": "https://www.doctorbangladesh.com/doctors-dhaka/",
    "chittagong": "https://www.doctorbangladesh.com/doctors-chittagong/",
    "sylhet": "https://www.doctorbangladesh.com/doctors-sylhet/",
    "rajshahi": "https://www.doctorbangladesh.com/doctors-rajshahi/",
    "rangpur": "https://www.doctorbangladesh.com/doctors-rangpur/",
    "khulna": "https://www.doctorbangladesh.com/doctors-khulna/",
    "barisal": "https://www.doctorbangladesh.com/doctors-barisal/",
    "mymensingh": "https://www.doctorbangladesh.com/doctors-mymensingh/",
    "narayanganj": "https://www.doctorbangladesh.com/doctors-narayanganj/",
    "cumilla": "https://www.doctorbangladesh.com/doctors-cumilla/",
    "bogura": "https://www.doctorbangladesh.com/doctors-bogura/",
    "pabna": "https://www.doctorbangladesh.com/doctors-pabna/",
    "kushtia": "https://www.doctorbangladesh.com/doctors-kushtia/"
}

def scrape_city_specialties(url):
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Select all <li><a> in <ul class="list">
        links = soup.select('ul.list li a')
        result = []
        for a in links:
            specialty = a.text.strip()
            link = a['href']
            result.append({"specialty": specialty, "url": link})
        print(f"✔ Found {len(result)} categories")
        return result
    except Exception as e:
        print(f"🚨 Error: {e}")
        return []

if __name__ == "__main__":
    for city, url in city_urls.items():
        print(f"\n=== {city.upper()} ===")
        data = scrape_city_specialties(url)
        if data:
            with open(f"doctors_{city}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved to doctors_{city}.json")
        else:
            print("No data found.")
        time.sleep(1)
    print("\n✅ All city category scrapes complete!")