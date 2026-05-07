from flask import Flask, request, jsonify
import uuid
from queue_manager import message_queue, results
from storage import get_account

app = Flask(__name__)

@app.route("/saldo/<int:account_id>", methods=["GET"])
def saldo(account_id):
    account = get_account(account_id)
    if not account:
        return jsonify({"error": "Cuenta no encontrada"}), 404
    return jsonify({
        "account_id": account_id,
        "saldo": account["saldo"]
    })

@app.route("/depositar", methods=["POST"])
def depositar():
    data = request.json
    req_id = str(uuid.uuid4())

    msg = {
        "request_id": req_id,
        "type": "deposito",
        "account_id": data["account_id"],
        "monto": data["monto"]
    }

    results[req_id] = {"status": "pending"}
    message_queue.put(msg)

    return jsonify({"request_id": req_id, "status": "pending"})

@app.route("/retirar", methods=["POST"])
def retirar():
    data = request.json
    req_id = str(uuid.uuid4())

    msg = {
        "request_id": req_id,
        "type": "retiro",
        "account_id": data["account_id"],
        "monto": data["monto"]
    }

    results[req_id] = {"status": "pending"}
    message_queue.put(msg)

    return jsonify({"request_id": req_id, "status": "pending"})

@app.route("/resultado/<request_id>", methods=["GET"])
def resultado(request_id):
    res = results.get(request_id)
    if not res:
        return jsonify({"error": "request_id no encontrado"}), 404
    return jsonify(res)

