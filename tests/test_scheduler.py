import ast
from pathlib import Path


def test_register_passes_sync_window_into_order_job() -> None:
    source = Path("app/scheduler/jobs.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    register_func = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "register"
    )

    sync_call = next(
        call
        for call in ast.walk(register_func)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "add_job"
        and call.args
        and isinstance(call.args[0], ast.Attribute)
        and call.args[0].attr == "sync_recent_orders"
    )

    kwargs_arg = next(
        kw.value for kw in sync_call.keywords if kw.arg == "kwargs"
    )

    assert isinstance(kwargs_arg, ast.Dict)
    assert [key.value for key in kwargs_arg.keys if isinstance(key, ast.Constant)] == [
        "minutes"
    ]
