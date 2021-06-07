import os
from tempfile import gettempdir
from pathlib import Path

tmp = Path(gettempdir())
lockfile = tmp / "pixels.lock"

if os.path.exists(lockfile):
    with open(lockfile) as old_lockfile:
        old_pid = int(old_lockfile.read())

    try:
        os.kill(old_pid, 0)
    except OSError:  # Dead process
        os.remove(lockfile)
    else:
        # process is still active
        raise RuntimeError(f"Pixels painter is already running elsewhere. It is running under PID {old_pid}.")

lockfile.touch()
with open(lockfile, "w") as opened_lockfile:
    opened_lockfile.write(str(os.getpid()))
