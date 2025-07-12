import os
import requests
from bs4 import BeautifulSoup
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9'
}
MAX_THREADS = 5  # Number of concurrent requests
DELAY_SECONDS = 1  # Delay between requests to avoid getting blocked

# Load hospital data
DISTRICTS = {
    "Khulna": [
        {"specialty": "Anesthesiology (Pain) Specialist in Khulna", "url": "https://www.doctorbangladesh.com/anesthesiologist-khulna/"},
        {"specialty": "Cancer Specialist in Khulna", "url": "https://www.doctorbangladesh.com/oncologist-khulna/"},
        {"specialty": "Cardiac Surgery Specialist in Khulna", "url": "https://www.doctorbangladesh.com/cardiac-surgeon-khulna/"},
        {"specialty": "Cardiology Specialist in Khulna", "url": "https://www.doctorbangladesh.com/cardiologist-khulna/"},
        {"specialty": "Chest & Asthma Specialist in Khulna", "url": "https://www.doctorbangladesh.com/chest-specialist-khulna/"},
        {"specialty": "Child Specialist in Khulna", "url": "https://www.doctorbangladesh.com/pediatrician-khulna/"},
        {"specialty": "Colorectal Surgery Specialist in Khulna", "url": "https://www.doctorbangladesh.com/colorectal-surgeon-khulna/"},
        {"specialty": "Dental Specialist in Khulna", "url": "https://www.doctorbangladesh.com/dentist-khulna/"},
        {"specialty": "Diabetes & Hormone Specialist in Khulna", "url": "https://www.doctorbangladesh.com/endocrinologist-khulna/"},
        {"specialty": "ENT Specialist in Khulna", "url": "https://www.doctorbangladesh.com/otolaryngologist-khulna/"},
        {"specialty": "Eye Specialist in Khulna", "url": "https://www.doctorbangladesh.com/ophthalmologist-khulna/"},
        {"specialty": "Gastroenterology Specialist in Khulna", "url": "https://www.doctorbangladesh.com/gastroenterologist-khulna/"},
        {"specialty": "General & Laparoscopic Surgery Specialist in Khulna", "url": "https://www.doctorbangladesh.com/general-surgeon-khulna/"},
        {"specialty": "Gynecology & Obstetrics Specialist in Khulna", "url": "https://www.doctorbangladesh.com/gynecologist-khulna/"},
        {"specialty": "Hematology (Blood) Specialist in Khulna", "url": "https://www.doctorbangladesh.com/hematologist-khulna/"},
        {"specialty": "Hepatobiliary Surgeon in Khulna", "url": "https://www.doctorbangladesh.com/hepatobiliary-surgeon -khulna/"},
        {"specialty": "Infertility Specialist in Khulna", "url": "https://www.doctorbangladesh.com/infertility-specialist-khulna/"},
        {"specialty": "Kidney Specialist in Khulna", "url": "https://www.doctorbangladesh.com/nephrologist-khulna/"},
        {"specialty": "Liver Specialist in Khulna", "url": "https://www.doctorbangladesh.com/hepatologist-khulna/"},
        {"specialty": "Medicine Specialist in Khulna", "url": "https://www.doctorbangladesh.com/medicine-specialist-khulna/"},
        {"specialty": "Neurology/Neuromedicine Specialist in Khulna", "url": "https://www.doctorbangladesh.com/neurologist-khulna/"},
        {"specialty": "Neurosurgery Specialist in Khulna", "url": "https://www.doctorbangladesh.com/neurosurgeon-khulna/"},
        {"specialty": "Orthopedic Specialist in Khulna", "url": "https://www.doctorbangladesh.com/orthopedic-specialist-khulna/"},
        {"specialty": "Pediatric Surgery Specialist in Khulna", "url": "https://www.doctorbangladesh.com/pediatric-surgeon-khulna/"},
        {"specialty": "Physical Medicine Specialist in Khulna", "url": "https://www.doctorbangladesh.com/physical-medicine-specialist-khulna/"},
        {"specialty": "Plastic Surgery Specialist in Khulna", "url": "https://www.doctorbangladesh.com/plastic-surgeon-khulna/"},
        {"specialty": "Psychiatry (Mental) Specialist in Khulna", "url": "https://www.doctorbangladesh.com/psychiatrist-khulna/"},
        {"specialty": "Psychologist in Khulna", "url": "https://www.doctorbangladesh.com/psychologist-khulna/"},
        {"specialty": "Rheumatology Specialist in Khulna", "url": "https://www.doctorbangladesh.com/rheumatologist-khulna/"},
        {"specialty": "Sex Specialist in Khulna", "url": "https://www.doctorbangladesh.com/sexologist -khulna/"},
        {"specialty": "Skin Specialist in Khulna", "url ": "https://www.doctorbangladesh.com/dermatologist-khulna/"},
        {"specialty": "Urology Specialist in Khulna", "url": "https://www.doctorbangladesh.com/urologist-khulna/"},
        {"specialty": "Vascular Surgery Specialist in Khulna", "url": "https://www.doctorbangladesh.com/vascular-surgeon-khulna/"}
    ],
    "Kustia": [
        {"name": "Amin Diagnostic & Medical Services, Kushtia", "url": "https://www.doctorbangladesh.com/amin-kushtia-doctor-list-contact/"},
        {"name": "Popular Diagnostic Centre, Kushtia", "url": "https://www.doctorbangladesh.com/popular-kushtia-doctor-list-contact/"
        },
        {
            "name": "Sono Hospital (Sono Tower 1 & 2), Kushtia", "url": "https://www.doctorbangladesh.com/sono-kushtia-doctor-list-contact/"
        }
    ],
    "Mymensingh": [
        {"name": "Delta Health Care, Mymensingh", "url": "https://www.doctorbangladesh.com/delta-mymensingh-doctor-list-contact/"},
        {"name": "Icon Diagnostic Center, Mymensingh", "url": "https://www.doctorbangladesh.com/icon-mymensingh-doctor-list-contact/"},
        {"name": "Labaid Diagnostic, Mymensingh", "url": "https://www.doctorbangladesh.com/labaid-mymensingh-doctor-list-contact/"},
        {"name": "Mymensingh Medical College & Hospital", "url": "https://www.doctorbangladesh.com/mmch-doctor -list-contact/"},
        {"name": "Nexus Hospital, Mymensingh", "url": "https://www.doctorbangladesh.com/nexus-hospital-mymensingh-doctor-list-contact/"},
        {"name": "Popular Diagnostic Center, Mymensingh", "url": "https://www.doctorbangladesh.com/popular-mymensingh-doctor-list-contact/"},
        {"name": "Pranto Specialized Hospital, Mymensingh", "url": "https://www.doctorbangladesh.com/pranto-mymensingh-doctor-list-contact/"},
        {"name": "Sayem Diagno Complex & Hospital, Mymensingh", "url": "https://www.doctorbangladesh.com/sayem-hospital-mymensingh-doctor-list-contact/"},
        {"name": "Serum Lab & Hospital, Mymensingh", "url": "https://www.doctorbangladesh.com/serum-lab-mymensingh-doctor-list-contact/"},
        {"name": "Sodesh Hospital, Mymensingh", "url": "https://www.doctorbangladesh.com/sodesh-hospital-mymensingh-doctor-list-contact/"},
        {"name": "TMC Hospital & Diagnostic, Mymensingh", "url": "https://www.doctorbangladesh.com/tmc-mymensingh-doctor-list-contact/"},
        {"name": "Union Specialized Hospital, Mymensingh", "url": "https://www.doctorbangladesh.com/union-hospital-mymensingh-doctor-list-contact/"}
    ],
    "Narayanganj": [
        {"name": "Medinova Medical Services, Narayanganj", "url": "https://www.doctorbangladesh.com/medinova-narayanganj-doctor-list-contact/"},
        {"name": "Modern Diagnostic Center, Narayanganj", "url": "https://www.doctorbangladesh.com/modern-diagnostic-narayanganj-doctor-list-contact/"},
        {"name": "Popular Diagnostic Center, Narayanganj", "url": "https://www.doctorbangladesh.com/popular-narayanganj-doctor-list-contact/"}
    ],
    "Pabna": [
        {"name": "Shafique Hospital & Diagnostic, Pabna", "url": "https://www.doctorbangladesh.com/shafique-hospital-pabna-doctor-list-contact/"},
        {"name": "Akota Diagnostic Center, Pabna", "url": "https://www.doctorbangladesh.com/akota-diagnostic-center-pabna-doctor-list-contact/"},
        {"name": "Assort Specialised Hospital, Pabna", "url": "https://www.doctorbangladesh.com/assort-hospital-pabna-doctor-list-contact/"},
        {"name": "Central Hospital, Pabna", "url": "https://www.doctorbangladesh.com/central-hospital-pabna-doctor-list-contact/"},
        {"name": "City Diagnostic Center, Pabna", "url": "https://www.doctorbangladesh.com/city-diagnostic-center-pabna-doctor-list-contact/"},
        {"name": "Digital Diagnostic Center, Pabna", "url": "https://www.doctorbangladesh.com/digital-diagnostic-pabna-doctor-list-contact/"},
        {"name": "Dr. Gaffar Diagnostic Complex, Pabna", "url": "https://www.doctorbangladesh.com/gaffar-diagnostic-complex-pabna-doctor-list-contact/"},
        {"name": "Euro Medical Center, Pabna", "url": "https://www.doctorbangladesh.com/euro-medical-center-pabna-doctor-list-contact/"},
        {"name": "Fair Hospital & Diagnostic Center, Pabna", "url": "https://www.doctorbangladesh.com/fair-hospital-pabna-doctor-list-contact/"},
        {"name": "Fast Care Medical Center, Pabna", "url": "https://www.doctorbangladesh.com/fast-care-pabna-doctor-list-contact/"},
        {"name": "250 Bedded General Hospital, Pabna", "url": "https://www.doctorbangladesh.com/pabna-general-hospital-doctor-list-contact/"},
        {"name": "Grameen Diagnostic Center, Pabna", "url": "https://www.doctorbangladesh.com/grameen-diagnostic-pabna-doctor-list-contact/"},
        {"name": "Halima Clinic, Pabna", "url": "https://www.doctorbangladesh.com/halima-clinic-pabna-doctor-list-contact/"},
        {"name": "Jalal Memorial Hospital, Pabna", "url": "https://www.doctorbangladesh.com/jalal-memorial-hospital-pabna-doctor-list-contact/"},
        {"name": "Kimia Diagnostic Center, Pabna", "url": "https://www.doctorbangladesh.com/kimia-diagnostic-center -pabna-doctor-list-contact/"},
        {"name": "Labaid Diagnostic, Pabna", "url": "https://www.doctorbangladesh.com/labaid-diagnostic-pabna-doctor -list-contact/"},
        {"name": "Medicare Diagnostic Center, Pabna", "url": "https://www.doctorbangladesh.com/medicare-diagnostic-center-pabna-doctor-list-contact/"},
        {"name": "Model Hospital & Diagnostic Center, Pabna", "url": "https://www.doctorbangladesh.com/model-hospital-pabna-doctor-list-contact/"},
        {"name": "Pabna Eye Hospital & Phaco Center", "url": "https://www.doctorbangladesh.com/pabna-eye-hospital-doctor-list-contact/"},
        {"name": "Pabna Medical College & Hospital", "url": "https://www.doctorbangladesh.com/pabna-medical-college-hospital-doctor-list-contact/"},
        {"name": "Popular Hospital, Kashinathpur", "url": "https://www.doctorbangladesh.com/popular-kashinathpur-doctor-list/"},
        {"name": "Mental Hospital, Pabna", "url": "https://www.doctorbangladesh.com/pabna-mental-hospital-doctor-list-contact/"},
        {"name": "PDC Specialized Hospital, Pabna", "url": "https://www.doctorbangladesh.com/pdc-hospital-pabna-doctor-list-contact/"},
        {"name": "Shimla Hospital, Pabna", "url": "https://www.doctorbangladesh.com/simla-hospital-pabna-doctor-list-contact/"},
        {"name": "Sunrise Clinic & Diagnostic Center, Pabna", "url": "https://www.doctorbangladesh.com/sunrise-diagnostic-center-pabna-doctor-list-contact/"},
        {"name": "Unique Diagnostic Complex, Pabna", "url": "https://www.doctorbangladesh.com/unique-diagnostic-complex-pabna-doctor-list-contact/"},
        {"name": "ZamZam Medical & Diagnostic Center, Pabna", "url": "https://www.doctorbangladesh.com/zamzam-diagnostic-pabna-doctor-list-contact/"}
    ],
    "Rajshahi": [
        {"name": "Al Arafa Clinic & Diagnostic Center, Rajshahi", "url": "https://www.doctorbangladesh.com/al-arafa-clinic-rajshahi-doctor-list-contact/"},
        {"name": "Biopath Diagnostic Center, Rajshahi", "url": "https://www.doctorbangladesh.com/biopath-rajshahi-doctor-list-contact/"},
        {"name": "Hepta Health Care, Rajshahi", "url": "https://www.doctorbangladesh.com/hepta-health-care-rajshahi-doctor-list-contact/"},
        {"name": "Islami Bank Hospital, Rajshahi", "url": "https://www.doctorbangladesh.com/islami -bank-hospital-rajshahi-doctor-list-contact/"},
        {"name": "Labaid Diagnostic, Rajshahi", "url": "https://www.doctorbangladesh.com/labaid-diagnostic-rajshahi-doctor-list-contact/"},
        {"name": "Life Line Diagnostic Center, Rajshahi", "url": "https://www.doctorbangladesh.com/life-line-diagnostic-rajshahi-doctor-list-contact/"},
        {"name": "Medipath Diagnostic Complex, Rajshahi", "url": "https://www.doctorbangladesh.com/medipath-diagnostic-rajshahi-doctor-list-contact/"},
        {"name": "Metro Diagnostic Center, Rajshahi", "url": "https://www.doctorbangladesh.com/metro-diagnostic-center-rajshahi-doctor-list-contact/"},
        {"name": "Micropath Diagnostic Center, Rajshahi", "url": "https://www.doctorbangladesh.com/micropath-diagnostic-center-rajshahi-doctor-list-contact/"},
        {"name": "Motherland Infertility Center & Hospital, Rajshahi", "url": "https://www.doctorbangladesh.com/motherland-infertility-rajshahi-doctor-list-contact/"},
        {"name": "North Bengal Diagnostic Center, Rajshahi", "url": "https://www.doctorbangladesh.com/north-bengal-diagnostic-rajshahi-doctor-list-contact/"},
        {"name": "Popular Diagnostic Center, Rajshahi", "url": "https://www.doctorbangladesh.com/popular-rajshahi-doctor-list-contact/"},
        {"name": "Rajshahi Central Hospital & Diagnostic Center", "url": "https://www.doctorbangladesh.com/rajshahi-central-hospital-doctor-list-contact/"},
        {"name": "Rajshahi Medical College & Hospital", "url": "https://www.doctorbangladesh.com/rmch-doctor-list-contact/"},
        {"name": "Rajshahi Metropolitan Hospital & Diagnostic Center", "url": "https://www.doctorbangladesh.com/rajshahi-metropolitan-hospital-doctor-list-contact/"},
        {"name": "Rajshahi Model Hospital", "url": "https://www.doctorbangladesh.com/rajshahi-model-hospital-doctor-list-contact/"},
        {"name": "Re-Life Hospital & Diagnostic, Rajshahi", "url": "https://www.doctorbangladesh.com/re-life-hospital-rajshahi/doctor-list-contact/"},
        {"name": "Rajshahi Royal Hospital Pvt. Ltd.", "url": "https://www.doctorbangladesh.com/royal-hospital-rajshahi-doctor-list-contact/"},
        {"name": "Shapla Diagnostic Complex, Rajshahi", "url": "https://www.doctorbangladesh.com/shapla-diagnostic-rajshahi-doctor-list-contact/"},
        {"name": "Zamzam Islami Hospital, Rajshahi", "url": "https://www.doctorbangladesh.com/zamzam-islami-hospital-rajshahi-doctor-list-contact/"}
    ],
    "Rangpur": [
        {"name": "Apollo Diagnostic Center, Rangpur", "url": "https://www.doctorbangladesh.com/apollo-diagnostic-center-rangpur-doctor-list-contact/"},
        {"name": "Doctor's Community Hospital, Rangpur", "url": "https://www.doctorbangladesh.com/doctors-clinic-rangpur-doctor-list-contact/"},
        {"name": "Elegant Dentistry, Rangpur", "url": "https://www.doctorbangladesh.com/elegant-dentistry-rangpur-doctor-list/"},
        {"name": "Good Health Hospital, Rangpur", "url": "https://www.doctorbangladesh.com/good-health-rangpur-doctor-list-contact/"},
        {"name": "Hypertension & Research Center", "url": "https://www.doctorbangladesh.com/htncr-doctor-list-contact/"},
        {"name": "Islami Bank Community Hospital, Rangpur", "url": "https://www.doctorbangladesh.com/islami-bank-community-hospital-rangpur-doctor-list-contact/"},
        {"name": "Labaid Diagnostic, Rangpur", "url": "https://www.doctorbangladesh.com/labaid-diagnostic-rangpur-doctor-list-contact/"},
        {"name": "Popular Diagnostic Center, Rangpur", "url": "https://www.doctorbangladesh.com/popular-rangpur-doctor-list-contact/"},
        {"name": "Prime Medical College Hospital, Rangpur", "url": "https://www.doctorbangladesh.com/pmch-rangpur-doctor-list-contact/"},
        {"name": "Rangpur Community Medical College & Hospital", "url": "https://www.doctorbangladesh.com/rangpur-community-medical-college-doctor-list-contact/"},
        {"name": "Rangpur Medical College & Hospital", "url": "https://www.doctorbangladesh.com /rangpur-medical-college-hospital-doctor-list-contact/"},
        {"name": "Update Diagnostic, Rangpur", "url": "https://www.doctorbangladesh.com/update-diagnostic-rangpur-doctor-list-contact/"}
    ],
    "Sylhet": [
        {"name": "Al Haramain Hospital Pvt Ltd, Sylhet", "url": "https://www.doctorbangladesh.com/al-haramain-hospital-sylhet-doctor-list-contact/"},
        {"name": "Comfort Medical Services, Sylhet", "url": "https://www.doctorbangladesh.com/comfort-medical-sylhet-doctor-list-contact/"},
        {"name": "Ibn Sina Hospital Ltd, Sylhet", "url": "https://www.doctorbangladesh.com/ibn-sina-sylhet-doctor-list-contact/"},
        {"name": "Ibn Sina Diagnostic & Consultation Center, Rikabibazar", "url": "https://www.doctorbangladesh.com/ibn-sina-rikabibazar-doctor-list-contact/"},
        {"name": "Jalalabad Ragib Rabeya Medical College Hospital", "url": "https://www.doctorbangladesh.com/jrrmch-doctor-list-contact/"},
        {"name": "Kidney Foundation Hospital Sylhet", "url": "https://www.doctorbangladesh.com/kidney-foundation-hospital-sylhet-doctor-list/"},
        {"name": "Labaid Diagnostic Limited, Sylhet", "url": "https://www.doctorbangladesh.com/labaid-sylhet-doctor-list-contact/"},
        {"name": "Mount Adora Hospital, Akhalia, Sylhet", "url": "https://www.doctorbangladesh.com/mount-adora-akhalia-doctor-list-contact/"},
        {"name": "Mount Adora Hospital, Nayasarak, Sylhet", "url": "https://www.doctorbangladesh.com/mount-adora-nayasarak-doctor-list-contact/"},
        {"name": "Medinova Medical Services, Sylhet", "url": "https://www.doctorbangladesh.com/medinova-sylhet-doctor-list-contact/"},
        {"name": "Medi-Aid Diagnostic & Consultation Center", "url": "https://www.doctorbangladesh.com/medi-aid-sylhet-doctor-list-contact/"},
        {"name": "National Heart Foundation Hospital, Sylhet", "url": "https://www.doctorbangladesh.com/heart-foundation-sylhet-doctor-list/"},
        {"name": "Noorjahan Hospital, Sylhet", "url": "https://www.doctorbangladesh.com/noorjahan-hospital-sylhet-doctor-list-contact/"},
        {"name": "North East Medical College & Hospital", "url": "https://www.doctorbangladesh.com/nemch-doctor-list-contact/"},
        {"name": "Oasis Hotel, Sylhet", "url": "https://www.doctorbangladesh.com/oasis-hospital-sylhet-doctor-list-contact/"},
        {"name": "Parkview Medical College & Hospital, Sylhet", "url": "https://www.doctorbangladesh.com/parkview-hospital -sylhet-doctor-list-contact/"},
        {"name": "Popular Medical Center, Kajolshah, Sylhet", "url": "https://www.doctorbangladesh.com/popular-sylhet-doctor-list-contact/"},
        {"name": "Popular Medical Center & Hospital, Subhanighat, Sylhet", "url": "https://www.doctorbangladesh.com/popular-hospital-sylhet-doctor-list-contact/"},
        {"name": "Shahjalal Medical Services, Sylhet", "url": "https://www.doctorbangladesh.com/shahjalal-medical-sylhet-doctor-list/"},
        {"name": "Stadium Market, Sylhet", "url": "https://www.doctorbangladesh.com/stadium-market-sylhet-doctor-list-contact/"},
        {"name": "Sylhet MAG Osmani Medical College & Hospital", "url": "https://www.doctorbangladesh.com/somc-doctor-list-contact/"},
        {"name": "Sylhet Women's Medical College & Hospital", "url": "https://www.doctorbangladesh.com/swmc-doctor-list-contact/"},
        {"name": "Trust Medical Services, Sylhet", "url": "https://www.doctorbangladesh.com/trust-medical-sylhet-doctor-list-contact/"}
    ]
}


