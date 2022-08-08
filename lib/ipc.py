import os, stat
def isFifo():
    try:
        stat.S_ISFIFO(os.stat("/tmp/fifo").st_mode)
    except:
        return False
    finally:
        return True


def mem_write(str):
    if not isFifo():
        os.mkfifo("/tmp/fifo")

    fifo_read = open('/tmp/fifo', 'w') #0 without buffering
    fifo_read.write(str)
    fifo_read.close()


def mem_read():
    fifo_read = open('/tmp/fifo', 'r') #0 without buffering
    result = fifo_read.read()
    fifo_read.close()
    return result