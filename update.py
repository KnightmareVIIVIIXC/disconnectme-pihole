import json
import os
import requests
from urllib.parse import urlparse

entities_link = "https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/entities.json"
services_link = "https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/master/services.json"


def retrieve_contents(link):
    try:
        response = requests.get(link)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error retrieving data from {link}: {e}")
        return None


def extract_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path.split("/")[0]
    return domain.lower().strip()


def generate_entities_files():
    content = retrieve_contents(entities_link)
    if not content:
        return

    try:
        entities = json.loads(content)["entities"]
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {e}")
        return

    domains = set()
    for entity in entities.values():
        for domain in entity.get("resources", []):
            domain = extract_domain(domain)
            if domain:
                domains.add(domain)

    with open("entities.txt", "w") as f:
        for domain in sorted(domains):
            print(domain, file=f)


def generate_services_files():
    content = retrieve_contents(services_link)
    if not content:
        return

    try:
        categories = json.loads(content)["categories"]
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {e}")
        return

    category_domains = {}
    for category, services in categories.items():
        for service in services:
            for domain_lists in service.values():
                for domain_list in domain_lists.values():
                    if isinstance(domain_list, list):
                        normalized_domains = {
                            extract_domain(domain) for domain in domain_list
                        }
                        category_domains.setdefault(category, set()).update(
                            normalized_domains
                        )

    with open("services.txt", "w") as f:
        for category, domains in sorted(category_domains.items()):
            for domain in sorted(domains):
                print(domain, file=f)

    for category, domains in sorted(category_domains.items()):
        with open(f"services_{category}.txt", "w") as f_category:
            for domain in sorted(domains):
                print(domain, file=f_category)


if __name__ == "__main__":
    generate_entities_files()
    generate_services_files()
