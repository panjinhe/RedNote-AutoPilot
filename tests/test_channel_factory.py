import ast
from pathlib import Path


def test_factory_uses_browser_channel_only() -> None:
    source = Path("app/channels/factory.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert "BrowserRPAChannel" in source

    build_func = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "build_channel"
    )
    returns = [n for n in ast.walk(build_func) if isinstance(n, ast.Return)]

    assert len(returns) == 1


def test_readme_mentions_pure_browser_assistant() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "纯浏览器" in readme
