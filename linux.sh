#!/bin/sh

CURRENT_UID=$(id -u):$(id -g) TARGET=${1} docker-compose up
