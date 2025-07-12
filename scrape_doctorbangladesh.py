import requests
from bs4 import BeautifulSoup
import json
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

def scrape_hospitals(url):
    hospitals = []
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        hospital_list = soup.select('ul.list li a')
        
        if not hospital_list:
            print(f"⚠ No hospital listings found at {url}")
            return hospitals
        
        for item in hospital_list:
            hospitals.append({
                "name": item.text.strip(),
                "link": item['href']
            })
            
        print(f"Found {len(hospitals)} hospitals")
        return hospitals
    
    except Exception as e:
        print(f"🚨 Failed to scrape {url}: {str(e)}")
        return []

def scrape_all_hospitals():
    cities = [
        ("chittagong", "https://www.doctorbangladesh.com/hospitals-chittagong/"),
        ("sylhet", "https://www.doctorbangladesh.com/hospitals-sylhet/"),
        ("rajshahi", "https://www.doctorbangladesh.com/hospitals-rajshahi/"),
        ("rangpur", "https://www.doctorbangladesh.com/hospitals-rangpur/"),
        ("khulna", "https://www.doctorbangladesh.com/hospitals-khulna/"),
        ("barisal", "https://www.doctorbangladesh.com/hospitals-barisal/"),
        ("narayanganj", "https://www.doctorbangladesh.com/hospitals-narayanganj/"),
        ("mymensingh", "https://www.doctorbangladesh.com/hospitals-mymensingh/"),
        ("cumilla", "https://www.doctorbangladesh.com/hospitals-cumilla/"),
        ("bogura", "https://www.doctorbangladesh.com/hospitals-bogura/"),
        ("pabna", "https://www.doctorbangladesh.com/hospitals-pabna/"),
        ("kushtia", "https://www.doctorbangladesh.com/hospitals-kushtia/")
    ]

    for city, url in cities:
        print(f"\n=== SCRAPING {city.upper()} HOSPITALS ===")
        hospitals = scrape_hospitals(url)
        
        if hospitals:
            filename = f"hospitals-{city}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(hospitals, f, ensure_ascii=False, indent=2)
            print(f"✅ Saved {len(hospitals)} hospitals to {filename}")
        else:
            print(f"⚠ No data saved for {city}")
        
        time.sleep(2)  # Be polite with requests

if __name__ == "__main__":
    scrape_all_hospitals()
    print("\nAll hospital scraping complete!")