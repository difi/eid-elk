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

Loggmeldingene som indekseres er status og audit logger fra eFormidling. Filebeat er konfigurert til å lese loggmeldinger fra `logs/StatusAndAudit_source.json`. De originale loggmeldingene ble hentet ut med en `match`-query i Elasticsearch, og inneholder dermed ikke bare `_source`, men også annen info relatert til søket som `_score`. Python-scriptet `get_log_source.py` kan brukes til å lage en ren json-fil med kun `_source` som kan leses og håndteres direkte av Logstash.

For å bruke dette scriptet plasser `StatusAndAudit.json` i mappen `logs/` og kjør `get_log_source.py`. Scriptet vil opprette `logs/StatusAndAudit_source.json`.

## Beskrivelse av pipeline

Scriptet `initial_setup` gjør det initielle oppsettet ved å
1. Opprette en index template i Elasticsearch for loggene.
2. Opprette en input `Status and audit logs` i Graylog for loggdataene.
3. Opprette et indekssett `Status and audit logs` med indeksprefix `logs_status_and_audit` i Graylog for loggdataene.
4. Opprette og starte en stream i Graylog for loggdataene som sørger for å indeksere dokumentene i riktig indekssett.
5. Oppretter en pipeline i Graylog for å erstatte Graylog sitt timestamp med timestampet til hendelsen
6. Sørger for at rekkefølgen i "Message Processor Configuration" er korrekt.

Pipelinene fungerer som følger:
1. Filebeat leser loggene fra filen `logs/StatusAndAudit_source.json` og sender dem til Logstash. Filebeatkonfigurasjonen ligger i `filebeat/filebeat.yml`, data ligger i `filebeat/data`.
2. Logstash tar imot loggene fra Filebeat, parser dem, og sender dem videre til Graylog. Logstashkonfigurasjonen ligger i `logstash/config/logstash.yml`, pipelinedefinisjonen ligger i `logstash/pipeline/logs_status_and_audit.conf`.
3. Graylog tar imot loggene, og skriver dem til indekssettet `Status and audit logs`. Dette gjøres med en regel, opprettet av `initial_setup`, for meldinger med `"fields_log_type": "logs_status_and_audit"`, som stammer fra Filebeat.

Se ytterligere dokumentasjon på [Confluence](http://confluence.difi.local/pages/viewpage.action?pageId=63045634).

## Slette data og starte på nytt

Dersom man ønsker å starte helt på nytt er det mulig ved å gjøre:
```bash
$ docker-compose down
$ sudo rm -rf elasticsearch/data mongo/data filebeat/data graylog/journal
```
I linux opplever vi at filene under `graylog/journal` og `mongo/data` blir opprettet med en annen brukeren enn din bruker, pga hvordan docker imaget er satt opp. Derfor kjører vi disse kommandoene som `sudo`.

Hvis man trenger ikke persistering av data, en annen måte å fikse problemet ovenfor er å fjerne følgene `volumes` fra `docker-compose.yml`:
- `./graylog/journal:/usr/share/graylog/data/journal`
- `./mongo/data:/data/db`
- `./elasticsearch/data:/usr/share/elasticsearch/data`
- `./filebeat/data:/usr/share/filebeat/data/`

## Aksessere GUI

Du kan nå aksessere Graylog i [http://localhost:9000/](http://localhost:9000/). 
Bruk default brukernavn `admin` med default passord `admin` for å få tilgang.

