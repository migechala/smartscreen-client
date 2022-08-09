if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

FILE=obj/smartscreen
if [[ -f "$FILE" ]]; then
    cp $FILE /usr/local/bin/smartscreen
else
    echo "Please first run \"make all\"" ;\
fi
