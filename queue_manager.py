from multiprocessing.managers import BaseManager
from multiprocessing import Queue, Lock

class QueueManager(BaseManager): pass

lock = Lock()

queue_dicts = {}

def get_queue(key):
    with lock:
        return queue_dicts[key]

def create_queue(key):
    with lock:
        if key not in queue_dicts:
            queue_dicts[key] = Queue()
        return queue_dicts[key]

def delete_queue(key):
    with lock:
        # Empty the queue
        while not queue_dicts[key].empty():
            queue_dicts[key].get()
        # Delete the queue
        del queue_dicts[key]

QueueManager.register('get_queue', callable=get_queue)
QueueManager.register('create_queue', callable=create_queue)
QueueManager.register('delete_queue', callable=delete_queue)