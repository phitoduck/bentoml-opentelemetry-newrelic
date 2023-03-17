install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dummy-api-deps:
	pip install pydantic

build:
	bentoml build .

containerize:
	bentoml containerize dummy_service:latest \
		--docker-image-tag dummy-service:latest \
		--opt platform=linux/amd64

serve:
	bentoml serve .

serve-docker:
	docker run -it --rm -p 3000:3000 dummy-service:latest serve --production