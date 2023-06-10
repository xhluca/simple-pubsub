from queue_manager import QueueManager

m = QueueManager(address=('localhost', 40080), authkey=b'abracadabra')

m.connect()

m.get_queue('a').put('a1')
m.get_queue('b').put('b1')
m.get_queue('a').put('a2')
m.get_queue('c').put('c1')
