Create WebApp preview and import preloaded data:
```
docker-compose up -d --build
docker-compose exec backend flask import-data ./parse_results
```
Available at: ```http://localhost:3000/```


Command for parsing data (optionally save to database or .json file):
```
docker-compose exec backend flask launch-parser --help
```
Command for importing parsed data to database:
```
docker-compose exec backend flask import-data --help
```
