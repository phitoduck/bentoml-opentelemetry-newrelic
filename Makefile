install:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt

install-dummy-api-deps:
	python3 -m pip install pydantic

build-bento:
	cd ./bentoml-app/ \
	&& NEW_RELIC_APP_NAME=dummy-bento-service \
		python3 -m bentoml build ./

containerize:
	cd ./bentoml-app/ \
	&& NEW_RELIC_APP_NAME=dummy-bento-service \
	python3 -m bentoml containerize dummy-bento-service:latest \
		--docker-image-tag dummy-bento-service:latest \
		--opt platform=linux/amd64

serve:
	python3 -m bentoml serve .

pull-adot-image:
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
	docker pull public.ecr.aws/aws-observability/aws-otel-collector:latest


serve-docker:
	docker run -it --rm -p 3000:3000 --env-file=.env dummy-bento-service:latest serve --production