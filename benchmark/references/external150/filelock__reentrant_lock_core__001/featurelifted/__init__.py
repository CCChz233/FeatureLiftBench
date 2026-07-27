import os, time
class Timeout(TimeoutError): pass
class FileLock:
    def __init__(self, lock_file, timeout=-1, poll_interval=0.05):
        self.lock_file = str(lock_file); self.timeout = timeout; self.poll_interval = poll_interval
        self._fd = None; self.lock_counter = 0
    @property
    def is_locked(self): return self._fd is not None
    def acquire(self, timeout=None, poll_interval=None, blocking=True):
        if self.is_locked:
            self.lock_counter += 1; return self
        timeout = self.timeout if timeout is None else timeout
        if not blocking: timeout = 0
        poll = self.poll_interval if poll_interval is None else poll_interval
        started = time.monotonic()
        while True:
            try:
                self._fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                self.lock_counter = 1; return self
            except FileExistsError:
                if timeout >= 0 and time.monotonic() - started >= timeout: raise Timeout(self.lock_file)
                time.sleep(poll)
    def release(self, force=False):
        if not self.is_locked: return
        self.lock_counter = 0 if force else self.lock_counter - 1
        if self.lock_counter <= 0:
            os.close(self._fd); self._fd = None
            try: os.unlink(self.lock_file)
            except FileNotFoundError: pass
    def __enter__(self): return self.acquire()
    def __exit__(self, *exc): self.release()
