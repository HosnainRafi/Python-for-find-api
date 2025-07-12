import os
import requests
from bs4 import BeautifulSoup
import json

# URL to scrape
url = "https://www.doctorbangladesh.com/anesthesiologist-barisal/"

# Create folder structure
if not os.path.exists('Doctors by district'):
    os.makedirs('Doctors by district')

# Set headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/'
}

try:
    # Make the request with headers
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Check for HTTP errors
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all doctor entries
    doctors = soup.select('ul.doctors li.doctor')
    
    doctor_data = []
    
    for doctor in doctors:
        try:
            name = doctor.select_one('h3.title a').get_text(strip=True)
            photo = doctor.select_one('.photo img')['src'] if doctor.select_one('.photo img') else None
            degree = doctor.select_one('li:nth-of-type(1)').get_text(strip=True) if doctor.select_one('li:first-of-type') else "N/A"
            specialty = doctor.select_one('li.speciality').get_text(strip=True) if doctor.select_one('li.speciality') else "N/A"
            workplace = doctor.select_one('li:has(> small)').get_text(strip=True) if doctor.select_one('li:has(> small)') else "N/A"
            chamber_link = doctor.select_one('h3.title a')['href'] if doctor.select_one('h3.title a') else None
            
            doctor_data.append({
                "name": name,
                "photo": photo,
                "degree": degree,
                "specialty": specialty,
                "workplace": workplace,
                "chamber_link": chamber_link
            })
        except Exception as e:
            print(f"Error parsing doctor: {e}")
            continue
    
    # Save to JSON file
    district = "Barisal"
    filename = os.path.join('Doctors by district', f'{district.lower()}_anesthesiologists.json')
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "district": district,
            "specialty": "Anesthesiology",
            "doctors": doctor_data,
            "source_url": url
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully saved {len(doctor_data)} doctors to {filename}")
    
except requests.exceptions.HTTPError as http_err:
    if response.status_code == 403:
        print("403 Forbidden - The website is blocking our request. Try:")
        print("1. Using a different User-Agent header")
        print("2. Adding delays between requests")
        print("3. Using a rotating proxy")
    else:
        print(f"HTTP error occurred: {http_err}")
except requests.exceptions.RequestException as e:
    print(f"Error fetching the URL: {e}")
except Exception as e:
    print(f"An error occurred: {e}")