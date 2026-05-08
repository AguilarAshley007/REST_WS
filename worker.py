import time
from queue_manager import message_queue, results
from storage import get_account, update_account

def validar_monto(monto):
    return isinstance(monto, (int, float)) and monto > 0

def process_message(msg):
    req_id = msg["request_id"]
    tipo = msg["type"]
    acc_id = msg["account_id"]
    monto = msg.get("monto", 0)

    account = get_account(acc_id)

    if not account:
        results[req_id] = {"status": "error", "mensaje": "Cuenta no encontrada"}
        return

    if tipo == "deposito":
        if not validar_monto(monto):
            results[req_id] = {"status": "error", "mensaje": "Monto inválido"}
            return

        account["saldo"] += monto
        update_account(acc_id, account)

        results[req_id] = {"status": "done", "saldo": account["saldo"]}

    elif tipo == "retiro":
        if account["estado"] != "activa":
            results[req_id] = {"status": "error", "mensaje": "Cuenta inactiva"}
            return

        if not validar_monto(monto):
            results[req_id] = {"status": "error", "mensaje": "Monto inválido"}
            return

        if account["saldo"] < monto:
            results[req_id] = {"status": "error", "mensaje": "Fondos insuficientes"}
            return

        account["saldo"] -= monto
        update_account(acc_id, account)

        results[req_id] = {"status": "done", "saldo": account["saldo"]}

def worker_loop():
    print("Worker iniciado...")
    while True:
        msg = message_queue.get()
        process_message(msg)
        message_queue.task_done()
        time.sleep(0.5)  # simula procesamiento

if __name__ == "__main__":
    worker_loop()