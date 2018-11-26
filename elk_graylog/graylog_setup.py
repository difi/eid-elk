import requests
from urllib.parse import urljoin
import json
from datetime import datetime
import time
import pytz

# User configurable options
input_name = 'Access logs'
graylog_host = 'http://localhost:9000'
username = 'admin'
password = 'admin'

head = {
    'Content-Type': 'application/json'
}

# Get ID of node
full_path = urljoin(graylog_host, 'api/system/cluster/nodes')
response = requests.get(full_path, auth=(username, password), headers=head)
node_id = response.json()['nodes'][0]['node_id']

# Great input
input_def = {
    "title": input_name,
    "global": False,
    "type": "org.graylog2.inputs.gelf.udp.GELFUDPInput",
    "node": node_id,
    "configuration": {
        "override_source": None,
        "recv_buffer_size": 262144,
        "bind_address": "0.0.0.0",
        "port": 12201,
        "decompress_size_limit": 8388608
    }}
full_path = urljoin(graylog_host, 'api/system/inputs')
response = requests.post(full_path, auth=(username, password), headers=head, data=json.dumps(input_def))
if response.status_code >= 400:
    print(response.status_code, response.text)
    exit(-1)
else:
    print('Created input with ID ' + response.json()['id'])

# Create index set
index_set_def = {
    "title": "Access logs",
    "description": "Index set for access logs",
    "index_prefix": "logs_access",
    "shards": 1,
    "replicas": 0,
    "creation_date": datetime.now(pytz.timezone(time.localtime().tm_zone)).isoformat(),
    "rotation_strategy_class": "org.graylog2.indexer.rotation.strategies.MessageCountRotationStrategy",
    "rotation_strategy": {
        "type": "org.graylog2.indexer.rotation.strategies.MessageCountRotationStrategyConfig",
        "max_docs_per_index": 20000000
    },
    "retention_strategy_class": "org.graylog2.indexer.retention.strategies.DeletionRetentionStrategy",
    "retention_strategy": {
        "type": "org.graylog2.indexer.retention.strategies.DeletionRetentionStrategyConfig",
        "max_number_of_indices": 20
    },
    "index_analyzer": "standard",
    "index_optimization_max_num_segments": 1,
    "index_optimization_disabled": False,
    "writable": True,
    "default": False
}
full_path = urljoin(graylog_host, 'api/system/indices/index_sets')
response = requests.post(full_path, auth=(username, password), headers=head, data=json.dumps(index_set_def))
if response.status_code >= 400:
    print(response.status_code, response.text)
    exit(-1)
else:
    index_set_id = response.json()['id']
    print('Created index set with ID ' + index_set_id)

# Create stream with rule for access logs type
stream_def = {
    "matching_type": "AND",
    "description": "Stream access logs to the access logs index set",
    "rules": [
        {
            "field": "fields_log_type",
            "description": "Route access log to access logs index set",
            "type": 1,
            "inverted": False,
            "value": "access_log"
        }
    ],
    "title": "Access logs",
    "remove_matches_from_default_stream": True,
    "index_set_id": index_set_id
}
full_path = urljoin(graylog_host, 'api/streams')
response = requests.post(full_path, auth=(username, password), headers=head, data=json.dumps(stream_def))
if response.status_code >= 400:
    print(response.status_code, response.text)
    exit(-1)
else:
    stream_id = response.json()['stream_id']
    print('Created stream with ID ' + stream_id)

# Start stream
full_path = urljoin(graylog_host, 'api/streams/' + stream_id + '/resume')
response = requests.post(full_path, auth=(username, password), headers=head)
if response.status_code >= 400:
    print(response.status_code, response.text)
    exit(-1)
else:
    print('Started stream with ID ' + stream_id)
