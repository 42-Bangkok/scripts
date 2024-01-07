IMAGE_NAME = ft-cripts

default: build run

build:
	docker build -t $(IMAGE_NAME):latest .

run:
	docker run -it --rm --env-file .env $(IMAGE_NAME):latest

req:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

clean:
	-docker rmi $(IMAGE_NAME):latest
