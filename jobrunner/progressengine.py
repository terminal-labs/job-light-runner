import os
import sys
import time

from jobrunner.config import tmp_dirs

def pbar(uuid_name, checkpointlines):
    runs = len(checkpointlines)
    count = 0
    while count <= runs - 1:
        updt(runs, count)
        with open('.tmp/runners/runs/' + uuid_name + "/process.out") as f:
            count = measure_progress(f, checkpointlines)
        time.sleep(1)
    updt(runs, count)


def measure_progress(f, checkpointlines):
    lines = f.readlines()
    lines = [s.strip() for s in lines]
    count = 0
    for line in checkpointlines:
        if line in lines:
            count = count + 1
    return count

def get_checkpointlines(filepath):
    with open(filepath) as f:
        checkpointlines = f.readlines()
        checkpointlines = [s.strip() for s in checkpointlines]
    return checkpointlines

def register_run(uuid_name):
    dir = '.tmp/runners/runs/' + uuid_name
    if not os.path.exists(dir):
        os.mkdir(dir)
    with open('.tmp/runners/runs/' + uuid_name + "/process.lines", 'w') as f:
        f.write("")
    with open('.tmp/runners/runs/' + uuid_name + "/process.events", 'w') as f:
        f.write("")


def updt(total, progress):
    barLength, status = 20, ""
    progress = float(progress) / float(total)
    if progress >= 1.:
        progress, status = 1, "\r\n"
    block = int(round(barLength * progress))
    text = "\r[{}] {:.0f}% {}".format(
        "#" * block + "-" * (barLength - block), round(progress * 100, 0),
        status)
    sys.stdout.write(text)
    sys.stdout.flush()


def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()
