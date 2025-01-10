import json
from linkedin_api import Linkedin
from concurrent.futures import ThreadPoolExecutor

def fetch_contact_info(person, api, profiles_data, FILENAME):
    """
    Fetch LinkedIn contact information for a profile and update the data.
    """
    try:
        profile_url = person["Profile"]
        profile_name = profile_url.split('/')[-1]

        # Fetch contact info for the profile
        contact_info = api.get_profile_contact_info(profile_name)

        # Append contact info to the person's data
        person["Contact Info"] = contact_info

        # Save updated profiles data to out.json
        with open(FILENAME, 'w') as file:
            json.dump(profiles_data, file, indent=4)

        print(f"Fetched Contact Info for {person['Firstname']} {person['Lastname']}: {contact_info}")

    except Exception as e:
        print(f"Error fetching contact info for {person['Firstname']} {person['Lastname']}: {e}")

def run_linkedin_fetch(LINKEDIN_EMAIL, LINKEDIN_PASSWORD, FILENAME):
    """
    Main function to fetch contact information using LinkedIn API.
    """
    # Authenticate using LinkedIn user account credentials
    api = Linkedin(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)

    # Load profiles data from JSON file
    with open(FILENAME, 'r') as file:
        profiles_data = json.load(file)

    # Use ThreadPoolExecutor to make concurrent requests
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda person: fetch_contact_info(person, api, profiles_data, FILENAME), profiles_data)
