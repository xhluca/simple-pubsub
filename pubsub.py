from functools import partial
from multiprocessing import Process, Queue
from uuid import uuid4

class Listener(Process):
    def __init__(self, queue, callback):
        super().__init__()
        self.queue = queue
        self.callback = callback

    def run(self):
        while True:
            self.callback(self.queue.get())

class Pubsub:
    def __init__(self, manager):
        self.manager = manager
        self.listeners = {}
        self.listener_queue = Queue()
        self.uid = str(uuid4())
    
    def _put_message(self, channel: str, message: str):
        return self.listener_queue.put({'channel': channel, 'data': message.encode(), 'type': 'message'})
    
    def subscribe(self, *channels):
        self.unsubscribe(*channels)  # Remove previous subscriptions
        for channel in channels:
            q = self.manager.create_queue(channel, self.uid)
            self.listeners[channel] = Listener(q, partial(self._put_message, channel))
            self.listeners[channel].start()
    
    def unsubscribe(self, *channels):
        for channel in channels:
            if channel in self.listeners:
                self.listeners.pop(channel).terminate()
                self.manager.delete_queue(channel, self.uid)

    def listen(self, block=True, timeout=None):
        while True:
            yield self.listener_queue.get(block=block, timeout=timeout)

def publish(manager, channel, message, block=False, timeout=None):
    for subkey in manager.get_subkeys(channel).copy():
        manager.get_queue(channel, subkey).put(message, block=block, timeout=timeout)

def load_manager(host="localhost", port=40080, authkey="abracadabra", register=True, connect=True):
    from multiprocessing.managers import BaseManager

    class QueueManager(BaseManager): pass

    if register:
        QueueManager.register('get_queue')
        QueueManager.register('create_queue')
        QueueManager.register('delete_queue')
        QueueManager.register('get_subkeys')
    
    qm = QueueManager(address=(host, port), authkey=authkey.encode())
    if connect:
        qm.connect()
    return qm

