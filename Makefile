start:
	scripts/cs_launch.sh

clean:
	docker-compose kill
	docker-compose rm
