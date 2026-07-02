"""
Modal deployment for NetPath.

Deploy with: uv run modal deploy modal_deploy.py
This gives you a public URL like: https://<you>--netpath-web.modal.run
"""

from pathlib import Path
import modal

app = modal.App("netpath")
local_dir = Path(__file__).parent

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("fastapi", "uvicorn", "pydantic")
    .add_local_dir(local_dir, remote_path="/root")
)


@app.function(image=image, timeout=300)
@modal.concurrent(max_inputs=20)
@modal.asgi_app()
def web():
    import sys
    sys.path.insert(0, "/root")
    from api.service import app as fastapi_app
    return fastapi_app
