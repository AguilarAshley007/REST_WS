import requests
import threading
import time

BASE_URL = "http://127.0.0.1:5000"
ACCOUNT_ID = 1
MONTO_RETIRO = 500

def obtener_token():
    try:
        response = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "1234"})
        return response.json().get("token")
    except requests.exceptions.ConnectionError:
        print("Error: El servidor no está respondiendo.")
        return None

def cliente_concurrente(nombre_hilo, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print(f"[{nombre_hilo}] Solicitando retiro de {MONTO_RETIRO}...")
    response = requests.post(
        f"{BASE_URL}/retirar", 
        json={"account_id": ACCOUNT_ID, "monto": MONTO_RETIRO}, 
        headers=headers
    )
    
    data = response.json()
    print(f"[{nombre_hilo}] Petición en cola, request_id: {data.get('request_id')}")
    
    if "request_id" in data:
        request_id = data["request_id"]
        time.sleep(1.5) 
        res_poll = requests.get(f"{BASE_URL}/resultado/{request_id}", headers=headers)
        print(f"[{nombre_hilo}] RESULTADO FINAL: {res_poll.json()}")

def ejecutar_prueba():
    print("--- INICIANDO PRUEBA DE CONCURRENCIA (3 CLIENTES) ---")
    token = obtener_token()
    
    if not token:
        print("No se pudo obtener el token. Abortando prueba.")
        return


    headers = {"Authorization": f"Bearer {token}"}
    saldo_inicial = requests.get(f"{BASE_URL}/saldo/{ACCOUNT_ID}", headers=headers)
    print(f"Saldo inicial en cuenta {ACCOUNT_ID}: {saldo_inicial.json()}")
    print("-" * 50)

    # Crear 3 hilos para simular 3 clientes atacando el endpoint exactamente al mismo tiempo
    hilos = []
    for i in ["Cliente A", "Cliente B", "Cliente C"]:
        hilo = threading.Thread(target=cliente_concurrente, args=(i, token))
        hilos.append(hilo)
    
    # Iniciar todos los hilos
    for hilo in hilos:
        hilo.start()
        
    # Esperar a que todos terminen
    for hilo in hilos:
        hilo.join()
        
    print("-" * 50)
    print("Prueba de concurrencia finalizada.")
    
    # Consultar saldo final
    saldo_final = requests.get(f"{BASE_URL}/saldo/{ACCOUNT_ID}", headers=headers)
    print(f"Saldo final en cuenta {ACCOUNT_ID}: {saldo_final.json()}")

if __name__ == "__main__":
    ejecutar_prueba()