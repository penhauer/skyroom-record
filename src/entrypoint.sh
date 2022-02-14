#!/bin/bash

Xvfb :99 -screen 0 1920x1080x24 &

touch ~/.Xauthority

flask run -h 0.0.0.0 -p 5000 &

while test $# != 0
do
    case "$1" in
    --single) single=t ;;
		*)	all="${all} ${1}" ;;
    esac
		shift
done


if [[ $single == "t" ]]; then
	python3 main.py $all
else
	echo "" > cron-tabs.tab
fi
