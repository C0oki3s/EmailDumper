import yaml
import sys
from LinkedinAPI import run_linkedin_fetch
from Combinations import generate_email_combinations
from Linkedindump import LinkedInDumper

def load_config(config_file):
    with open(config_file, "r") as file:
        return yaml.safe_load(file)

if len(sys.argv) != 2:
    print("[ERROR] Please provide the path to your config.yaml file as an argument.")
    print("Usage: python script.py <path_to_config.yaml>")
    exit(1)

config_file = sys.argv[1]

try:
    config = load_config(config_file)
except FileNotFoundError:
    print(f"[ERROR] The configuration file '{config_file}' was not found.")
    print("Please ensure the correct path to your config.yaml is provided.")
    exit(1)

cookie = config["linkedin"]["cookie"]
linkedin_email = config["linkedin"]["email"]
linkedin_password = config["linkedin"]["password"]

domain = config["company"]["domain"]
linkedin_url = config["company"]["linkedin_url"]
output_file = config["company"]["output_file"]

dumper_config = config["dumper"]

dumper = LinkedInDumper(
    cookie=cookie,
    email_format=dumper_config["email_format"],
    include_private=dumper_config["include_private"],
    jitter=dumper_config["jitter"],
    quiet=dumper_config["quiet"],
    csrftoken=dumper_config["csrftoken"]
)

try:
    dumper.dump_employees(linkedin_url, output_file)
except Exception as e:
    print("Error during dumping employees:", str(e))
    print("Please add or refresh the CSRF token and cookie.")
    print("Logout and login to your account again, then update the cookie and CSRF token in the config file.")

try:
    run_linkedin_fetch(linkedin_email, linkedin_password, output_file)
except Exception as e:
    print("Error during LinkedIn Profile fetch:", str(e))

try:
    generate_email_combinations(output_file, output_file, domain=domain)
except Exception as e:
    print("Error during generating email combinations:", str(e))
    print("Please ensure the output file and domain configurations are correct.")
