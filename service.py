import time
import numpy as np
import bentoml
from typing import Any, List, Tuple, Union
from bentoml.io import JSON
from pydantic import BaseModel
from numpy.typing import NDArray


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
        print("input data", type(input_data))
        print("input data", input_data)
        # return ["image1", 0.11], ["image2", 0.22]
        return [[f"image{i}", 0.11 * i] for i, _ in enumerate(input_data)]


example_runner = bentoml.Runner(
    models=[],
    runnable_class=ExampleRunnable,
    name="example_runner",
    max_latency_ms=100_000,
    max_batch_size=10,
)

svc = bentoml.Service("dummy_service", runners=[example_runner])


@svc.api(
    route="/predict",
    input=JSON(pydantic_model=PredictRequest),
    output=JSON(pydantic_model=PredictResponse),
)
def predict(input: PredictRequest) -> np.ndarray:
    time.sleep(2)
    result: int = example_runner.run(
        [input.input],
    )
    print("RESULT", result)
    return PredictResponse(
        output=result[0],
    )
