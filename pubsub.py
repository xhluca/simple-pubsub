from multiprocessing import Process, Queue

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
    
    def _put_message(self, channel: str):
        def put(message):
            self.listener_queue.put({'channel': channel, 'data': message.encode(), 'type': 'message'})
        
        return put
    
    def subscribe(self, *channels):
        for channel in channels:
            self.listeners[channel] = Listener(
                self.manager.create_queue(channel), self._put_message(channel)
            )
            self.listeners[channel].start()
    
    def unsubscribe(self, *channels):
        for channel in channels:
            if channel in self.listeners:
                self.listeners.pop(channel).terminate()

    def listen(self):
        while True:
            yield self.listener_queue.get()

def publish(manager, channel, message):
    manager.get_queue(channel).put(message)

def load_manager(host="localhost", port=40080, authkey="abracadabra", register=True, connect=True):
    from queue_manager import QueueManager

    qm = QueueManager(address=(host, port), authkey=authkey.encode())
    if register:
        qm.register('get_queue')
        qm.register('create_queue')
        qm.register('delete_queue')
    if connect:
        qm.connect()
    return qm

