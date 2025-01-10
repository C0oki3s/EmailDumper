import requests
import json
import re
import time
import random
import unidecode
import urllib.parse
from datetime import datetime

class LinkedInDumper:
    def __init__(self, cookie, email_format=None, include_private=False, jitter=False, quiet=False, csrftoken="ajax:4913164021469932139"):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Content-type': 'application/json',
            'Csrf-Token': f"{csrftoken}"
        }
        self.cookies = {
            "li_at": cookie,
            "JSESSIONID": f"{csrftoken}"
        }
        self.email_format = email_format
        self.include_private = include_private
        self.jitter = jitter
        self.quiet = quiet
        self.special_chars = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}

    def clean_text(self, text):
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"
            u"\u3030"
            "]+", re.UNICODE)
        
        cleaned = re.sub(emoji_pattern, '', text).strip()
        cleaned = cleaned.replace('Ü','Ue').replace('Ä','Ae').replace('Ö','Oe')
        cleaned = cleaned.replace('ü','ue').replace('ä','ae').replace('ö','oe')
        cleaned = cleaned.replace(',', '').replace(';', ',')
        return unidecode.unidecode(cleaned).strip()

    def get_company_id(self, company_name):
        company_encoded = urllib.parse.quote(company_name)
        url = f"https://www.linkedin.com/voyager/api/voyagerOrganizationDashCompanies?decorationId=com.linkedin.voyager.dash.deco.organization.MiniCompany-10&q=universalName&universalName={company_encoded}"
        response = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=200)
        return response.json()["elements"][0]["entityUrn"].split(":")[-1]

    def get_employees(self, company_id, start=0, count=10):
        url = f"https://www.linkedin.com/voyager/api/search/dash/clusters?decorationId=com.linkedin.voyager.dash.deco.search.SearchClusterCollection-165&origin=COMPANY_PAGE_CANNED_SEARCH&q=all&query=(flagshipSearchIntent:SEARCH_SRP,queryParameters:(currentCompany:List({company_id}),resultType:List(PEOPLE)),includeFiltersInResponse:false)&count={count}&start={start}"
        if self.jitter:
            time.sleep(random.choice([0.5, 1, 0.8, 0.3, 3, 1.5, 5]))
        response = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=200)
        return response.json()

    def parse_employee(self, employee):
        try:
            name = self.clean_text(employee["itemUnion"]['entityResult']["title"]["text"]).split()
            name = [n for n in name if n not in ['Prof.', 'Dr.', 'M.A.', ',', 'LL.M.']]
            
            firstname = ' '.join(name[:-1]) if len(name) > 2 else name[0]
            lastname = name[-1]
            
            position = self.clean_text(employee["itemUnion"]['entityResult'].get("primarySubtitle", {}).get("text", "N/A"))
            location = employee["itemUnion"]['entityResult'].get("secondarySubtitle", {}).get("text", "N/A")
            profile = employee["itemUnion"]['entityResult'].get("navigationUrl", "N/A").split("?")[0]

            if (firstname != "LinkedIn" and lastname != "Member") or self.include_private:
                email = self.email_format.format(
                    firstname.replace(".","").lower().translate(self.special_chars),
                    lastname.replace(".","").lower().translate(self.special_chars)
                ) if self.email_format else ""

                return {
                    "Firstname": firstname,
                    "Lastname": lastname,
                    "Email": email,
                    "Position": position,
                    "Gender": "N/A",
                    "Location": location,
                    "Profile": profile
                }
        except Exception:
            return None

    def dump_employees(self, company_url, output_file):
        if not company_url.startswith('https://www.linkedin.com/company/'):
            raise ValueError("Invalid LinkedIn company URL")
        
        company_name = company_url.split('company/')[1].split('/')[0]
        company_id = self.get_company_id(company_name)
        
        if not self.quiet:
            print(f"[i] Processing {company_name} (ID: {company_id})")

        initial_data = self.get_employees(company_id, 0)
        total_employees = initial_data["paging"]["total"]
        required_pages = -(-total_employees // 10)

        employees = []
        for page in range(required_pages):
            if not self.quiet:
                print(f"Progress: {page+1}/{required_pages}", end='\r')
                
            response = self.get_employees(company_id, page * 10)
            for element in response.get("elements", []):
                for item in element.get("items", []):
                    employee = self.parse_employee(item)
                    if employee:
                        employees.append(employee)

        # Remove duplicates while preserving order
        unique_employees = list({json.dumps(emp): emp for emp in employees}.values())

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_employees, f, indent=4, ensure_ascii=False)

        if not self.quiet:
            print(f"\n[i] Dumped {len(unique_employees)} employees to {output_file}")