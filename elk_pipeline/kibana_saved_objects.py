import requests
from urllib.parse import urljoin
import json

# User configurable options
kibana_host = 'http://localhost:5601'
saved_objects_path = './kibana/saved_objects/export.json'
username = 'elastic'
password = 'changeme'


head = {
    'Content-Type': 'application/json',
    'kbn-xsrf': 'true'
}

types = ['visualization', 'dashboard', 'search', 'index-pattern']

def export_saved_objects():
    full_path = urljoin(kibana_host, 'api/saved_objects/_find')
    response = requests.get(full_path, auth=(username, password), headers=head,
                            params={"type": types})
    saved_objects = response.json()['saved_objects']
    if response.status_code != 200:
        print(response.status_code, response.text)
        return -1

    # Remove "updated_at" key as it is now allowed when posting
    for object in saved_objects:
        object.pop("updated_at")

    with open(saved_objects_path, 'w') as fid:
        fid.write(json.dumps(saved_objects, indent=2))

    return 0


def import_saved_objects():
    with open(saved_objects_path, 'r') as fid:
        saved_objects = fid.read()

    full_path = urljoin(kibana_host, 'api/saved_objects/_bulk_create')
    response = requests.post(full_path, headers=head, auth=(username, password),
                             data=saved_objects)
    if response.status_code != 200:
        print(response.status_code, response.text)
        return -1

    return 0