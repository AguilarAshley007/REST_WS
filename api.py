from flask import Flask, request, jsonify
import uuid
from queue_manager import message_queue, results
from storage import (
    get_account,
    get_accounts,
    create_account,
    transfer_money
)

app = Flask(__name__)

def validar_monto(monto):
    return isinstance(monto, (int, float)) and monto > 0

@app.route("/saldo/<int:account_id>", methods=["GET"])
def saldo(account_id):
    
    account = get_account(account_id)
    
    if not account:
        return jsonify({"error": "Cuenta no encontrada"}), 404
    return jsonify({
        "account_id": account_id,
        "saldo": account["saldo"]
    })

#Endpoint agregado para obtener la lista de cuentas disponibles
@app.route("/cuentas", methods=["GET"])
def cuentas():
    
    accounts = get_accounts()
    
    return jsonify([{
        "account_id": account["account_id"],
        "nombre": account["nombre"],
        "saldo": account["saldo"]
    } for account in accounts])

#Endpoint agregado para crear una cuenta nueva
@app.route("/crear_cuenta", methods=["POST"])
def crear_cuenta():
    
    data = request.json
    
    if not data:
        return jsonify({"error": "JSON requerido"}), 400
    
    if "nombre" not in data or "saldo" not in data:
        return jsonify({"error": "Campos 'nombre' y 'saldo' son requeridos"}), 400
    
    if not data["nombre"].strip():
        return jsonify({"error": "El campo 'nombre' no puede estar vacío"}), 400
    
    if not isinstance(data["saldo"], (int, float)):
        return jsonify({"error": "El campo 'saldo' debe ser numérico"}), 400
    
    if data["saldo"] < 0:
        return jsonify({"error": "El campo 'saldo' no puede ser negativo"}), 400
    
    new_account = create_account(data["nombre"], data["saldo"])
    
    return jsonify({
        "account_id": new_account["account_id"],
        "nombre": new_account["nombre"],
        "saldo": new_account["saldo"]
    }), 201

#Endpoint agregado para transferir dinero entre cuentas
@app.route("/transferir", methods=["POST"])
def transferir():
    data = request.json
    if not data:
        return jsonify({"error": "JSON requerido"}), 400
    
    required = [
        "from_account_id",
        "to_account_id",
        "monto"
    ]

    for field in required:
        if field not in data:
            return jsonify({
                "error": f"Falta el campo {field}"
            }), 400

    if not validar_monto(data["monto"]):
        return jsonify({"error": "Monto inválido"}), 400

    if data["from_account_id"] == data["to_account_id"]:
        return jsonify({
            "error": "No puedes transferir a la misma cuenta"
        }), 400
    
    origin = get_account(data["from_account_id"])
    destiny = get_account(data["to_account_id"])

    if not origin or not destiny:
        return jsonify({
            "error": "Cuenta no encontrada"
        }), 404

    if origin["saldo"] < data["monto"]:
        return jsonify({
            "error": "Fondos insuficientes"
        }), 400

    transfer_money(data["from_account_id"], data["to_account_id"], data["monto"])
    return jsonify({"message": "Transferencia realizada con éxito"}), 200

@app.route("/depositar", methods=["POST"])
def depositar():

    data = request.json

    if not data:
        return jsonify({"error": "JSON requerido"}), 400
    
    # Validar campos
    if "account_id" not in data or "monto" not in data:
        return jsonify({"error": "Faltan campos"}), 400
    
    account = get_account(data["account_id"])

    if not account:
        return jsonify({
            "error": "Cuenta no encontrada"
        }), 404

    if not validar_monto(data["monto"]):
        return jsonify({
            "error": "Monto inválido"
        }), 400

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

    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    if "account_id" not in data or "monto" not in data:
        return jsonify({"error": "Faltan campos"}), 400

    account = get_account(data["account_id"])

    if not account:
        return jsonify({
            "error": "Cuenta no encontrada"
        }), 404

    if not validar_monto(data["monto"]):
        return jsonify({
            "error": "Monto inválido"
        }), 400

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

if __name__ == "__main__":
    app.run(debug=True)