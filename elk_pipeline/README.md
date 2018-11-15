# Eksempel på logging-pipeline med filebeat, logstash og elasticsearch

Dette er et eksempel på lesing av logger (som potensielt strekker seg over flere linjer) med filebeat, parsing av disse med logstash pipelines, indeksering i Elasticsearch med et enkelt tilknyttet dashboard.

Docker-bildene som brukes har X-Pack aktivert for monitorering av både Elasticsearch og Logstash.

## Hvordan kjøre eksempelet?

### Generere eller klargjøre loggfiler

Loggen det ønskes å indeksere må legges i mappen `logs`. Scriptet `generate_large_log.py` kan brukes til å generere en stor loggfil med datoer i ønsket område. Scriptet tar utgangspunkt i et sett med loggfiler som ligger i en mappe, plasseringen av denne mappen angis med variabelen `input_logs_dir`. Scriptet har blitt tested med følgende loggfiler fra `oidc-prod-20181009.zip`:
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
Etter å ha endret variablene i første kodeblokk etter ønske kjøres scriptet for å generere loggfilen:
```bash
python create_large_logs.py
```

### Førstegangsinitialisering

Eksempelet kjøres ved å først kjøre (kun første gang)
```bash
$ ELK_VERSION=6.4.3 docker-compose build
$ ./initial_setup
```

### Kjøre eksempelet

og deretter
```bash
$ ELK_VERSION=6.4.3 docker-compose up
```

Ved debugging, der det ønskes å lese samme logg flere ganger, kan registry-filen til filebeat slettes først:
```bash
$ rm filebeat/data/registry && ELK_VERSION=6.4.3 docker-compose up
```

For å logge inn i Kibana er brukernavnet `elastic` og passordet `changeme`.

## Konfigurasjon

### Filebeat med multiline

Filebeat er konfigurert til å lese loggfiler fra mappen `logs` og sende dem til Logstash. Configurasjonen av filebeat litter i `filebeat/filebeat.yml`, les mer om multiline i Filebeat [her](https://www.elastic.co/guide/en/beats/filebeat/current/multiline-examples.html).

### Logstash med pipelines, dissect og feltaugmentering

Logstash tar imot logghendelsene fra Filebeat og prosesserer dem i dette eksempelet én pipeline. Konfigurasjonen til Logstash ligger i `logstash/config/logstash.yml`, mens pipelinekonfigurasjonen ligger i `logstash/config/pipelines.yml`. I konfigurasjonen av pipelinen er persistent queue aktivert, som betyr at Logstash kan håndtere flom av hendelser og garanterer minst en levering av hver hendelse. Les mer om logstash pipelines [her](https://www.elastic.co/guide/en/logstash/current/multiple-pipelines.html) og persistent queues [her](https://www.elastic.co/guide/en/logstash/current/persistent-queues.html).

Logstash-pipelinen er definert i `logstash/pipeline/logstash.conf`, hvor et dissect-filter blir brukt til å parse loggen. Når det er mulig å bruke dissect istedenfor grok kan det lønne seg siden dissect er raskere, se flere detaljer [her](https://www.elastic.co/guide/en/logstash/current/plugins-filters-dissect.html).

Felt som ukedag og måned blir lagt til med Ruby-kode i `logstash/pipeline/logstash.conf`.

### Elasticsearch med index template

Konfigurasjonen til Elasticsearch er definert i `elasticsearch/config/elasticsearch.yml`. Det defineres også en index template som tar seg av mappingen av loggindeksen. Denne er definert i `elasticsearch/mapping_template.json`.

### Kibana med logging dashboard og monitoring

For å logge inn i Kibana er brukernavnet `elastic` og passordet `changeme`.

Konfigurasjonen til Kibana ligger i `kibana/config/kibana.yml`. Siden X-Pack er aktivert kan Logstash, Kibana og Elasticsearch monitoreres i Kibana. Spesielt kan det være interessant å følge med på Logstash under indekseringen.

Et enkelt logging dashboard (med tilhørende index pattern og visualiseringer) ligger lagret i `kibana/saved_objects/export.json`, og importeres som en del av `initial_setup`-scriptet.

## Nyttige funksjoner

Nyttige funksjoner for å eksportere og importere lagrede objekter i Kibana (som index templates, dashboards etc.), finnes i `kibana_saved_objects.py`.