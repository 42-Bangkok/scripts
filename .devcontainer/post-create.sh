#! /bin/bash

PRE='export $(cat '
POST='/.env | xargs)'
CMD=$PRE$1$POST
echo $CMD >> ~/.bashrc

poetry install
