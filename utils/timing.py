import time
from contextlib import contextmanager, nullcontext


class StageTimer:
    def __init__(self):
        self.stages: dict[str, float] = {}
        self.info: dict[str, object] = {}

    @contextmanager
    def measure(self, stage_name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            self.stages[stage_name] = round(time.perf_counter() - start, 3)

    def total(self) -> float:
        return round(sum(self.stages.values()), 3)


def measure(timer: StageTimer | None, stage_name: str):
    """Đo thời gian nếu có timer, ngược lại không làm gì."""
    return timer.measure(stage_name) if timer else nullcontext()
