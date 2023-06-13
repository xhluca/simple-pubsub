from flask import Flask, stream_with_context
import pubsub as ps

manager = ps.load_manager()
p = ps.Pubsub(manager)
p.subscribe('my-channel')

app = Flask(__name__)

@app.route('/stream')
def streamed_response():
    def generate():
        yield '<p>Generating...</p>'
        for message in p.listen():
            print(message)
            yield f'<p>{message}</p>'
    
    return stream_with_context(generate())

if __name__ == '__main__':
    app.run()

# In a first terminal:
# $ python queue_manager.py  # Starts queue manager server
#
# In another terminal:
# $ python -i pubsub.py
#
# In the interpreter:
# >>> manager = load_manager()
# >>> publish(manager, 'my-channel', 'Hello World!')
# >>> publish(manager, 'my-channel', 'Goodbye World!')
# >>> publish(manager, 'my-channel', 'Hello Again!')