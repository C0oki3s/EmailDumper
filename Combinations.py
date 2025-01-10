import itertools
from typing import List, Tuple
import unicodedata
from unidecode import unidecode
import json
import re


class EmailGenerator:
    def __init__(self, normalize: bool = True):
        self.normalize = normalize

    def normalize_name(self, name: str) -> str:
        name = name.lower()
        name = unidecode(name)
        normalized = unicodedata.normalize('NFKD', name)
        ascii_encoded = normalized.encode('ascii', 'ignore').decode('ascii')
        email_compliant = re.sub(r'[^a-zA-Z0-9]', '', ascii_encoded)
        return email_compliant

    def parse_name(self, full_name: str) -> Tuple[str, str, str]:
        parts = full_name.split()

        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            if len(parts[1]) == 1:
                return parts[0], parts[1], ""
            else:
                return parts[0], "", parts[1]
        else:
            return parts[0], "", " ".join(parts[1:]) if len(parts) > 1 else ""

    def generate_variants(self, full_name: str, domain: str) -> List[str]:
        first_name, middle_name, last_name = self.parse_name(full_name)

        if self.normalize:
            first_name = self.normalize_name(first_name)
            middle_name = self.normalize_name(middle_name)
            last_name = self.normalize_name(last_name)

        variants = set()

        patterns = [
            first_name,
            last_name,
            f"{first_name}{middle_name}",
            f"{first_name}.{middle_name}",
            f"{first_name}_{middle_name}",
            *([] if not last_name else [
                f"{first_name}{last_name}",
                f"{first_name}.{last_name}",
                f"{first_name}_{last_name}",
                f"{first_name[0]}{last_name}",
                f"{first_name[0]}.{last_name}",
                f"{first_name[0]}.{last_name[0]}"
            ]),
            *([] if not (middle_name and last_name) else [
                f"{first_name}{middle_name}{last_name}",
                f"{first_name}.{middle_name}.{last_name}",
                f"{first_name}{middle_name[0]}{last_name}",
                f"{first_name[0]}{middle_name[0]}{last_name}",
                f"{first_name[0]}{middle_name[0]}{last_name[0]}",
            ])
        ]

        variants.update(patterns)
        return [f"{variant}@{domain}" for variant in variants if variant]


def generate_email_combinations(input_file: str, output_file: str, domain: str):
    """
    Generate email combinations and update the input JSON file.
    """
    with open(input_file, 'r') as file:
        data = json.load(file)

    generator = EmailGenerator()

    for person in data:
        first_name = person.get("Firstname", "")
        last_name = person.get("Lastname", "")
        full_name = f"{first_name} {last_name}"
        emails = generator.generate_variants(full_name, domain)
        person["combination_email"] = emails

    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)
