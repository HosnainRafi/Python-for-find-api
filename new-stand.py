import os
import json
from pathlib import Path

def clean_rating(rating_str):
    """Remove parentheses while keeping their contents"""
    if not rating_str:
        return None
    return rating_str.replace('(', '').replace(')', '')

def standardize_data_format():
    script_dir = Path(__file__).parent.resolve()
    input_dir = script_dir / "Doctor_Details"
    output_dir = script_dir / "Standardized_Doctor_Details"
    output_dir.mkdir(exist_ok=True)
    
    district_files = list(input_dir.glob("doctors-details-*.json"))
    
    all_doctors = []
    duplicates_removed = 0
    
    for file_path in district_files:
        try:
            district = file_path.stem.replace("doctors-details-", "")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                standardized_doctors = []
                seen_profiles = set()
                
                for doctor in data.get('doctors', []):
                    profile_url = doctor.get('profile_url') or doctor.get('chamber_link')
                    if not profile_url:
                        continue
                        
                    if profile_url in seen_profiles:
                        duplicates_removed += 1
                        continue
                    seen_profiles.add(profile_url)
                    
                    standardized = {
                        'district': district,
                        'name': doctor.get('name'),
                        'profile_url': profile_url,
                        'photo': doctor.get('photo'),
                        'qualification': doctor.get('qualification') or doctor.get('degree'),
                        'specialty': doctor.get('specialty'),
                        'designation': doctor.get('designation'),
                        'workplace': doctor.get('workplace'),
                        'rating': clean_rating(doctor.get('rating')),  # Apply the cleaning here
                        'chambers': doctor.get('chambers', []),
                        'source': {
                            'hospital': doctor.get('hospital_name') or doctor.get('source_hospital'),
                            'link': doctor.get('hospital_link') or doctor.get('source_hospital_link')
                        }
                    }
                    
                    standardized = {k: v for k, v in standardized.items() if v}
                    standardized_doctors.append(standardized)
                
                output_path = output_dir / f"standardized-{district}.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(standardized_doctors, f, ensure_ascii=False, indent=2)
                
                all_doctors.extend(standardized_doctors)
        
        except Exception as e:
            print(f"Error processing {file_path.name}: {str(e)}")
    
    if all_doctors:
        combined_path = output_dir / "all-doctors-combined.json"
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(all_doctors, f, ensure_ascii=False, indent=2)
        
        print(f"\nStandardization complete!")
        print(f"Total doctors: {len(all_doctors)}")
        print(f"Duplicates removed: {duplicates_removed}")
    else:
        print("\nNo doctors were processed.")

if __name__ == "__main__":
    standardize_data_format()