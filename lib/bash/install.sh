if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

FILE=obj/smartscreen
ASSETS=assets
LOCAL=""

if [[ $OSTYPE == 'darwin'* ]]; then
  LOCAL="local/"
fi

if [[ -f "$FILE" ]]; then
    if [[ -f "$PYFILE" ]]; then
      sh compile_python.sh
    fi
    sudo cp $FILE /usr/"$LOCAL"bin/smartscreen
    sudo mkdir -p /usr/"$LOCAL"share/smartscreen/scripts
    sudo cp -r $ASSETS /usr/"$LOCAL"share/smartscreen
    sudo cp obj/smartscreen-python /usr/"$LOCAL"share/smartscreen/scripts
else
    echo "Please first run \"make all\"" ;\
fi
