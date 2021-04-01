#!/bin/sh

export SECRET_KEY=secretkey
export FLASK_ENV=development
export FLASK_RUN_PORT=8000
export FLASK_RUN_HOST=127.0.0.1

export FLASK_APP=webferea

flask run