def create_directory_structure():
    """Create the output directory structure."""
    if not os.path.exists('Doctors by district'):
        os.makedirs('Doctors by district')
    for district in DISTRICTS.keys():
        district_dir = os.path.join('Doctors by district', district.lower())
        if not os.path.exists(district_dir):
            os.makedirs(district_dir)


def scrape_doctor_info(url):
    """Scrape doctor information from a single specialty page."""
    try:
        time.sleep(DELAY_SECONDS)
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        doctors = soup.select('ul.doctors li.doctor')
        hospital_doctors = []
        
        for doctor in doctors:
            try:
                name = doctor.select_one('h3.title a').get_text(strip=True)
                photo = doctor.select_one('.photo img')['src'] if doctor.select_one('.photo img') else None
                info_items = doctor.select('.info ul li')
                
                degree = info_items[0].get_text(strip=True) if len(info_items) > 0 else "N/A"
                specialty = info_items[1].get_text(strip=True) if len(info_items) > 1 else "N/A"
                workplace = info_items[2].get_text(strip=True) if len(info_items) > 2 else "N/A"
                chamber_link = doctor.select_one('h3.title a')['href'] if doctor.select_one('h3.title a') else None
                
                hospital_doctors.append({
                    "name": name,
                    "photo": photo,
                    "degree": degree,
                    "specialty": specialty,
                    "workplace": workplace,
                    "chamber_link": chamber_link
                })
            except Exception as e:
                print(f"Error parsing doctor from {url}: {str(e)}")
                continue
                
        return hospital_doctors

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {str(e)}")
        return None


