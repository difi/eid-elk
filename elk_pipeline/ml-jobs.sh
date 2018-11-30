#!/bin/bash

ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=changeme
ES_URL="http://$ELASTIC_USERNAME:$ELASTIC_PASSWORD@localhost:9200"


printf "Defining the job..."
curl -s -H 'Content-Type: application/json' \
     -X PUT $ES_URL/_xpack/ml/anomaly_detectors/access-log-event-responsetime-size \
     -d'
{
  "description": "Access log multiple anomaly in event count, response time and response size",
  "analysis_config": {
    "bucket_span": "6h",
    "detectors": [
      {
        "detector_description": "mean(size)",
        "function": "mean",
        "field_name": "size",
        "detector_index": 0
      },
      {
        "detector_description": "high_mean(responsetime_in_ms)",
        "function": "high_mean",
        "field_name": "responsetime_in_ms",
        "detector_index": 1
      },
      {
        "detector_description": "count",
        "function": "count",
        "detector_index": 2
      }
    ],
    "influencers": [
      "request.keyword",
      "remote_host"
    ]
  },
  "analysis_limits": {
    "model_memory_limit": "10mb",
    "categorization_examples_limit": 4
  },
  "data_description": {
    "time_field": "@timestamp",
    "time_format": "epoch_ms"
  }
}' > /dev/null

# Open the job for execution
printf "\nOpening the job: "
curl -s -H 'Content-Type:application/json' \
     -X POST $ES_URL/_xpack/ml/anomaly_detectors/access-log-event-responsetime-size/_open

# Define a data feed to connect the job to the data
curl -s -H 'Content-Type:application/json' \
     -X PUT $ES_URL/_xpack/ml/datafeeds/datafeed-access-log-event-responsetime-size \
     -d'
{
  "job_id": "access-log-event-responsetime-size",
  "indices": ["logs_access"]
}'

# Start the job
printf "\nExecuting the job: "
curl -s -H 'Content-Type:application/json' \
     -X POST $ES_URL/_xpack/ml/datafeeds/datafeed-access-log-event-responsetime-size/_start

printf "\nWaiting for the job to finish"
sleep 20

# Stop the data feed
printf "\nStopping the job... "
curl -s -H 'Content-Type:application/json' \
     -X POST $ES_URL/_xpack/ml/datafeeds/datafeed-access-log-event-responsetime-size/_stop

# Close the job for execution
printf "\nClosing the job: "
curl -s -H 'Content-Type:application/json' \
     -X POST $ES_URL/_xpack/ml/anomaly_detectors/access-log-event-responsetime-size/_close

printf "\ndone.\n"
