# Lekekasse for oppgradering fra Graylog 2.1 og Elasticsearch 2.4 til Graylog 2.4 og Elasticsearch 5.6

Dette er en lekekasse for eksperimetering med oppgraderingsprosessen fra Graylog 2.1 og Elasticsearch 2.4 til Graylog 2.4 og Elasticsearch 5.6. Mer detaljert beskrivelse finnes på [Confluence](http://confluence.difi.local/display/EID/Oppgradering+fra+Graylog+2.1.2+og+Elasticsearch+2.4+til+Graylog+2.4+og+Elasticsearch+5.6).

For å kjøre eksempelet må det ligge en fil med navn `StatusAndAudit_source.json` i mappen `logs`, denne kan lages på samme måte som eksempelet `elk_graylog` som også ligger i dette repoet. Det kan være nyttig å gå gjennom det eksempelet før man går gjennom oppgraderingen.

## Hvordan kjøre eksempelet?

### Førstegangsinitialisering

Eksempelet kjøres ved å først kjøre (kun første gang)
```bash
$ docker-compose build
$ ./initial_setup
```

### Kjøre eksempelet

Alle komponenter (Elasticsearch, Logstash, Graylog, MongoDB) kjører i Docker og kan startes med
```bash
$ docker-compose up
```

Deretter kan oppgraderingsguiden på [Confluence](http://confluence.difi.local/display/EID/Oppgradering+fra+Graylog+2.1.2+og+Elasticsearch+2.4+til+Graylog+2.4+og+Elasticsearch+5.6) følges.

Det er viktig å la Docker få tilgang til nok ressurser, vi kjører for øyeblikket Docker med tilgang til 6 CPUer og 6 GiB RAM.