def process_district(district_name, hospitals):
    """Process all specialties in a district."""
    print(f"\nProcessing district: {district_name}")
    district_data = {
        "district": district_name,
        "hospitals": [],
        "total_doctors": 0
    }

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_hospital = {
            executor.submit(scrape_doctor_info, hospital["url"]): hospital
            for hospital in hospitals if "url" in hospital
        }
        
        for future in as_completed(future_to_hospital):
            hospital = future_to_hospital[future]
            try:
                doctors = future.result()
                if doctors:
                    hospital_data = {
                        "name": hospital.get("specialty", hospital.get("name", "Unknown")),
                        "link": hospital["url"],
                        "doctors": doctors,
                        "count": len(doctors)
                    }
                    district_data["hospitals"].append(hospital_data)
                    district_data["total_doctors"] += len(doctors)
                    print(f"Processed {hospital.get('specialty', hospital.get('name', 'Unknown'))} - {len(doctors)} doctors")
            except Exception as e:
                print(f"Error processing {hospital.get('specialty', hospital.get('name', 'Unknown'))}: {str(e)}")

    filename = os.path.join(
        'Doctors by district',
        district_name.lower(),
        f'hospitals-{district_name.lower()}.json'
    )
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(district_data, f, ensure_ascii=False, indent=2)

    print(f"Saved data for {district_name} district with {district_data['total_doctors']} total doctors")


def main():
    create_directory_structure()
    for district_name, hospitals in DISTRICTS.items():
        process_district(district_name, hospitals)


if __name__ == "__main__":
    main()
    print("Processing district: Kustia")