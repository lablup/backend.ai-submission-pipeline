"""
(C) 2015-2021 Lablup Inc.

Backend.AI Code Evaluator Example
=================================

Accept code submissions, stores them into the "store" directory in the current working directory,
and run the submission on the Backend.AI cloud.

NOTE: This code is super-simplified version of CodeOnWeb auto-grade feature,
      but modified to run without ingen server.
"""

from datetime import datetime
import getpass
import io
import json
import logging
import os
from pathlib import Path
import secrets
from typing import Any, Literal, Optional

import aiofiles
import aiohttp
from fastapi import FastAPI, File, UploadFile, Header
import uvicorn

from ai.backend.client.session import AsyncSession
from ai.backend.client.func.session import ComputeSession

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

    session_name = f"eval-{secrets.token_urlsafe(16)}"
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    reply = {"filename": file.filename}

    # This is an SDK API usage example to run an upload file on Backend.AI.
    async with AsyncSession() as session:
        log.info("run[%s]: Preparing compute session for evaluation...", run_id)
        compute_session = await session.ComputeSession.get_or_create(
            # FIXME: The image name
            "cr.backend.ai/cloud/python:3.8-ubuntu18.04",
            name=session_name,
            type_="interactive",
            domain_name="default",
            # FIXME: The project name you belongs to.
            group_name="lablup",
            # FIXME: Specify the resource amounts to evalute the submission.
            resources={
                'cpu': '2',
                'mem': '16G',
                'cuda.shares': '4',
            },
        )
        if compute_session.status == 'RUNNING':
            if compute_session.created:
                log.debug("run[%s]: The session is created.", run_id)
            else:
                log.debug("run[%s]: The session is ready.", run_id)
        elif compute_session.status == 'TERMINATED':
            log.error("run[%s]: The session has terminated too early.", run_id)
            return reply
        elif compute_session.status in ('ERROR', 'CANCELLED'):
            log.error("run[%s]: The session was cancelled or got error during startup.", run_id)
            return reply
        try:
            ret = await compute_session.upload([submitted_file_path], basedir=None)
            if ret.status // 100 != 2:
                log.error("run[%s]: Failed to upload the submission file", run_id)
                return reply

            opts = {
                'clean': None,
                'build': f"unzip {submitted_file_path} -d .; "
                         f"pip install --user -r ./requirements_test.txt",
                'exec': "cd code; python test.py",
            }
            log.info("run[%s]: Executing user code...", run_id)
            build_exit_code, exec_exit_code, clean_exit_code = await exec_loop(
                stdout_buf,
                stderr_buf,
                compute_session,
                'batch', '',
                opts=opts,
            )
            log.info("run[%s]: Exit codes of build/exec/clean commands: %d, %d, %d",
                     run_id, build_exit_code, exec_exit_code, clean_exit_code)
            # Note: You may also check the process exit code of build/exec commands.
        finally:
            await compute_session.destroy()

    # Check the stdout log.
    try:
        stdout = stdout_buf.getvalue()
        check_result(stdout)
    except AssertionError as e:
        log.info("run[%s]: Result check failed! (error: %r)", run_id, e)

    return reply


async def exec_loop(
    stdout: io.StringIO,
    stderr: io.StringIO,
    compute_session: ComputeSession,
    mode: Literal['batch', 'query'],
    code: Optional[str],
    opts: dict[str, Any],
) -> tuple[int, int, int]:
    # A minimal version of handling the query/batch code execution API
    build_exit_code = -1
    exec_exit_code = -1
    clean_exit_code = -1
    async with compute_session.stream_execute(code, mode=mode, opts=opts) as stream:
        async for result in stream:
            if result.type == aiohttp.WSMsgType.TEXT:
                result = json.loads(result.data)
            else:
                # future extension
                continue
            for rec in result.get('console', []):
                if rec[0] == 'stdout':
                    print(rec[1], end='', file=stdout)
                elif rec[0] == 'stderr':
                    print(rec[1], end='', file=stderr)
                else:
                    print('----- output record (type: {0}) -----'.format(rec[0]),
                          file=stdout)
                    print(rec[1], file=stdout)
                    print('----- end of record -----', file=stdout)
            stdout.flush()
            files = result.get('files', [])
            if files:
                print('--- generated files ---', file=stdout)
                for item in files:
                    print('{0}: {1}'.format(item['name'], item['url']), file=stdout)
                print('--- end of generated files ---', file=stdout)
            if result['status'] == 'clean-finished':
                clean_exit_code = result.get('exitCode')
            elif result['status'] == 'build-finished':
                build_exit_code = result.get('exitCode')
            elif result['status'] == 'finished':
                exec_exit_code = result.get('exitCode')
                break
            elif result['status'] == 'waiting-input':
                if result['options'].get('is_password', False):
                    code = getpass.getpass()
                else:
                    code = input()
                await stream.send_str(code)
            elif result['status'] == 'continued':
                pass
    return build_exit_code, exec_exit_code, clean_exit_code


def check_result(stdout: str):
    assert "Hello Backend.AI!" in stdout


def main():
    logging.config.dictConfig(log_config)
    # FIXME: put your host and port
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level="info")


if __name__ == "__main__":
    main()
