from threading import Thread
from storage import load_data
from worker import worker_loop
from api import app

if __name__ == "__main__":
    load_data()

    worker_thread = Thread(target=worker_loop, daemon=True)
    worker_thread.start()

    app.run(port=5000, debug=True)
    