#!/usr/bin/env bash

flake8 server
isort server
vulture server
black --line-length 120 server