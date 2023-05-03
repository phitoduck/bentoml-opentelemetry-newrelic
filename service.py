import time
import numpy as np
import bentoml
from typing import Any, List, Tuple, Union, Callable
from bentoml.io import JSON
from pydantic import BaseModel
from numpy.typing import NDArray
import os
import functools
import traceback


from logging import getLogger

LOGGER = getLogger(__name__)
NEW_RELIC_APP_NAME = os.environ["NEW_RELIC_APP_NAME"]


class PredictRequest(BaseModel):
    input: int


class PredictResponse(BaseModel):
    output: Tuple[str, float]


class ExampleRunnable(bentoml.Runnable):
    SUPPORTED_RESOURCES = ("cpu",)
    SUPPORTS_CPU_MULTI_THREADING = True

    @bentoml.Runnable.method(
        batchable=True,
        batch_dim=0,
    )
    def generate_image_overlayed_with_heatmap(
        self,
        input_data: List[int],
    ) -> List[Tuple[str, float]]:
        LOGGER.info("input data %s", type(input_data))
        LOGGER.info("input data %s", input_data)
        # return ["image1", 0.11], ["image2", 0.22]
        return [[f"image{i}", 0.11 * i] for i, _ in enumerate(input_data)]


example_runner = bentoml.Runner(
    models=[],
    runnable_class=ExampleRunnable,
    name="example_runner",
    max_latency_ms=100_000,
    max_batch_size=10,
)

svc = bentoml.Service(NEW_RELIC_APP_NAME, runners=[example_runner])


def log_traceback_asgi_route(func: Callable) -> Callable:
    """
    Handle exception in `func` by logging a traceback and re-raising the exception.

    This method allows the traceback log to be decorated by OpenTelemetry middleware.
    For example, the trace and span ID generated by BentoML will be present.
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as err:
            stack_trace: str = traceback.format_exc()
            LOGGER.error(stack_trace, exc_info=True)
            raise err

    return wrapper


@svc.api(
    route="/predict",
    input=JSON(pydantic_model=PredictRequest),
    output=JSON(pydantic_model=PredictResponse),
)
@log_traceback_asgi_route
def predict(input: PredictRequest) -> np.ndarray:
    """Simulate running a prediction."""
    time.sleep(1)
    result: int = example_runner.run(
        [input.input],
    )
    LOGGER.info("RESULT %s", result)

    return PredictResponse(
        output=result[0],
    )


@svc.api(
    route="/error",
    input=JSON(pydantic_model=PredictRequest),
    output=JSON(pydantic_model=PredictResponse),
)
@log_traceback_asgi_route
def error(input: PredictRequest) -> PredictResponse:
    """Raise an exception.

    The traceback should be logged and appropriated decorated with trace and span IDs.

    Trying markdown formatting

    - list item 1
    - list item 2
        - nested list item 1
    """
    result: int = example_runner.run([input.input])
    LOGGER.info("RESULT %s", result)

    raise Exception("Error")
