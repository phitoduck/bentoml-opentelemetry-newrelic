install:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt

install-dummy-api-deps:
	python3 -m pip install pydantic

build:
	python3 -m bentoml build .

containerize:
	python3 -m bentoml containerize dummy_service:latest \
		--docker-image-tag dummy-service:latest \
		--opt platform=linux/amd64

serve:
	python3 -m bentoml serve .

serve-docker:
	docker run -it --rm -p 3000:3000 --env-file=.env dummy-service:latest serve --production