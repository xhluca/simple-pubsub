from multiprocessing.managers import BaseManager, SyncManager
from multiprocessing import Queue, Lock, Manager

from collections import defaultdict

class QueueManager(BaseManager): pass

lock = Lock()

queue_dicts = defaultdict(dict)

def get_queue(key, subkey='default'):
    with lock:
        return queue_dicts[key][subkey]

def create_queue(key, subkey='default'):
    with lock:
        if subkey not in queue_dicts[key]:
            queue_dicts[key][subkey] = Queue()
        return queue_dicts[key][subkey]

def delete_queue(key, subkey='default'):
    with lock:
        q = queue_dicts[key][subkey]
        # Empty the queue
        while not q.empty():
            q.get()
        del queue_dicts[key][subkey]

def get_subkeys(key):
    with lock:
        return list(queue_dicts[key].keys())

QueueManager.register('get_queue', callable=get_queue)
QueueManager.register('create_queue', callable=create_queue)
QueueManager.register('delete_queue', callable=delete_queue)
QueueManager.register('get_subkeys', callable=get_subkeys)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=40080, type=int)
    parser.add_argument('--authkey', default='abracadabra')
    args = parser.parse_args()

    m = QueueManager(address=(args.host, args.port), authkey=args.authkey.encode())
    s = m.get_server()
    print(f"Starting server at: {args.host}:{args.port}")
    s.serve_forever()