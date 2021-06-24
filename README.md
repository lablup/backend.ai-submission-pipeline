# Backend.AI Code submission example

This code is an example of receiving a specific code from a user and making the code perform a specific operation on the backend.ai cluster.

Basically, this example is the simplest and most lightweight version of the ingen project (CodeOnWeb engine). 
You can create your own pipeline by adding or modifying your own implementations in the various parts.


## Setup build environment

We use [poetry](https://github.com/python-poetry/poetry) to manage dependencies and packaging. Poetry can be installed by the following command.

```shell
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
source ~/.poetry/env  # == export PATH="$HOME/.poetry/bin:$PATH"
```

We also recommend to use virtualenv to separate dependencies. After activating the virtualenv, run following command to install dependencies.

```shell
poetry install
```


## Run the receive server

```shell
poetry run uvicorn --app-dir receiver receiver_demo:app
```


## Run the sender

```shell
poetry run submit
```
