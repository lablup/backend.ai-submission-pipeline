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
from typing import Optional, Union

import aiofiles
from fastapi import FastAPI, File, UploadFile, Header
import uvicorn

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
    log.info("Received submission from %s", x_backendai_sender)
    # You may need a gate here. Only accepting specific sender keys.
    now = datetime.now()
    date_signature = now.strftime("%Y%m%d%H%M%S")
    submitted_file_name = f"submit-{x_backendai_sender}-{date_signature}.zip"
    submitted_file_path = Path("./store") / submitted_file_name

    # Save and store the file in specific directory.
    async with aiofiles.open(submitted_file_path, "wb") as out_file:
        while content := await file.read(1024):
            await out_file.write(content)

    # Add your backend.ai CLI command here. This is an example.
    cmdargs = await get_run_cmd(submitted_file_path)
    background_process = await asyncio.create_subprocess_exec(*cmdargs)
    await background_process.wait()

    return {"filename": file.filename}


async def get_run_cmd(
    submitted_file_path: Path,
) -> list[Union[str, Path]]:
    return [
        # The Backend.AI Client SDK CLI.
        "backend.ai"
        # run: create session, upload files, and run the given execution command.
        "run",
        # Auto-terminate after execution finishes.
        "--rm"
        # Specify the resource amounts to evalute the submission.
        "-r", "cpu=2",
        "-r", "mem=16G",
        "-r", "cuda.shares=4",
        # The project name you belongs to.
        "-g", "lablup",
        # The execution command to evalute the submission.
        # The uploaded path inside container follows the relative path to the current working
        # directory of the client and this submission script.
        "--exec", f"unzip {submitted_file_path} -d .; cd code; python test.py",
        # The image name
        "cr.backend.ai/cloud/python:3.8-ubuntu18.04",
        # The uploaded file(s)
        submitted_file_path,
    ]


def main():
    uvicorn.run(app, log_level="info")


if __name__ == "__main__":
    main()
