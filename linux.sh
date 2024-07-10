#!/bin/sh

CURRENT_UID=$(id -u):$(id -g) TARGET=${1} GITTRG=${2} docker compose up
