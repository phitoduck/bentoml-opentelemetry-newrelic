from fastapi import FastAPI, Depends, HTTPException, Request
import os
import httpx
import logging
import asyncio
from urllib.parse import urlparse
import json

from opentelemetry import trace
from opentelemetry.sdk.metrics import MeterProvider

# Setting up logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Set up tracing
# trace.set_tracer_provider(TracerProvider())
TRACER = trace.get_tracer(__name__)
# trace.get_tracer_provider().add_span_processor(
#     SimpleSpanProcessor(ConsoleSpanExporter())
# )

# Set up metrics
METRICS = MeterProvider().get_meter(__name__)

ERRORS_COUNTER = METRICS.create_counter(
    "errors",
    description="Number of errors occurred",
    unit="1",
)

APP = FastAPI(docs_url="/")

# Getting the DOWNSTREAM_API_TARGETS
DOWNSTREAM_API_TARGETS = os.environ.get("DOWNSTREAM_API_TARGETS", "").split(",")
DOWNSTREAM_HTTP_REQUEST_METHOD = os.environ.get("DOWNSTREAM_HTTP_REQUEST_METHOD", "GET")
DOWNSTREAM_HTTP_REQUEST_BODY = json.loads(os.environ.get("DOWNSTREAM_HTTP_REQUEST_BODY", ""))


@APP.get("/echo")
async def echo(message: str, request: Request):
    # with TRACER.start_as_current_span("echo"):

    HISTOGRAM = MeterProvider().get_meter(__name__).create_histogram(
        "some.prefix.eric_http_request_duration_custom",
        description="Time taken for each request",
        unit="ms",
    )

    LOGGER.info(f"Received message: {message}")
    ERRORS_COUNTER.add(1)

    if not DOWNSTREAM_API_TARGETS or DOWNSTREAM_API_TARGETS == [""]:
        return {"data": {"message": message}}

    responses = await asyncio.gather(*[fetch(url) for url in DOWNSTREAM_API_TARGETS])

    for response in responses:
        duration = response["response"].get("duration", 0)
        HISTOGRAM.record(duration, {"path": request.url.path})
        LOGGER.info(f"URL: {response['url']}, Response: {response['response']}")

    return {"data": responses}


@APP.get("/error")
async def error(message: str):
    try:
        raise Exception(message)
    except Exception as e:
        span = TRACER.start_span("error_handling")
        span.record_exception(e)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        span.end()
        ERRORS_COUNTER.add(1)
        LOGGER.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def get_request_path(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.path


async def fetch(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        for i in range(10):
            print("content", DOWNSTREAM_HTTP_REQUEST_BODY)
        resp = await client.request(
            method=DOWNSTREAM_HTTP_REQUEST_METHOD,
            url=url,
            json=DOWNSTREAM_HTTP_REQUEST_BODY,
        )
        resp_data = resp.json()
        return {
            "url": url,
            "response": resp_data,
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(APP, host="0.0.0.0", port=8000)
