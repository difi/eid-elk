# Multiline med filebeat og logstash

Her er et eksempel på lesing av multiline-logger med filebeat. Eksempelloggen ligger i `./logs` og filebeat-konfigurasjonen ligger i `./filebeat/filebeat.yml`.

Docker-bildene som brukes har X-Pack aktivert for monitorering av både Elasticsearch og Logstash.

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
