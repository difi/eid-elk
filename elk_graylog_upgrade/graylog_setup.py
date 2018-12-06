import requests
from urllib.parse import urljoin
import json
from datetime import datetime
import time
import pytz
import os
import time

# User configurable options
input_name = 'Status and audit logs'
log_type = 'logs_status_and_audit'
graylog_host = 'http://localhost:9000'
username = 'admin'
password = 'admin'

head = {
    'Content-Type': 'application/json'
}


def save_id(id_name, id):
    with open(os.path.join('graylog/ids', id_name), 'w') as fid:
        fid.write(id)


################################################################################
# Creating input, index set and stream
################################################################################

# Get ID of node (try until Graylog is ready)
print('Waiting for Graylog to start...', end='', flush=True)
full_path = urljoin(graylog_host, 'api/system/cluster/nodes')
while True:
    try:
        response = requests.get(full_path, auth=(username, password), headers=head)
        node_id = response.json()['nodes'][0]['node_id']
        break
    except requests.exceptions.ConnectionError:
        print('.', end='', flush=True)
        time.sleep(1)
print()

# Create input
input_def = {
      "title": "Status and audit logs",
      "global": True,
      "type": "org.graylog2.inputs.gelf.udp.GELFUDPInput",
      "configuration": {
        "override_source": None,
        "recv_buffer_size": 262144,
        "bind_address": "0.0.0.0",
        "port": 12201,
        "decompress_size_limit": 8388608
      },
      "node": None,
}
full_path = urljoin(graylog_host, 'api/system/inputs')
response = requests.post(full_path, auth=(username, password), headers=head, data=json.dumps(input_def))
if response.status_code >= 400:
    print(response.status_code, response.text, flush=True)
    exit(-1)
else:
    input_id = response.json()['id']
    print('Created input with ID ' + input_id, flush=True)
    save_id('input_id', input_id)

# Create stream with rule for log type
stream_def = {
    "matching_type": "AND",
    "title": input_name,
    "description": "Stream " + input_name.lower() + " to the " + input_name.lower() + " index set",
    "rules": [
        {
            "field": "fields_log_type",
            "description": "Route " + input_name.lower() + " to the " + input_name.lower() + " index set",
            "type": 1,
            "inverted": False,
            "value": log_type
        }
    ]
}
full_path = urljoin(graylog_host, 'api/streams')
response = requests.post(full_path, auth=(username, password), headers=head, data=json.dumps(stream_def))
if response.status_code >= 400:
    print(response.status_code, response.text, flush=True)
    exit(-1)
else:
    stream_id = response.json()['stream_id']
    print('Created stream with ID ' + stream_id, flush=True)

# Start stream
full_path = urljoin(graylog_host, 'api/streams/' + stream_id + '/resume')
response = requests.post(full_path, auth=(username, password), headers=head)
if response.status_code >= 400:
    print(response.status_code, response.text, flush=True)
    exit(-1)
else:
    print('Started stream with ID ' + stream_id, flush=True)


# The rest of the script is not needed as pipelines are not used by eFormidling
exit(0)

################################################################################
# Pipeline for setting Graylog timestamp to event timestamp
################################################################################

# Create pipeline rule for parsing timestamp
pipeline_rule_def = {
    "title": "parse event timestamp",
    "description": "Replace graylog timestamp with event timestamp",
    "source": """rule "parse event timestamp"
when
    true
then
    set_field("timestamp", flex_parse_date(to_string($message.event_timestamp)));
    remove_field("event_timestamp");
end"""
}
full_path = urljoin(graylog_host, 'api/plugins/org.graylog.plugins.pipelineprocessor/system/pipelines/rule')
response = requests.post(full_path, auth=(username, password), headers=head, data=json.dumps(pipeline_rule_def))
if response.status_code >= 400:
    print(response.status_code, response.text, flush=True)
    exit(-1)
else:
    pipeline_rule_id = response.json()['id']
    print('Created pipeline rule with ID ' + pipeline_rule_id, flush=True)

# Create pipeline
pipeline_def = {
    "title": "Timestamp",
    "description": "Replaces Graylog timestamp with event timestamp",
    "source": """pipeline "Timestamp"
stage 0 match all
rule "parse event timestamp"
end"""
}
full_path = urljoin(graylog_host, 'api/plugins/org.graylog.plugins.pipelineprocessor/system/pipelines/pipeline')
response = requests.post(full_path, auth=(username, password), headers=head, data=json.dumps(pipeline_def))
if response.status_code >= 400:
    print(response.status_code, response.text, flush=True)
    exit(-1)
else:
    pipeline_id = response.json()['id']
    print('Created pipeline rule with ID ' + pipeline_id, flush=True)

# Define connection between pipeline and stream
stream_connection_def = {
    "stream_id": stream_id,
    "pipeline_ids": [
        pipeline_id
    ]
}
full_path = urljoin(
    graylog_host,
    'api/plugins/org.graylog.plugins.pipelineprocessor/system/pipelines/connections/to_stream'
)
response = requests.post(full_path, auth=(username, password), headers=head, data=json.dumps(stream_connection_def))
if response.status_code >= 400:
    print(response.status_code, response.text, flush=True)
    exit(-1)
else:
    stream_connection_id = response.json()['id']
    print('Created stream connection with ID ' + stream_connection_id, flush=True)

################################################################################
# Make sure "Pipeline Processor" is below "Message Filter Chain" in the Message Processors Configuration
################################################################################

# Get the current Message Processors Configuration
full_path = urljoin(graylog_host, 'api/system/messageprocessors/config')
response = requests.get(full_path, auth=(username, password), headers=head)
message_processors_configuration_def = response.json()
processor_order = message_processors_configuration_def['processor_order']

# Find the correct order
ind_pipeline = -1
class_name_pipeline = 'org.graylog.plugins.pipelineprocessor.processors.PipelineInterpreter'
ind_message = -1
class_name_message = 'org.graylog2.messageprocessors.MessageFilterChainProcessor'
for i in range(len(processor_order)):
    if processor_order[i]['class_name'] == class_name_pipeline:
        ind_pipeline = i
    elif processor_order[i]['class_name'] == class_name_message:
        ind_message = i

# Switch the order if necessary and update the Message Processors Configuration
if ind_pipeline < ind_message:
    processor_order_tmp = processor_order[ind_pipeline]
    processor_order[ind_pipeline] = processor_order[ind_message]
    processor_order[ind_message] = processor_order_tmp

    # Update the Message Processors Configuration
    message_processors_configuration_def['processor_order'] = processor_order
    full_path = urljoin(graylog_host, 'api/system/messageprocessors/config')
    response = requests.put(full_path, auth=(username, password), headers=head,
                            data=json.dumps(message_processors_configuration_def))
    if response.status_code >= 400:
        print(response.status_code, response.text, flush=True)
        exit(-1)
    else:
        print('Updated message processors configuration', flush=True)
else:
    print('Did not need to update message processors configuration', flush=True)
