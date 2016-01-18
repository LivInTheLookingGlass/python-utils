import multiprocessing, sys
from datetime import datetime

print_lock = multiprocessing.RLock()


def safeprint(msg):
    """Prints in a thread-lock, taking a single object as an argument"""
    string = ("[" + str(multiprocessing.current_process().pid) + "] " +
              datetime.now().strftime('%H:%M:%S: ') + str(msg) + '\r\n')
    with print_lock:
        sys.stdout.write(string)
