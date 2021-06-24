#!/usr/bin/python
"""
(C) 2015-2021 Lablup Inc.

This script receives codes.
It also stores them and run on the cloud.

NOTE: this code is super-simplified version of CodeOnWeb auto-grade feature, but modified to run without ingen server.

How to run: uvicorn receive_demo:app --reload

"""
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Header
import aiofiles
from datetime import datetime
from asyncio import create_subprocess_exec
import shlex
import os
app = FastAPI()
@app.post("/submit/")
async def create_upload_file(file: UploadFile = File(...), x_backendai_sender: Optional[str] = Header(None)):
    print(os.getcwd())
    print(x_backendai_sender)
    # You may need a gate here. Only accepting specific sender keys.
    now = datetime.now()
    date_signature = now.strftime("%Y%m%d%H%M%S")
    submitted_file_name = 'submit-'+x_backendai_sender+'-'+date_signature+'.zip'
    submitted_file_path = './store/'+submitted_file_name

    # Save and store the file in specific directory.
    async with aiofiles.open(submitted_file_path, 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk
    
    # Add your backend.ai CLI command here. This is an example.
    CLI_param = await CLI_parameter_generator(submitted_file_path, submitted_file_name)
    background_process = await create_subprocess_exec(*shlex.split(CLI_param))
    print(CLI_param) # In this example, we use raw Backend.AI CLI commands. You may change it with Backend.AI SDK
    await background_process.wait()
    return {"filename": file.filename}

async def CLI_parameter_generator(submitted_file_path: str, submitted_file_name: str):
    # This is just a basic parameter.
    # Change 'python' to your kernel name.
    return f'backend.ai run --rm -r cpu=2 -r mem=16G -r cuda.shares=4 -g lablup --exec "ls -l;unzip ./store/{submitted_file_name} -d .;cd code;python test.py" cr.backend.ai/cloud/python:3.8-ubuntu18.04 {submitted_file_path}'