from macrobot_action_gateway.api_types import ResourceId
from macrobot_action_gateway.resource_manager import ResourceManager


def test_atomic_acquire_and_release():
    manager = ResourceManager()
    assert manager.acquire("a", [ResourceId.BASE_MOTION, ResourceId.PICO_MOTION])
    assert not manager.acquire("b", [ResourceId.PICO_MOTION])
    assert manager.owner(ResourceId.BASE_MOTION) == "a"
    manager.release("a")
    assert manager.acquire("b", [ResourceId.PICO_MOTION])
