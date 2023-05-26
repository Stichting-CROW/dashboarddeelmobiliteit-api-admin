# dashboarddeelmobiliteit-api-admin
Een API voor gebruikers-, organisatie- en financieel beheer voor het Dashboard Deelmobiliteit

# ssh tunnels
```bash
ssh -L 5433:10.133.75.95:5432 root@auth.deelfietsdashboard.nl
```

# Building:
```bash
docker build -t ghcr.io/stichting-crow/dashboarddeelmobiliteit-od-matrix-aggregator:x.y .
docker push ghcr.io/stichting-crow/dashboarddeelmobiliteit-od-matrix-aggregator:x.y
```
