# Multiline med filebeat og logstash

Her er et eksempel på lesing av multiline-logger med filebeat. Eksempelet kjøres ved å bruke Docker, og startes med
```bash
$ ELK_VERSION=6.4.3 docker-compose up
```

Ved debugging, der det ønskes å lese samme logg flere ganger, kan registry-filen til filebeat slettes først:
```bash
$ rm filebeat/data/registry && ELK_VERSION=6.4.3 docker-compose up
```

Eksempelloggen ligger i `./logs` og filebeat-konfigurasjonen ligger i `./filebeat/filebeat.yml`.
