import os
import sys
import json
import time

from jobrunner.config import tmp_dirs

def get_track_data(uuid_name):
    with open('.tmp/runners/runs/' + uuid_name + "/track.json", "rb") as f:
        data = json.loads(f.read())
        return data

def write_track_data(filepath, status):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=4)

def track_run(uuid_name, checkpointlines, pbar=False):
    def _update_track_file(runs, count):
        status = {"runs":runs, "count":count}
        write_track_data('.tmp/runners/runs/' + uuid_name + "/track.json", status)
    runs = len(checkpointlines)
    count = 0
    status = {"runs":runs, "count":count}
    if pbar:
        updt(runs, count)
    _update_track_file(runs, count)
    while count < runs:
        with open('.tmp/runners/runs/' + uuid_name + "/process.out") as f:
            mp = measure_progress(f, checkpointlines)
            if mp > count:
                count = mp
                if pbar:
                    updt(runs, count)
                _update_track_file(runs, count)
        time.sleep(1)

def measure_progress(f, checkpointlines):
    lines = f.readlines()
    lines = [s.strip() for s in lines]
    lines = [s for s in lines if s]
    count = 0
    for line in checkpointlines:
        if line in lines:
            count = count + 1
    return count

def get_checkpointlines(filepath):
    with open(filepath) as f:
        checkpointlines = f.readlines()
        checkpointlines = [s.strip() for s in checkpointlines]
        checkpointlines = [s for s in checkpointlines if s]

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
