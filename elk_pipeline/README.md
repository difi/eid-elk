# Eksempel på logging-pipeline med filebeat, logstash og elasticsearch

Dette er et eksempel på lesing av logger (som potensielt strekker seg over flere linjer) med filebeat, parsing av disse med logstash pipelines, indeksering i Elasticsearch med et enkelt tilknyttet dashboard.

Docker-bildene som brukes har X-Pack aktivert for monitorering av både Elasticsearch og Logstash.

## Hvordan kjøre eksempelet?

### Generere eller klargjøre loggfiler

Scriptet `generate_large_log.py` kan brukes til å generere en stor loggfil med datoer i ønsket område. Scriptet tar utgangspunkt i et sett med loggfiler som ligger i to mapper. Gjør som følge:

Applikasjonslogger fra `oidc-prod-20181009.zip` plasseres i mappen `./application_logs`. Vi har brukt følgende filer:
```
difi-pt2-oidc-app01.os.eon.no__var_log_idporten-oidc-provider_idporten-oidc-provider-difi.log.20181009
difi-pt2-oidc-app01.os.eon.no__var_log_idporten-oidc-provider_idporten-oidc-provider-nondifi.log.20181009
difi-pt2-oidc-app01.os.eon.no__var_log_kontaktinfo-oauth2-server_kontaktinfo-oauth2-server-difi.log.20181009
difi-pt2-oidc-app01.os.eon.no__var_log_kontaktinfo-oauth2-server_kontaktinfo-oauth2-server-nondifi.log.20181009
difi-pt2-oidc-app02.os.eon.no__var_log_idporten-oidc-provider_idporten-oidc-provider-difi.log.20181009
difi-pt2-oidc-app02.os.eon.no__var_log_idporten-oidc-provider_idporten-oidc-provider-nondifi.log.20181009
difi-pt2-oidc-app02.os.eon.no__var_log_kontaktinfo-oauth2-server_kontaktinfo-oauth2-server-difi.log.20181009
difi-pt2-oidc-app02.os.eon.no__var_log_kontaktinfo-oauth2-server_kontaktinfo-oauth2-server-nondifi.log.20181009
```
Access-logger fra `ki-prod-20181009.zip` dekomprimeres i `./access_logs`. Vi har brukt følgende filer:
```
difi-pt2-ki-web01.os.eon.no__var_log_dpi-registration_access_log.log.20181009
difi-pt2-ki-web01.os.eon.no__var_log_idporten-authlevel-api_access_log.log.20181009
difi-pt2-ki-web01.os.eon.no__var_log_minidonthefly-api_access_log.log.20181009
difi-pt2-ki-web02.os.eon.no__var_log_dpi-registration_access_log.log.20181009
difi-pt2-ki-web02.os.eon.no__var_log_idporten-authlevel-api_access_log.log.20181009
difi-pt2-ki-web02.os.eon.no__var_log_minidonthefly-api_access_log.log.20181009
difi-pt2-ki-web03.os.eon.no__var_log_dpi-registration_access_log.log.20181009
difi-pt2-ki-web03.os.eon.no__var_log_idporten-authlevel-api_access_log.log.20181009
difi-pt2-ki-web03.os.eon.no__var_log_minidonthefly-api_access_log.log.20181009
difi-pt2-ki-web04.os.eon.no__var_log_dpi-registration_access_log.log.20181009
difi-pt2-ki-web04.os.eon.no__var_log_idporten-authlevel-api_access_log.log.20181009
difi-pt2-ki-web04.os.eon.no__var_log_minidonthefly-api_access_log.log.20181009
```

Kjør scriptet for å generere de store loggfilene:
```bash
python create_large_logs.py
```

### Sette variabel for Elastic versjon

Kjør dette i konsolen for å sette riktig versjon av Elastic stacken:
```bash
export ELK_VERSION=6.5.1
```

### Førstegangsinitialisering

Eksempelet kjøres ved å først kjøre (kun første gang)
```bash
$ docker-compose build
$ ./initial_setup
```

### Kjøre eksempelet

og deretter
```bash
$ docker-compose up
```

Ved debugging, der det ønskes å lese samme logg flere ganger, kan registry-filene til filebeat slettes først:
```bash
$ rm filebeat_application_logs/data/registry filebeat_access_logs/data/registry && docker-compose up
```

