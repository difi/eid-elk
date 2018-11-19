# Contains two useful functions to export and import saved objects in Kibana.

import requests
from urllib.parse import urljoin
import json

# User configurable options
kibana_host_default = 'http://localhost:5601'
saved_objects_path_default = './kibana/saved_objects/export.json'
username_default = 'elastic'
password_default = 'changeme'


head = {
    'Content-Type': 'application/json',
    'kbn-xsrf': 'true'
}

types_default = ['visualization', 'dashboard', 'search', 'index-pattern']

def export_saved_objects(
        kibana_host=kibana_host_default,
        saved_objects_path=saved_objects_path_default,
        username=username_default,
        password=password_default,
        types=types_default
):
    """

    :param kibana_host: Address to Kibana
    :param saved_objects_path: Full address of json file to save objects to
    :param username: Kibana username
    :param password: Kibana password
    :return:
    """
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


def import_saved_objects(
        kibana_host=kibana_host_default,
        saved_objects_path=saved_objects_path_default,
        username=username_default,
        password=password_default
):
    with open(saved_objects_path, 'r') as fid:
        saved_objects = fid.read()

    full_path = urljoin(kibana_host, 'api/saved_objects/_bulk_create')
    response = requests.post(full_path, headers=head, auth=(username, password),
                             data=saved_objects)
    if response.status_code != 200:
        print(response.status_code, response.text)
        return -1

    return 0