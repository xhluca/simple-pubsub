from multiprocessing import Process

class Listener(Process):
    def __init__(self, queue, callback):
        super().__init__()
        self.queue = queue
        self.callback = callback

    def run(self):
        while True:
            self.callback({'key': self.key, 'item': self.queue.get()})

def print_with_key(content):
    print(f"{content['key']}: {content['item']}")

def listen(key, manager):
    queue = manager.get_queue(key)
    return Listener(queue, callback=print_with_key).start()

if __name__ == '__main__':
    # Testing with a listener on 3 queues
    from queue_manager import QueueManager
    qm = QueueManager(address=('localhost', 40080), authkey=b'abracadabra')
    qm.connect()

    listen('a', qm)
    listen('b', qm)
    listen('c', qm)