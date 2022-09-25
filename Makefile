run:
	docker-compose up -d --force-recreate

build:
	docker-compose build --no-cache

exec:
	docker-compose exec web /bin/bash

logs:
	docker-compose logs -f web

restart:
	docker-compose restart web

stop:
	docker-compose stop
