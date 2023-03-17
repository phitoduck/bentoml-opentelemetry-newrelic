# BentoML-OpenTelemetry-NewRelic Example

Usage:

1. Create a `.env` file in the root of this repo with a single variable called `NEW_RELIC_LICENSE_KEY`
2. Build and run the bento service

```bash
# create and activate a Python virtual environment
python -m venv ./venv/
source ./venv/bin/activate

# build the REST API container
make install install-dummy-api-deps build containerize

# run
docker-compose up
```

3. Visit `http://localhost:3000` and trigger a request to the API