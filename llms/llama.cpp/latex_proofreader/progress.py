from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from contextlib import contextmanager
import time

class ProgressManager:
    def __init__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            transient=True,
        )
        self.level = 0

    def __enter__(self):
        self.progress.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.progress.__exit__(exc_type, exc, tb)

    @contextmanager
    def task(self, description: str):
        indent = "  " * self.level
        task_id = self.progress.add_task(f"{indent}{description}...", total=None)

        self.level += 1
        start = time.perf_counter()

        try:
            yield
            self.progress.stop_task(task_id)
        finally:
            self.level -= 1
            elapsed = time.perf_counter() - start
            self.progress.update(
                task_id,
                description=f"{indent}✔ {description} ({elapsed:.2f}s)"
            )