For å logge inn i Kibana er brukernavnet `elastic` og passordet `changeme`. Etter å ha åpnet Kibana, gå til "Management", "Index Patterns" og velg en av index-patternene (`logs_access*` eller `logs_application*`) som favoritt.

## Konfigurasjon

### Filebeat med multiline

Filebeat er konfigurert til å lese loggfiler fra mappen `logs` og sende dem til Logstash. Configurasjonen av filebeat litter i `filebeat/filebeat.yml`, les mer om multiline i Filebeat [her](https://www.elastic.co/guide/en/beats/filebeat/current/multiline-examples.html).

### Logstash med to pipelines, dissect og feltaugmentering

Logstash tar imot logghendelsene fra Filebeat og prosesserer dem i dette eksempelet i to pipeliner, en for tilgang- og en for applikasjonslogger. Konfigurasjonen til Logstash ligger i `logstash/config/logstash.yml`, mens pipelinekonfigurasjonene ligger i `logstash/config/access_logs.conf` og `logstash/config/application_logs.conf`. I konfigurasjonen av pipelinene er persistent queue aktivert, som betyr at Logstash kan håndtere flom av hendelser og garanterer minst en levering av hver hendelse. Les mer om logstash pipelines [her](https://www.elastic.co/guide/en/logstash/current/multiple-pipelines.html) og persistent queues [her](https://www.elastic.co/guide/en/logstash/current/persistent-queues.html).

I Logstash-pipelinene blir dissect-filter brukt til å parse loggene. Når det er mulig å bruke dissect istedenfor grok kan det lønne seg siden dissect er raskere, se flere detaljer [her](https://www.elastic.co/guide/en/logstash/current/plugins-filters-dissect.html).

Felt som ukedag og måned blir lagt til med Ruby-kode i `logstash/pipeline/logstash.conf`.

[Dead Letter Queues](https://www.elastic.co/guide/en/logstash/current/dead-letter-queues.html) er også aktivert. Denne holder styr på dokumenter som ikke kan bli prosessert av pipelinen i Logstash, og skrives i gjeldende konfigurasjon til mappen `logstash/dead_letter_queue`.

### Elasticsearch med index template

Konfigurasjonen til Elasticsearch er definert i `elasticsearch/config/elasticsearch.yml`. Det defineres også to indeksmaler som tar seg av mappingen til loggindeksene. Disse er definert i `elasticsearch/access_template.json` og `elasticsearch/application_template.json`.

### Kibana med logging dashboard og monitoring

For å logge inn i Kibana er brukernavnet `elastic` og passordet `changeme`.

Konfigurasjonen til Kibana ligger i `kibana/config/kibana.yml`. Siden X-Pack er aktivert kan Logstash, Kibana og Elasticsearch monitoreres i Kibana. Spesielt kan det være interessant å følge med på Logstash under indekseringen.

Et enkelt logging dashboard (med tilhørende index pattern og visualiseringer) ligger lagret i `kibana/saved_objects/export.json`, og importeres som en del av `initial_setup`-scriptet.

Det er verdt å legge merke til at, per versjon 6.5.0, objekter som eksporteres fra GUIet til Kibana ikke kompatible for import via APIet, og vice versa. `export.json` ble exportert med APIet, og kan derfor ikke importeres gjennom GUIet. Nyttige funksjoner for export og import gjennom Saved Objects APIet til Kibana finnes i `kibana_saved_objects.py`.

For å se på monitorering av logstash du kan åpne:
 - [Logstash monitorering i kibana](http://localhost:5601/app/monitoring#/logstash/)
 - API endepunkt logstash [pipelines](http://localhost:9600/_node/stats/pipelines?pretty). 
 - API endepunkt logstash [jvm](http://localhost:9600/_node/stats/jvm?pretty)
 - API endepunkt logstash [events](http://localhost:9600/_node/stats/events?pretty)
 - Dokumentasjon av logstash [Monitoring API](https://www.elastic.co/guide/en/logstash/current/monitoring.html)


## Machine Learning

When the indexing of the logs is done, one can add the machine learning job example by running:

```bash
$ ./ml-jobs.sh
```
