import pytest

from support_app.tasks import TaskRunner, WorkerTask


class FakeThread:
    def __init__(self, running=True):
        self.running = running
        self.quit_calls = 0
        self.wait_calls = 0
        self.deleted = 0

    def isRunning(self):
        return self.running

    def quit(self):
        self.quit_calls += 1
        self.running = False

    def wait(self):
        self.wait_calls += 1

    def deleteLater(self):
        self.deleted += 1


class FakeWorker:
    def __init__(self):
        self.deleted = 0

    def deleteLater(self):
        self.deleted += 1


def make_task(slot=lambda *args: None):
    thread = FakeThread()
    worker = FakeWorker()
    return WorkerTask("demo", thread, worker, slot), thread, worker


def test_cleanup_is_idempotent():
    task, thread, worker = make_task()

    task.cleanup()
    task.cleanup()

    assert (thread.quit_calls, thread.wait_calls, thread.deleted) == (1, 1, 1)
    assert worker.deleted == 1


def test_cleanup_skips_stop_for_finished_thread():
    task, thread, _ = make_task()
    thread.running = False

    task.cleanup()

    assert thread.quit_calls == 0
    assert thread.deleted == 1


def test_dispatch_finished_with_payload():
    received = []
    task, _, _ = make_task(lambda payload: received.append(payload))

    task.dispatch_finished(({"rust_id": "123"},))

    assert received == [{"rust_id": "123"}]


def test_dispatch_finished_without_payload():
    calls = []
    task, _, _ = make_task(lambda: calls.append("done"))

    task.dispatch_finished(())

    assert calls == ["done"]


def test_task_runner_finishes_and_cleans_up():
    runner = TaskRunner(lambda *a: None, lambda *a: None, lambda: None)
    task, thread, worker = make_task()
    runner._tasks[task.name] = task

    runner._finish(task.name, ())

    assert runner.active_task_names() == ()
    assert thread.deleted == 1
    assert worker.deleted == 1


def test_task_runner_cleans_up_when_slot_raises():
    def boom():
        raise RuntimeError("slot failed")

    runner = TaskRunner(lambda *a: None, lambda *a: None, lambda: None)
    task, thread, worker = make_task(boom)
    runner._tasks[task.name] = task

    with pytest.raises(RuntimeError):
        runner._finish(task.name, ())

    assert runner.active_task_names() == ()
    assert thread.deleted == 1
    assert worker.deleted == 1


def test_task_runner_ignores_unknown_task():
    runner = TaskRunner(lambda *a: None, lambda *a: None, lambda: None)

    runner._finish("missing", ())  # must not raise

    assert runner.active_task_names() == ()


def test_task_runner_rejects_duplicate_task():
    runner = TaskRunner(lambda *a: None, lambda *a: None, lambda: None)
    task, _, _ = make_task()
    runner._tasks[task.name] = task

    started = runner.start(task.name, None, "run", lambda: None)

    assert started is False
    assert runner.is_running(task.name) is True


def test_invoke_runs_worker_method():
    calls = []

    class Worker:
        def run(self):
            calls.append("ran")

    runner = TaskRunner(lambda *a: None, lambda *a: None, lambda: None)

    runner._invoke("demo", Worker(), "run")

    assert calls == ["ran"]


def test_invoke_cleans_up_and_reports_failure():
    errors = []

    class Worker:
        def run(self):
            raise RuntimeError("boom")

    runner = TaskRunner(
        lambda *a: None,
        lambda *a: None,
        lambda: None,
        on_task_error=lambda name, error: errors.append((name, str(error))),
    )
    task, thread, worker = make_task()
    runner._tasks[task.name] = task

    runner._invoke(task.name, Worker(), "run")

    assert runner.active_task_names() == ()
    assert thread.deleted == 1
    assert worker.deleted == 1
    assert errors == [("demo", "boom")]
