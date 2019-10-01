#!/bin/sh

CURRENT_UID=$(id -u):$(id -g) DZGITLOC=${1} DZSUBDIR=${2} docker-compose up
