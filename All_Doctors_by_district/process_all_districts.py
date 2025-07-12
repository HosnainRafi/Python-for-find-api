import os
import json
import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

# Configuration
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}
MAX_THREADS = 5  # Number of concurrent requests
DELAY_SECONDS = 1  # Delay between requests
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Parent folder path

DISTRICTS = [
    "barisal"
]

def load_json_data(filename):
    """Load JSON data from file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {filename}")
        return None

def save_json_data(data, filename):
    """Save JSON data to file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def scrape_doctor_details(url):
    """Scrape detailed information from a doctor's profile page."""
    try:
        time.sleep(DELAY_SECONDS)
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        doctor_data = {
            "profile_url": url,
            "name": None,
            "photo": None,
            "qualification": None,
            "specialty": None,
            "designation": None,
            "workplace": None,
            "rating": None,
            "chambers": []
        }
        
        # Extract basic info
        header = soup.find('header', class_='entry-header')
        if header:
            # Photo
            photo = header.find('img')
            if photo:
                doctor_data["photo"] = photo.get('src')
            
            # Name
            name = header.find('h1', class_='entry-title')
            if name:
                doctor_data["name"] = name.get_text(strip=True)
            
            # Details from info list
            info_items = header.select('div.info ul li')
            if info_items:
                if len(info_items) > 0:
                    doctor_data["qualification"] = info_items[0].get_text(strip=True)
                if len(info_items) > 1:
                    doctor_data["specialty"] = info_items[1].get_text(strip=True)
                if len(info_items) > 2:
                    doctor_data["designation"] = info_items[2].get_text(strip=True)
                if len(info_items) > 3:
                    doctor_data["workplace"] = info_items[3].get_text(strip=True)
            
            # Rating
            rating_div = header.find('div', class_='ssr-rating')
            if rating_div:
                doctor_data["rating"] = rating_div.get_text(strip=True)

        # Extract chamber information
        entry_content = soup.find('div', class_='entry-content')
        if entry_content:
            chambers = []
            h2_tags = entry_content.find_all('h2')
            
            for h2 in h2_tags:
                if 'chamber' in h2.get_text().lower() or 'appointment' in h2.get_text().lower():
                    next_p = h2.find_next('p')
                    if next_p:
                        chamber_info = next_p.get_text('\n', strip=True).split('\n')
                        chamber = {}
                        
                        for line in chamber_info:
                            if 'address' in line.lower():
                                chamber["address"] = line.split(':', 1)[-1].strip()
                            elif 'hour' in line.lower():
                                chamber["visiting_hour"] = line.split(':', 1)[-1].strip() if ':' in line else line.strip()
                            elif 'appointment' in line.lower():
                                chamber["appointment"] = line.split(':', 1)[-1].strip()
                            else:
                                chamber["name"] = line.strip()
                        
                        chamber_link = next_p.find('a')
                        if chamber_link:
                            chamber["url"] = chamber_link.get('href')
                        
                        chambers.append(chamber)
            
            doctor_data["chambers"] = chambers

        return doctor_data

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def process_district(district):
    """Process all doctors for a single district."""
    input_dir = os.path.join(BASE_DIR, district)
    input_json = os.path.join(input_dir, f"hospitals-{district}.json")
    output_dir = os.path.join(BASE_DIR, "Doctor_Details")
    output_json = os.path.join(output_dir, f"doctors-details-{district}.json")
    
    if not os.path.exists(input_json):
        print(f"Skipping {district} - input file not found")
        return
    
    district_data = load_json_data(input_json)
    if not district_data:
        return
    
    all_doctors = []
    
    # Collect all doctors with chamber links
    for hospital in district_data.get("hospitals", []):
        for doctor in hospital.get("doctors", []):
            if doctor.get("chamber_link"):
                all_doctors.append({
                    "name": doctor["name"],
                    "chamber_link": doctor["chamber_link"],
                    "hospital_name": hospital["name"],
                    "hospital_link": hospital.get("link", "")
                })
    
    total_doctors = len(all_doctors)
    print(f"Processing {total_doctors} doctors in {district}")
    
    # Process doctor details concurrently
    processed_doctors = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_doctor = {
            executor.submit(scrape_doctor_details, doctor["chamber_link"]): doctor
            for doctor in all_doctors
        }
        
        for future in as_completed(future_to_doctor):
            doctor = future_to_doctor[future]
            details = future.result()
            if details:
                merged = {
                    **doctor,
                    **details,
                    "source_hospital": doctor["hospital_name"],
                    "source_hospital_link": doctor["hospital_link"]
                }
                processed_doctors.append(merged)
                print(f"Processed {doctor['name']}")
    
    # Save results
    result = {
        "district": district,
        "total_doctors_processed": len(processed_doctors),
        "doctors": processed_doctors
    }
    
    save_json_data(result, output_json)
    print(f"Saved {len(processed_doctors)} doctor details for {district}")

def main():
    """Process all districts."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(BASE_DIR, "Doctor_Details")
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each district
    for district in DISTRICTS:
        print(f"\nStarting processing for {district}")
        process_district(district)

if __name__ == "__main__":
    main()
    print("\nAll districts processed successfully!")