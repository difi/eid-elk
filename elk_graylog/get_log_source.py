import json

# User configurable options
input_log = './logs/StatusAndAudit.json'
output_log = './logs/StatusAndAudit_source.json'
source_fields_to_remove = ['gl2_source_node', 'level', 'streams', 'full_message']

# Read json and extract source
with open(input_log, 'r') as fid_in:
    with open(output_log, 'w') as fid_out:
        for line in fid_in:
            search_result = json.loads(line)
            source = search_result['_source']
            for key in source_fields_to_remove:
                source.pop(key)
            fid_out.write(json.dumps(source) + '\n')
