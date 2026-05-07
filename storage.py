import json
from threading import Lock

FILE_PATH = "cuentas.json"
lock = Lock()

cuentas = {}

def load_data():
    global cuentas
    with open(FILE_PATH, "r") as f:
        data = json.load(f)
        cuentas = {c["account_id"]: c for c in data}

def save_data():
    with lock:
        with open(FILE_PATH, "w") as f:
            json.dump(list(cuentas.values()), f, indent=2)

def get_account(account_id):
    return cuentas.get(account_id)

def update_account(account_id, data):
    cuentas[account_id] = data
    save_data()