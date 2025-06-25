"""Module executed via `python -m extracttext.server`.
Starts the FastAPI dev server on port 6060.
"""
from . import _run_dev_server

if __name__ == "__main__":
    _run_dev_server() 