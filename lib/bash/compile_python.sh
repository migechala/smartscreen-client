PYFILE=get_data.py
CFILE=get_data.c

cython $PYFILE --embed
PYTHONLIBVER=python$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')$(python3-config --abiflags)
gcc -Os $(python3-config --includes) $CFILE -o obj/smartscreen-python $(python3-config --ldflags) -l$PYTHONLIBVER
rm $CFILE