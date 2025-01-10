# LinkedIn Employee Data Dumper

This project is a tool to fetch employee data from a LinkedIn company page, generate email combinations, and store the results in a JSON file. 
It uses LinkedIn API scraping with provided credentials and cookies, and various modules for data extraction and email generation.


## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
---

## Features

- Fetches employee data from a LinkedIn company page.
- Generates email combinations based on a specified domain.
- Saves extracted data into a JSON file.
- Configurable via a `config.yaml` file.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/LinkedInFetcher.git
   cd LinkedInFetcher
   ```
   
2. Install dependencies:
  ```bash
    pip install -r requirements.txt
```

## Usage: 
  - Edit the config.yaml file to include your configurations:
  - LinkedIn credentials (email, password, and cookie).
  - Company domain and LinkedIn URL.
  - Output file name.

Run the script:
```bash
  python main.py config.yaml
```
The extracted data will be saved in the specified JSON file (e.g., employees.json).

## Configuration
All settings are stored in config.yaml. Below is an example configuration:
  ```bash
linkedin:
  cookie: "Your LinkedIn session cookie"
  email: "Your LinkedIn email"
  password: "Your LinkedIn password"
company:
  domain: "example.com"
  linkedin_url: "https://www.linkedin.com/company/example-company"
  output_file: "employees.json"
dumper:
  email_format: "{0}.{1}@example.com"
  include_private: true
  jitter: true
  quiet: false
```

Update the fields as needed.
