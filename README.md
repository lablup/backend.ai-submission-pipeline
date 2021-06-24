# Backend.AI Code submission example

This code is an example of receiving a specific code from a user and making the code perform a specific operation on the backend.ai cluster.

Basically, this example is the simplest and most lightweight version of the ingen project (CodeOnWeb engine). 
You can create your own pipeline by adding or modifying your own implementations in the various parts.


## Setup

We use [poetry](https://github.com/python-poetry/poetry) to manage dependencies and packaging.
Poetry can be installed by the following command.

```shell
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
source ~/.poetry/env  # == export PATH="$HOME/.poetry/bin:$PATH"
```

Once poetry is installed, run the following to automatically populate a dedicated virtual
environment and all dependency packages:

```shell
poetry install
```


## Run the submission receiver sample

```shell
poetry run uvicorn --app-dir receiver receiver_demo:app
```


## Run the submission sender sample

```shell
poetry run submit
```
