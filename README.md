# Backend.AI Code submission example

This repository shows an example of receiving a specific code from a Backend.AI user and
running the code on the backend.ai cluster (for instance, to evaluate the result of submitted codes).

The structure of this repository follows a standard Backend.AI namespace package (`ai.backend.xxx`),
but each module (`evaluator` and `submit`) can be executed as a standalone script so that
the readers could just copy-and-paste the desired part of the sample code.

Basically, this example is the simplest and most lightweight version of the ingen project (CodeOnWeb engine). 
You can create your own pipeline by adding or modifying your own implementations in the various parts.


## Setup

We use [poetry](https://github.com/python-poetry/poetry) to manage dependencies and packaging.
Poetry can be installed by the following command.

```console
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
$ source ~/.poetry/env  # == export PATH="$HOME/.poetry/bin:$PATH"
```

Once poetry is installed, run the following to automatically populate a dedicated virtual
environment and all dependency packages:

```console
$ poetry install
```


## Run the submission evaluator sample

```shell
$ poetry run evaluator
```
or,
```console
$ poetry shell
$ python src/ai/backend/submission/evaluator.py
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
