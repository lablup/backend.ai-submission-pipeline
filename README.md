# Backend.AI Code submission example

This repository shows an example of receiving a specific code from a Backend.AI user and
running the code on the backend.ai cluster (for instance, to evaluate the result of submitted codes).

Basically, this example is the simplest and most lightweight version of the ingen project (CodeOnWeb engine). 
You can create your own pipeline by adding or modifying your own implementations in the various parts.


## Structure

The `submit` script collects and sends the compressed file of the "code" directory.
This script is supposed to be executed inside Backend.AI or similar online code-runner platforms
by the users who wants to "submit" the codes.

The `evaluator` modules runs a simple HTTP server that receives the submitted files,
executes them in isolated Backend.AI compute sessions, and checks the stdout results.
This module is supposed to be executed inside a web server by the users who wants to "evaluate" the
submitted codes.

The structure of this repository follows a standard Backend.AI namespace package (`ai.backend.xxx`),
but each module (`evaluator` and `submit`) can be executed as a standalone script so that
the readers could just copy-and-paste the desired part of the sample code.

To utilize this sample codes, you must adapt the CLI arguments and SDK function arguments in the codes
to fit with your setup marked with `FIXME`, as well as environment variables for your account keypairs, API endpoint, etc.


## Setup

We use [poetry](https://github.com/python-poetry/poetry) to manage dependencies and packaging.
Poetry can be installed by the following command.

Requires the client SDK environment variables to run.
The default service address is `http://127.0.0.1:8000`.

```console
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
$ source ~/.poetry/env  # == export PATH="$HOME/.poetry/bin:$PATH"
```

Once poetry is installed, run the following to automatically populate a dedicated virtual
environment and all dependency packages:

```console
$ poetry install
```


## Run the submission evaluator (based on CLI) sample

This evaluator invokes the `backend.ai` client CLI to execute user codes and get the result logs.
It downloads the whole container logs after execution, and this includes additional consoloe
logs of the container in addition to the output of user codes.

Requires the client SDK environment variables to run.
The default service address is `http://127.0.0.1:8000`.

```shell
$ poetry run evaluator-cli
```
or,
```console
$ poetry shell
$ python src/ai/backend/submission/evaluator_cli.py
```


## Run the submission evaluator (based on SDK) sample

This evaluator invokes the client SDK's functional API directly to execute user codes and get the
result logs.  It is more efficient because it does not have to download the stdout/stderr logs
twice and the stdout includes only the direct result of the given user code.

Requires the evaluator to be running and the user configures his/her identity as
`BACKENDAI_ACCESS_KEY` environment variable.
The default evaluator address is set to `http://127.0.0.1:8000` and users should
change this to match with their clusters.

```shell
$ poetry run evaluator-sdk
```
or,
```console
$ poetry shell
$ python src/ai/backend/submission/evaluator_sdk.py
```


## Run the submission sender sample

```console
$ poetry run submit
```
or,
```console
$ poetry shell
$ python src/ai/backend/submission/submit.py
```
