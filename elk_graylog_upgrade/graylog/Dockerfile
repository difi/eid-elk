# Graylog 2.1.2
FROM graylog2/server:2.1.2-1

# Graylog 2.2.1
# FROM graylog/graylog:2.2.1-1

# Graylog 2.3.2
# FROM graylog/graylog:2.3.2-1

# Graylog 2.4.6
# FROM graylog/graylog:2.4.6-1

# Install jq to be able to parse json
RUN apt-get update && apt-get install -y wget curl
RUN wget -q https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
RUN chmod +x jq-linux64
RUN mv jq-linux64 /usr/bin/jq
