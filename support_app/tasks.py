"""Lifecycle management for QThread based worker tasks.

The backend used to keep a loose ``{task_name: {thread, worker}}`` dict and
tear threads down inline.  ``WorkerTask``/``TaskRunner`` make that lifecycle
explicit: one owner per task, idempotent cleanup and a single place that
connects progress/log/self-uninstall signals.
"""

from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import QThread

from support_app.logging_setup import get_logger

logger = get_logger(__name__)


class WorkerTask:
    """A worker and its thread, with idempotent Qt cleanup."""

    def __init__(
        self,
        name: str,
        thread: Any,
        worker: Any,
        finished_slot: Callable[..., Any],
    ) -> None:
        self.name = name
        self.thread = thread
        self.worker = worker
        self.finished_slot = finished_slot
        self._cleaned_up = False

    def dispatch_finished(self, result: tuple) -> None:
        """Invoke the task's completion slot with or without its payload."""
        if result:
            self.finished_slot(*result)
        else:
            self.finished_slot()

    def cleanup(self) -> None:
        """Stop the thread and schedule both objects for deletion once."""
        if self._cleaned_up:
            return
        self._cleaned_up = True

        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()


class TaskRunner:
    """Create, track and tear down worker threads for the backend."""

    def __init__(
        self,
        on_progress: Callable[..., Any],
        on_log: Callable[[str], Any],
        on_self_uninstall: Callable[[], Any],
    ) -> None:
        self._on_progress = on_progress
        self._on_log = on_log
        self._on_self_uninstall = on_self_uninstall
        self._tasks: dict[str, WorkerTask] = {}

    def start(
        self,
        task_name: str,
        worker_class: Any,
        start_method_name: str,
        finished_slot: Callable[..., Any],
        worker_args: tuple | None = None,
    ) -> None:
        """Instantiate *worker_class*, move it to a new thread and start it."""
        thread = QThread()
        worker = worker_class(*(worker_args or ()))
        worker.moveToThread(thread)

        thread.started.connect(getattr(worker, start_method_name))

        if hasattr(worker, "progress_changed"):
            worker.progress_changed.connect(self._on_progress)
        if hasattr(worker, "log"):
            worker.log.connect(self._on_log)
        if hasattr(worker, "selfUninstallTriggered"):
            worker.selfUninstallTriggered.connect(self._on_self_uninstall)

        worker.finished.connect(
            lambda *result: self._finish(task_name, result)
        )

        task = WorkerTask(task_name, thread, worker, finished_slot)
        self._tasks[task_name] = task
        logger.debug("Starting worker task %s", task_name)
        thread.start()

    def _finish(self, task_name: str, result: tuple) -> None:
        task = self._tasks.pop(task_name, None)
        if task is None:
            return

        try:
            task.dispatch_finished(result)
        finally:
            task.cleanup()
            logger.debug("Worker task %s finished", task_name)

    def active_task_names(self) -> tuple[str, ...]:
        """Names of tasks that have been started and not finished yet."""
        return tuple(self._tasks)
