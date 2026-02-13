import ast
from pathlib import Path


def test_factory_supports_browser_rpa_mode() -> None:
    source = Path("app/channels/factory.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert "browser_rpa" in source

    build_func = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "build_channel"
    )
    returns = [n for n in ast.walk(build_func) if isinstance(n, ast.Return)]

    assert len(returns) >= 2


def test_readme_mentions_no_unauthorized_packet_capture() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "不建议、也不支持未授权抓包" in readme
