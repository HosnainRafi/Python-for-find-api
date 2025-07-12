import os
import json
from pathlib import Path

def standardize_data_format():
    # Get the absolute path to the current script's directory
    script_dir = Path(__file__).parent.resolve()
    
    # Define input directory (Doctor_Details folder)
    input_dir = script_dir / "Doctor_Details"
    
    # Create output directory (Standardized_Doctor_Details)
    output_dir = script_dir / "Standardized_Doctor_Details"
    output_dir.mkdir(exist_ok=True)
    
    # Get all JSON files in Doctor_Details folder automatically
    district_files = list(input_dir.glob("doctors-details-*.json"))
    
    if not district_files:
        print(f"No district files found in {input_dir}")
        print(f"Looking for files named: doctors-details-*.json")
        return
    
    all_doctors = []
    duplicates_removed = 0
    
    for file_path in district_files:
        try:
            district = file_path.stem.replace("doctors-details-", "")
            print(f"\nProcessing {district}...")
            
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
                        'rating': doctor.get('rating'),
                        'chambers': doctor.get('chambers', []),
                        'source': {
                            'hospital': doctor.get('hospital_name') or doctor.get('source_hospital'),
                            'link': doctor.get('hospital_link') or doctor.get('source_hospital_link')
                        }
                    }
                    
                    # Remove empty fields
                    standardized = {k: v for k, v in standardized.items() if v}
                    standardized_doctors.append(standardized)
                
                # Save individual district file
                output_path = output_dir / f"standardized-{district}.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(standardized_doctors, f, ensure_ascii=False, indent=2)
                
                all_doctors.extend(standardized_doctors)
                print(f"✅ Processed {len(standardized_doctors)} doctors")
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {str(e)}")
    
    if all_doctors:
        # Save combined file
        combined_path = output_dir / "all-doctors-combined.json"
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(all_doctors, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*50)
        print(f"Standardization complete!")
        print(f"🏥 Total districts processed: {len(district_files)}")
        print(f"👨‍⚕️ Total doctors: {len(all_doctors)}")
        print(f"🚫 Duplicates removed: {duplicates_removed}")
        print(f"📁 Output directory: {output_dir}")
    else:
        print("\nNo doctors were processed. Please check your input files.")

if __name__ == "__main__":
    standardize_data_format()