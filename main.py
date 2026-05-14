from threading import Thread
from storage import load_data
from worker import worker_loop
from api import app

if __name__ == "__main__":
    load_data()

    worker_thread = Thread(target=worker_loop, daemon=True)
    worker_thread.start()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        ssl_context=("server.crt", "server.key")
    )