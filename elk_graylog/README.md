# Eksempel på logging-pipeline med Filebeat, Logstash og Graylog

Dette er et eksempel på lesing av logger med filebeat, parsing av disse med Logstash pipelines, indeksering i Elasticsearch gjennom Graylog.

## Hvordan kjøre eksempelet?

### Førstegangsinitialisering

Eksempelet kjøres ved å først kjøre (kun første gang)
```bash
$ docker-compose build
$ ./initial_setup
```

### Kjøre eksempelet

Alle komponenter (Elasticsearch, Logstash, Filebeat, Graylog, MongoDB) kjører i Docker og kan startes med
```bash
$ docker-compose up
```

Det er viktig å la Docker få tilgang til nok ressurser, vi kjører for øyeblikket Docker med tilgang til 6 CPUer og 6 GiB RAM.

## Generere loggmeldinger

Scriptet `stream_log.py` kan brukes til å kontinuerlig skrive logglinjer til en fil som overvåkes av filebat. Som standard er filen som overvåkes (og skrives til av `stream_log.py`) `logs/stream.log`.  Denne trenger en loggfil i access-loggformat som den kan bygge nye logger på, denne angis med `input_log`-variabelen. Et eksempel på en slik fil er `difi-pt2-ki-web01.os.eon.no__var_log_dpi-registration_access_log.log.20181009`.

## Beskrivelse av pipeline

Scriptet `initial_setup` gjør det initielle oppsettet ved å
1. Opprette en index template i Elasticsearch for loggene.
2. Opprette en input i Graylog for loggdataene.
3. Opprette et indekssett i Graylog for loggdataene.
4. Opprette og starte en stream i Graylog for loggdataene som sørger for indeksere dokumentene i riktig indekssett.

Pipelinene fungerer som følger:
1. Filebeat leser loggene fra filen `stream.log` og sender dem til Logstash. Filebeatkonfigurasjonen ligger i `filebeat/filebeat.yml`, data ligger i `filebeat/data`.
2. Logstash tar imot loggene fra Filebeat, parser dem, og sender dem videre til Graylog. Logstashkonfigurasjonen ligger i `logstash/config/logstash.yml`, pipelinedefinisjonen ligger i `logstash/pipeline/access_logs.conf`.
3. Graylog tar imot loggene, og skriver dem til indekssettet `Access logs`. Dette gjøres med en regel, opprettet av `initial_setup`, for meldinger med `"fields_log_type": "access_log"`, som stammer fra Filebeat.

## Slette data og starte på nytt

Dersom man ønsker å starte helt på nytt er det mulig ved å gjøre:
```bash
$ docker-compose down
$ rm -rf elasticsearch/data mongo/data filebeat/data graylog/journal
```
