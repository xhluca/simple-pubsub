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