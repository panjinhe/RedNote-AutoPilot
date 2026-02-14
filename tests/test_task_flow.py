from app.ai_engine.content_generator import AIContentGenerator
from app.channels.device_auto import DeviceAutoChannel
from app.models.schemas import ProductCreate, TaskStatus
from app.product_manager.service import ProductManager
from app.tasks.executor import ListingTaskExecutor
from app.tasks.repository import TaskRepository


def test_auto_create_product_executes_and_persists_task(tmp_path) -> None:
    repo = TaskRepository(str(tmp_path / "autopilot.db"))
    channel = DeviceAutoChannel(device_id="test-device")
    executor = ListingTaskExecutor(channel=channel, repo=repo)
    manager = ProductManager(
        channel=channel,
        ai_generator=AIContentGenerator(),
        task_repo=repo,
        task_executor=executor,
        operation_mode="auto_device",
    )

    output = manager.auto_create_product(
        ProductCreate(
            title="便携风扇",
            cost_price=19.9,
            sale_price=39.9,
            category="3C数码",
            keywords=["静音", "续航"],
        )
    )

    task = output["task"]
    assert task["status"] == TaskStatus.done.value
    assert task["output"]["create"]["success"] is True

    loaded = repo.get_task(task["task_id"])
    assert loaded is not None
    assert loaded.status == TaskStatus.done
