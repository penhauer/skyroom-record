# Skyroom recording automation

This repository is a dockerized environment to record classes of vclass.sharif.edu and skyroom.online.

## How to use?
It's simple. Install docker and then create a `downloads` directory.

create the docker image as the image is not published yet.

goto base directory and run

```bash
docker build --tag skyroom-recorder:latest .
```

for recording only one class run
```bash
docker run --rm --volume "$(pwd)/downloads:/opt/downloads" --name recorder skyroom-recorder --single -u VLASS_URL -d CLASS_DURATION -n test-class -e encoding
```

for recording classes with cron, edit cron-tabs.tab and run

```bash
bash run.sh
```

Notes:
 - VCLASS_URL must be the url of class with `https://`.
 - CLASS_DURATION must be the duration of recording in minutes. like `90`
 - Your recorded video will be saved on `./downloads/test-class/NOW/video.webm`.
 - To update your docker image you can just run: `docker pull atofighi/skyroom-record`.
 - Encoding quality `-e`
 
      This option converts the `.webm` file to a `.mp4` file. It has encoding presets that should be defined otherwise no conversion would occur.

      `high` -best quality, slower and higher in size

      `medium` -best choice for uploading, medium quality, medium speed, medium size

      `low` - chat text becomes unreadable but low in size and fast

      `no-encoding` -default best quality, medium size, no conversion
 - With the `-v` option you can specify a file to encode without needing to record. Please note that when using this option you should provide only `-e` and `-v` otherwise it wouldn't work.

