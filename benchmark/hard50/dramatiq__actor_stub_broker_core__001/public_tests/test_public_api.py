from __future__ import annotations

from featurelifted import Middleware, StubBroker, actor, get_broker, set_broker


class Probe(Middleware):
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def before_enqueue(self, broker, message, delay) -> None:
        self.events.append(("before", message.actor_name))

    def after_enqueue(self, broker, message, delay) -> None:
        self.events.append(("after", message.actor_name))


def test_send_enqueues_on_stub_broker() -> None:
    broker = StubBroker()
    set_broker(broker)

    @actor(max_retries=0)
    def ping(value: int) -> int:
        return value

    message = ping.send(3)
    assert message.actor_name == "ping"
    assert message.args == (3,)
    assert get_broker() is broker


def test_middleware_before_and_after_enqueue() -> None:
    broker = StubBroker()
    probe = Probe()
    broker.add_middleware(probe)
    set_broker(broker)

    @actor(max_retries=0)
    def echo(value: str) -> str:
        return value

    echo.send("hi")
    assert probe.events == [("before", "echo"), ("after", "echo")]
