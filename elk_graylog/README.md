# Eksempel på logging-pipeline med Filebeat, Logstash og Graylog

Dette er et eksempel på lesing av logger med filebeat, parsing av disse med Logstash pipelines, indeksering i Elasticsearch gjennom Graylog.

## Hvordan kjøre eksempelet?

Scriptet `stream_log.py` kan brukes til å kontinuerlig skrive logglinjer til en fil som overvåkes av filebat. Som standard er filen som overvåkes (og skrives til av `stream_log.py`) `logs/stream.log`.  Denne trenger en loggfil i access-loggformat som den kan bygge nye logger på, denne angis med `input_log`-variabelen.

Alle komponenter (Elasticsearch, Logstash, Filebeat, Graylog, MongoDB) kjører i Docker og kan startes med
```
docker-compose up
```

Det er viktig å la Docker få tilgang til nok ressurser, vi kjører for øyeblikket Docker med tilgang til 6 CPUer og 6GiB RAM.

For å la Graylog motta loggmeldingene på det lages en input, gå til "System/Inputs" -> "Inputs" og lag en ny GELF UDP-input med passende navn. Behold standardinnstillingene.