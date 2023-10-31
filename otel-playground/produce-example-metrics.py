#!/usr/bin/env python3

import time
import random
import threading
import logging
from typing import Iterable

from opentelemetry import metrics
from opentelemetry.sdk.metrics import Histogram
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.view import View, ExplicitBucketHistogramAggregation

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO


exponential_boundaries_view = View(
    # meter_name="github.com/uptrace/uptrace-python",
    # instrument_name="some.prefix.histogram",
    aggregation=ExplicitBucketHistogramAggregation(boundaries=[2, 4, 6, 8, 10], record_min_max=True),
    instrument_type=Histogram
)

# Warning - Overriding of current MeterProvider is not allowed; you can
# only override the singleton MeterProvider once.
metrics.set_meter_provider(
    MeterProvider(
        views=[exponential_boundaries_view],
    )
)
METER = metrics.get_meter("github.com/uptrace/uptrace-python", "1.0.0")
HISTOGRAM = METER.create_histogram(
    "some.prefix.histogram",
    description="TODO",
    unit="microseconds",
)



# ExponentialBucketHistogramAggregation is a thing. You can do powers of 2.

def counter():
    counter = METER.create_counter("some.prefix.counter", description="TODO")

    # while True:
    #     counter.add(1)
    #     logging.info("Counter incremented by 1")
    #     time.sleep(1)


def up_down_counter():
    counter = METER.create_up_down_counter(
        "some.prefix.up_down_counter", description="TODO"
    )

    # while True:
    if random.random() >= 0.5:
        counter.add(+1)
        logging.info("Up-down counter incremented by 1")
    else:
        counter.add(-1)
        logging.info("Up-down counter decremented by 1")
    # time.sleep(1)


def histogram():


    # for i in range(100):
    #     value = random.randint(1, 5000000)
    #     histogram.record(value, attributes={"attr1": "value1"})
    #     logging.info(f"Histogram recorded with value: {value}")

    for i in range(10_000):
        # sample a value from a normal distribution
        value = random.normalvariate(100, 5)
        HISTOGRAM.record(value, attributes={"attr1": "value1"})


def counter_observer():
    number = 0

    def callback(options: CallbackOptions) -> Iterable[Observation]:
        nonlocal number
        number += 1
        logging.info(f"Counter observer callback incremented number to: {number}")
        yield Observation(int(number), {})

    counter = METER.create_observable_counter(
        "some.prefix.counter_observer", [callback], description="TODO"
    )


def up_down_counter_observer():
    def callback(options: CallbackOptions) -> Iterable[Observation]:
        value = random.random()
        logging.info(f"Up-down counter observer callback yielded value: {value}")
        yield Observation(value, {})

    counter = METER.create_observable_up_down_counter(
        "some.prefix.up_down_counter_observer",
        [callback],
        description="TODO",
    )


def gauge_observer():
    def callback(options: CallbackOptions) -> Iterable[Observation]:
        value = random.random()
        logging.info(f"Gauge observer callback yielded value: {value}")
        yield Observation(value, {})

    gauge = METER.create_observable_gauge(
        "some.prefix.gauge_observer",
        [callback],
        description="TODO",
    )


def main():

    # threading.Thread(target=counter).start()
    # threading.Thread(target=up_down_counter).start()
    threading.Thread(target=histogram).start()

    # counter_observer()
    # up_down_counter_observer()
    # gauge_observer()

    print("reporting measurements to Otel-collector... (press Ctrl+C to stop)")
    # time.sleep(300)


if __name__ == "__main__":
    main()
