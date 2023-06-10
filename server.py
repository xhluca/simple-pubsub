from queue_manager import QueueManager

if __name__ == '__main__':
    m = QueueManager(address=('', 40080), authkey=b'abracadabra')
    s = m.get_server()
    s.serve_forever()