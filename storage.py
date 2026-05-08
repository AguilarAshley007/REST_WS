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

def get_accounts():
    return list(cuentas.values())

def create_account(nombre, saldo):
    account_id = len(cuentas) + 1
    new_account = {
        "account_id": account_id,
        "nombre": nombre,
        "saldo": saldo,
        "estado": "activa"
    }
    cuentas[account_id] = new_account
    save_data()
    return new_account

def transfer_money(from_account_id, to_account_id, monto):
    from_account = get_account(from_account_id)
    to_account = get_account(to_account_id)

    if from_account and to_account and from_account["saldo"] >= monto:
        from_account["saldo"] -= monto
        to_account["saldo"] += monto
        update_account(from_account_id, from_account)
        update_account(to_account_id, to_account)

load_data()