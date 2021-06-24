"""
(C) 2015-2021 Lablup Inc.

Backend.AI Code Evaluator Example
=================================

Accept code submissions, stores them into the "store" directory in the current working directory,
and run the submission on the Backend.AI cloud.

NOTE: This code is super-simplified version of CodeOnWeb auto-grade feature,
      but modified to run without ingen server.
"""

import asyncio
from datetime import datetime
import logging
import os
from pathlib import Path
import secrets
from typing import Optional, Union

import aiofiles
from fastapi import FastAPI, File, UploadFile, Header
import uvicorn

from ai.backend.submission.logging import log_config

app = FastAPI()
log = logging.getLogger(__name__)


if 'BACKEND_ACCESS_KEY' not in os.environ:
    raise RuntimeError("Specify BACKEND_ACCESS_KEY environment variable for the evaluator account.")
if 'BACKEND_SECRET_KEY' not in os.environ:
    raise RuntimeError("Specify BACKEND_SECRET_KEY environment variable for the evaluator account.")


@app.post("/submit/")
async def create_upload_file(
    file: UploadFile = File(...),
    x_backendai_sender: Optional[str] = Header(None),
):
    run_id = f"submission-{secrets.token_hex(8)}"
    log.info("run[%s]: Received submission from %s", run_id, x_backendai_sender)
    # You may need a gate here. Only accepting specific sender keys.
    now = datetime.now()
    date_signature = now.strftime("%Y%m%d%H%M%S")
    submitted_file_name = f"submit-{x_backendai_sender}-{date_signature}.zip"
    submitted_file_path = Path("./store") / submitted_file_name

    # Save and store the file in specific directory.
    async with aiofiles.open(submitted_file_path, "wb") as out_file:
        while chunk := await file.read(1024):
            await out_file.write(chunk)

    # Add your backend.ai CLI command here. This is an example.
    log.info("run[%s]: Running a compute session for evaluation...", run_id)
    session_name = f"eval-{secrets.token_urlsafe(16)}"
    cmdargs = get_run_cmd(session_name, submitted_file_path)
    proc = await asyncio.create_subprocess_exec(
        *cmdargs,
    )
    await proc.wait()

    cmdargs = get_log_cmd(session_name)
    proc = await asyncio.create_subprocess_exec(
        *cmdargs,
        stdout=asyncio.subprocess.PIPE,
        stderr=None,
    )
    stdout_bufs = []
    assert proc.stdout is not None
    while chunk := await proc.stdout.read(1024):
        stdout_bufs.append(chunk.decode('utf8'))
    await proc.wait()
    stdout = ''.join(stdout_bufs)

    # Check the stdout log.
    try:
        check_result(stdout)
    except AssertionError as e:
        log.info("run[%s]: Result check failed! (error: %r)", run_id, e)

    return {"filename": file.filename}


def get_run_cmd(
    session_name: str,
    submitted_file_path: Path,
) -> list[Union[str, Path]]:
    return [
        # The Backend.AI Client SDK CLI.
        "backend.ai",
        # run: create session, upload files, and run the given execution command.
        "run",
        # The session name to use.
        "-t", session_name,
        # Auto-terminate after execution finishes.
        "--rm",
        # FIXME: Specify the resource amounts to evalute the submission.
        "-r", "cpu=2",
        "-r", "mem=16G",
        "-r", "cuda.shares=4",
        # FIXME: The project name you belongs to.
        "-g", "lablup",
        # The install command to install dependencies of the submission.
        # The uploaded path inside container follows the relative path to the current working
        # directory of the client and this submission script.
        "--build", f"unzip {submitted_file_path} -d .; "
                   f"pip install --user -r ./requirements_test.txt",
        # The execution command to evalute the submission.
        "--exec", "cd code; python test.py",
        # FIXME: The image name
        "cr.backend.ai/cloud/python:3.8-ubuntu18.04",
        # The uploaded file(s)
        submitted_file_path,
    ]


def get_log_cmd(session_name: str):
    return [
        "backend.ai",
        "logs",
        session_name,
    ]


def check_result(stdout: str):
    assert "Hello Backend.AI!" in stdout


def main():
    logging.config.dictConfig(log_config)
    # FIXME: put your host and port
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level="info")


if __name__ == "__main__":
    main()
