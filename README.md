# dashboarddeelmobiliteit-api-admin
Een API voor gebruikers-, organisatie- en financieel beheer voor het Dashboard Deelmobiliteit

# ssh tunnels
```bash
ssh -L 5433:10.133.75.95:5432 root@auth.deelfietsdashboard.nl
```

# Mailing (E-mail gebruikers)

De `/mailing/*` endpoints (alleen voor admins) versturen e-mails via SMTP. Benodigde environment variables:

| Variabele        | Omschrijving                                                | Default                    |
|------------------|-------------------------------------------------------------|----------------------------|
| `SMTP_HOST`      | SMTP-server (verplicht)                                     |                            |
| `SMTP_PORT`      | Poort                                                       | `587`                      |
| `SMTP_SECURITY`  | `starttls`, `ssl` of `none` (bijv. lokale mail-catcher)     | `starttls`                 |
| `SMTP_USER`      | Gebruikersnaam (optioneel, geen login als leeg)             |                            |
| `SMTP_PASSWORD`  | Wachtwoord (in k8s via secret `smtp-password`)              |                            |
| `SMTP_FROM`      | Afzenderadres (verplicht)                                   |                            |
| `SMTP_FROM_NAME` | Afzendernaam                                                | `Dashboard Deelmobiliteit` |

Secret aanmaken:

```bash
kubectl create secret generic smtp-password --from-literal=password='...'
```

De tabel `mailing` (zie `sql/admin.sql`) wordt bij het opstarten automatisch aangemaakt als deze nog niet bestaat.

Lokaal testen met een mail-catcher, bijvoorbeeld:

```bash
python -m aiosmtpd -n -l localhost:1025   # of: docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog
SMTP_HOST=localhost SMTP_PORT=1025 SMTP_SECURITY=none SMTP_FROM=info@dashboarddeelmobiliteit.nl uvicorn main:app --reload
```

# Feedbeheer

De `/feed/*` endpoints (alleen voor admins) beheren de tabel `feeds` die de importer (dd-importer-v2) gebruikt:

| Endpoint                          | Omschrijving                                                          |
|-----------------------------------|-----------------------------------------------------------------------|
| `GET /feed/list`                  | Alle feeds zonder credentials; query-waarden in de URL zijn gemaskeerd |
| `GET /feed/{feed_id}/credentials` | Volledige URL, authenticatie en request headers (wordt gelogd)        |
| `POST /feed/create`               | Nieuwe feed, altijd inactief                                          |
| `PUT /feed/update`                | Wijzigt alleen de meegestuurde velden; `system_id` en `data_type` liggen vast |
| `POST /feed/validate`             | Controleert een feed tegen MDS/GBFS via de feed validator             |
| `GET /feed/vehicle_types`         | Keuzes voor `default_vehicle_type`                                    |

Bij `/feed/validate` worden niet meegestuurde waarden (zoals ongewijzigde credentials) uit de opgeslagen feed gehaald.
De validator draait als aparte service in dd-importer-v2 (`cmd/feed_validator`). Benodigde environment variables:

| Variabele              | Omschrijving                                                      |
|------------------------|-------------------------------------------------------------------|
| `FEED_VALIDATOR_URL`   | Basis-URL van de validator, in k8s `http://feed-validator`        |
| `FEED_VALIDATOR_TOKEN` | Gedeeld geheim, in k8s via secret `feed-validator-token` (key `token`) |

Een validatie kan tot een minuut duren; de gateway-timeout voor `/admin` moet daarom minstens 70 seconden zijn.

Tests draaien (Python 3.11+):

```bash
pip install -r requirements.txt pytest
DB_NAME=test python -m pytest feed
```

# Building:
```bash
docker build -t ghcr.io/stichting-crow/dashboarddeelmobiliteit-od-matrix-aggregator:x.y .
docker push ghcr.io/stichting-crow/dashboarddeelmobiliteit-od-matrix-aggregator:x.y
```
