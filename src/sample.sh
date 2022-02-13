kill -9 $(lsof -i :5000 | awk ' {print $2 }' | tail -n 1)
export PATH="/home/amirmohammad/Desktop/Trunk/monazam/chrome-driver:${PATH}"
./entrypoint.sh -u https://vc.sharif.edu/ch/karevanrafto -d 1 -n test-class -e high -a ضابط
