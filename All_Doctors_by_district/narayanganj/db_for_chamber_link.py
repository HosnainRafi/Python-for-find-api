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
DELAY_SECONDS = 1  # Delay between requests to avoid getting blocked

def load_json_data(filename):
    """Load JSON data from file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_data(data, filename):
    """Save JSON data to file."""
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
            current_chamber = {}
            
            # Look for chamber sections
            h2_tags = entry_content.find_all('h2')
            for h2 in h2_tags:
                if 'chamber' in h2.get_text().lower() or 'appointment' in h2.get_text().lower():
                    next_p = h2.find_next('p')
                    if next_p:
                        chamber_info = next_p.get_text('\n', strip=True).split('\n')
                        
                        # Extract key-value pairs
                        chamber = {}
                        for line in chamber_info:
                            if line.lower().startswith('visiting hour'):
                                chamber["visiting_hour"] = line.replace('Visiting Hour:', '').strip()
                            elif line.lower().startswith('appointment'):
                                chamber["appointment"] = line.replace('Appointment:', '').strip()
                            elif 'address' in line.lower():
                                chamber["address"] = line.split(':', 1)[-1].strip()
                            elif 'hour' in line.lower() and 'visiting' not in line.lower():
                                chamber["visiting_hour"] = line.strip()
                            else:
                                if not chamber.get("name"):
                                    chamber["name"] = line.strip()
                        
                        # Get chamber link if available
                        chamber_link = next_p.find('a')
                        if chamber_link:
                            chamber["url"] = chamber_link.get('href')
                        
                        chambers.append(chamber)
            
            doctor_data["chambers"] = chambers

        return doctor_data

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {str(e)}")
        return None
    except Exception as e:
        print(f"Error parsing doctor details from {url}: {str(e)}")
        return None

def process_doctors(input_file, output_dir):
    """Process all doctors from input file and save detailed info to output directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    district_data = load_json_data(input_file)
    district_name = district_data.get("district", "unknown").lower()
    output_file = os.path.join(output_dir, f'doctors-details-{district_name}.json')
    
    all_doctors = []
    
    # Collect all doctors with chamber links
    for hospital in district_data.get("hospitals", []):
        for doctor in hospital.get("doctors", []):
            if doctor.get("chamber_link"):
                all_doctors.append({
                    "name": doctor["name"],
                    "chamber_link": doctor["chamber_link"],
                    "hospital_name": hospital["name"],
                    "hospital_link": hospital["link"]
                })
    
    total_doctors = len(all_doctors)
    print(f"Found {total_doctors} doctors with chamber links in {district_name}")
    
    # Process doctor details concurrently
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_doctor = {
            executor.submit(scrape_doctor_details, doctor["chamber_link"]): doctor
            for doctor in all_doctors
        }
        
        processed_doctors = []
        for future in as_completed(future_to_doctor):
            doctor = future_to_doctor[future]
            try:
                details = future.result()
                if details:
                    # Merge basic info with scraped details
                    merged = {
                        **doctor,
                        **details,
                        "source_hospital": doctor["hospital_name"],
                        "source_hospital_link": doctor["hospital_link"]
                    }
                    processed_doctors.append(merged)
                    print(f"Processed {doctor['name']}")
            except Exception as e:
                print(f"Error processing {doctor['name']}: {str(e)}")
    
    # Save all doctor details
    result = {
        "district": district_name,
        "total_doctors_processed": len(processed_doctors),
        "doctors": processed_doctors
    }
    
    save_json_data(result, output_file)
    print(f"Saved detailed doctor data for {district_name} to {output_file}")

if __name__ == "__main__":
    # Example usage - modify these paths as needed
    input_json = "hospitals-narayanganj.json"
    output_directory = "Doctor Details"
    
    process_doctors(input_json, output_directory)