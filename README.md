Table of content:
- [Installation](#installation)
- [Motivation](#motivation)
  - [Inspiration](#inspiration)
  - [Why not use redis?](#why-not-use-redis)
- [Implementation](#implementation)

# Installation

This is a pure python implementation, so you only need to run this:
```bash
git clone https://github.com/xhluca/simple-pubsub
cd simple-pubsub
```

If you want to run the flask app demo:
```bash
python -m venv venv
source venv/bin/activate
pip install flask
```


# Motivation

[Redis has a nice implementation of publish/subscribe](https://redis-py.readthedocs.io/en/stable/advanced_features.html#publish-subscribe). Apart from the use of redis (a scalable open-source, but enterprise ready in-memory data store), it has a nice `listen()` method that allows you to listen for messages on a channel, blocking until a message is available. When this is used as an iterator, it allows you to write scripts that only execute when a message is available:
```python
import redis

r = redis.Redis()
p = r.pubsub()
p.subscribe('my-channel')

for message in p.listen():
    if message['type'] == 'email':
        send_email(message['subject'], message['body'])
    elif message['type'] == 'sms':
        send_sms(message['body'])
    elif message['type'] == 'exit':
        break
```

There's other ways to do this; for example, `PyPubSub` directly attaches a callback when you call `subscribe`:
```python
from pubsub import pub

def my_channel_listener(arg1, arg2):
    print('Function listener1 received:')
    print('  arg1 =', arg1)
    print('  arg2 =', arg2)

# register listener
pub.subscribe(my_channel_listener, 'my-channel')

# send message
pub.sendMessage('my-channel', arg1='abc', arg2=123)
```

This, of course, is more powerful as you can send non-string messages. However, this does not allow you to write scripts that only execute when a message is available. You can, of course, use a `while True` loop and sleep for a bit, but this is not ideal. Similarly, [this tutorial](https://dev.to/mandrewcito/lazy-pub-sub-python-implementation-3fi8) concisely implements a pub/sub system, but also by attaching a callback to an object when you subscribe.

Why do I want a blocking iterator? Can I not refactor my code to use callbacks? It might be possible to come up with various scenarios where blocking is preferable, but my main reason is to be able to stream data via iterators. For example, in Flask, [you can stream data to the client](https://flask.palletsprojects.com/en/2.3.x/patterns/streaming/) by returning an iterator:

```python
from flask import Flask, stream_with_context
import redis

r = redis.Redis()
p = r.pubsub()
p.subscribe('my-channel')

app = Flask(__name__)

@app.route('/stream')
def streamed_response():
    def generate():
        for message in p.listen():
            yield f'<p>{message}</p>'
    
    return stream_with_context(generate())

# In another terminal:
# $ redis-cli
#
# In the redis-cli:
# > publish my-channel "Hello World!"
# > publish my-channel "Goodbye World!"
# > publish my-channel "Hello Again!"
```

[This stackoverflow thread](https://stackoverflow.com/a/12236019/13837091) oprvides a nice explanation of why this is useful.

## Inspiration

As I was faced with this problem, I came across this blog post by [Max Halford](https://maxhalford.github.io/blog/flask-sse-no-deps/) where he implements a pub/sub system to be used for Flask Streaming (Server-Sent Events). My implementation is based on his, but I've extended it to be multiprocessing read, as inspired by this [comment](https://github.com/MaxHalford/maxhalford.github.io/issues/5#issuecomment-902440289).

## Why not use redis?

Redis is cool, but it's an extra dependency. Also, you need to install it outside of Python (the official installation recommends using `sudo`, though there might be ways to install it without `sudo`).

Thus, it'd be nice to have a pure Python implementation of a pub/sub system that allows you to listen for messages on a channel, blocking until a message is available.

# Implementation

You can find the implementation in the following files:
- [pubsub.py](pubsub.py): The pub/sub system.
- [queue_manager.py](queue_manager.py): A queue system implemented in a multiprocessing manager that allows you to send messages to a channel.
- [app.py](app.py): A Flask app that uses the pub/sub system to stream data to the client.

To start the manager server, you can run the following command:
```bash
python queue_manager.py
```

Now, there's two options to listen (please choose one):

1. To start the Flask app: `python app.py`. Then, you can go to `http://localhost:5000/stream` to see the stream.
2. To listen for messages on a channel, you can use the `listen` method of the `Pubsub` class:

```python
import pubsub as ps

manager = ps.load_manager()
p = ps.Pubsub(manager)
p.subscribe('my-channel')
for message in p.listen():
    print(message)
```

To send messages to a channel, you can use the `publish` function:
```python
import time
import pubsub as ps

manager = ps.load_manager()
for i in range(60):
    ps.publish(manager, 'my-channel', f'Hello World {i}!')
    time.sleep(1)
```
