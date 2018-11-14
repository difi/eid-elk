# Multiline med filebeat og logstash

Her er et eksempel på lesing av multiline-logger med filebeat. Eksempelloggen ligger i `./logs` og filebeat-konfigurasjonen ligger i `./filebeat/filebeat.yml`.

Docker-bildene som brukes har X-Pack aktivert for monitorering av både Elasticsearch og Logstash.

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

Eksempelet kjøres ved å først kjøre (kun første gang)
```bash
$ ELK_VERSION=6.4.3 docker-compose build
$ ./initial_setup
```
og deretter
```bash
$ ELK_VERSION=6.4.3 docker-compose up
```

Ved debugging, der det ønskes å lese samme logg flere ganger, kan registry-filen til filebeat slettes først:
```bash
$ rm filebeat/data/registry && ELK_VERSION=6.4.3 docker-compose up
```
