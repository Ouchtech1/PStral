from __future__ import annotations

from pathlib import Path


def test_demo_assets_do_not_contain_real_schema_or_secrets():
    assets = Path(__file__).resolve().parents[1] / "app" / "demo_assets"
    text = "\n".join(path.read_text(encoding="utf-8") for path in assets.rglob("*") if path.is_file())
    assert "PASSWORD" not in text.upper()
    assert "ORACLE_PASSWORD" not in text.upper()
    assert "CREATE USER" not in text.upper()


def test_frontend_message_renderer_does_not_inject_html_or_load_images():
    message_file = Path(__file__).resolve().parents[2] / "frontend" / "src" / "components" / "Chat" / "MessageBubble.jsx"
    text = message_file.read_text(encoding="utf-8")
    assert "dangerouslySetInnerHTML" not in text
    assert "skipHtml" in text
    assert "img()" in text
