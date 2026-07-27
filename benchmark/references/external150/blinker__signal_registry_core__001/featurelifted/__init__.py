import contextlib, weakref
ANY = object()
class Signal:
    def __init__(self, doc=None): self.__doc__ = doc; self._receivers = []
    def connect(self, receiver, sender=ANY, weak=True):
        if weak:
            try:
                ref = weakref.WeakMethod(receiver)
            except TypeError:
                ref = weakref.ref(receiver)
        else: ref = lambda: receiver
        self._receivers.append((ref, sender, receiver if not weak else None))
        return receiver
    def disconnect(self, receiver, sender=ANY):
        self._receivers = [row for row in self._receivers if not ((row[0]() is receiver) and (sender is ANY or row[1] == sender))]
    def receivers_for(self, sender):
        alive = []
        for ref, expected, strong in self._receivers:
            receiver = ref()
            if receiver is None: continue
            alive.append((ref, expected, strong))
            if expected is ANY or expected == sender: yield receiver
        self._receivers = alive
    def send(self, sender=None, **kwargs):
        return [(receiver, receiver(sender, **kwargs)) for receiver in self.receivers_for(sender)]
    @contextlib.contextmanager
    def connected_to(self, receiver, sender=ANY):
        self.connect(receiver, sender=sender, weak=False)
        try: yield receiver
        finally: self.disconnect(receiver, sender=sender)
class Namespace(dict):
    def signal(self, name, doc=None):
        if name not in self: self[name] = Signal(doc)
        return self[name]
