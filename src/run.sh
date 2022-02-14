docker run --detach --mount type=bind,source="$(pwd)"/cron-tabs.tab,target=/opt/recorder/cron-tabs.tab --volume "$(pwd)/downloads:/opt/downloads" --name recorder-test new-recorder

