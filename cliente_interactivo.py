import requests
import time

BASE_URL = "http://127.0.0.1:5000"
TOKEN = None

def get_headers(require_auth=True):
    headers = {"Content-Type": "application/json"}
    if require_auth and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers

def login():
    global TOKEN
    print("\n--- INICIO DE SESIÓN ---")
    username = input("Usuario (ej. admin): ")
    password = input("Contraseña (ej. 1234): ")
    
    try:
        response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            TOKEN = response.json().get("token") 
            print("Login exitoso. Token guardado para esta sesión.")
        else:
            print(f"Error en login: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error de conexión: ¿Está corriendo tu servidor Flask (main.py)?")

def consultar_saldo():
    account_id = input("ID de la cuenta: ")
    response = requests.get(f"{BASE_URL}/saldo/{account_id}", headers=get_headers())
    print("\nRespuesta del servidor:", response.json())

def depositar():
    account_id = input("ID de la cuenta: ")
    try:
        monto = float(input("Monto a depositar: "))
        response = requests.post(
            f"{BASE_URL}/depositar", 
            json={"account_id": int(account_id), "monto": monto}, 
            headers=get_headers()
        )
        print("\nRespuesta del servidor:", response.json())
    except ValueError:
        print("Error: El monto debe ser un número.")

def retirar():
    account_id = input("ID de la cuenta: ")
    try:
        monto = float(input("Monto a retirar: "))
        response = requests.post(
            f"{BASE_URL}/retirar", 
            json={"account_id": int(account_id), "monto": monto}, 
            headers=get_headers()
        )
        print("\nRespuesta del servidor:", response.json())
    except ValueError:
        print("Error: El monto debe ser un número.")

def consultar_resultado():
    request_id = input("ID de la petición (request_id): ")
    response = requests.get(f"{BASE_URL}/resultado/{request_id}", headers=get_headers())
    print("\nRespuesta del servidor:", response.json())

def crear_cuenta():
    print("\n--- ALTA DE NUEVA CUENTA ---")
    nombre = input("Nombre del titular: ")
    try:
        saldo_inicial = float(input("Saldo inicial: "))
        response = requests.post(
            f"{BASE_URL}/crear_cuenta",
            json={"nombre": nombre, "saldo": saldo_inicial},
            headers=get_headers()
        )
        print("\nRespuesta del servidor:", response.json())
    except ValueError:
        print("Error: El saldo debe ser un número.")

def cambiar_estado():
    print("\n--- CAMBIAR ESTADO DE CUENTA ---")
    account_id = input("ID de la cuenta: ")
    print("Estados disponibles: 1. Activa, 2. Bloqueada")
    op = input("Selecciona el nuevo estado (1 o 2): ")
    
    nuevo_estado = "activa" if op == "1" else "bloqueada"
    
    response = requests.post(
        f"{BASE_URL}/cambiar_estado",
        json={"account_id": int(account_id), "estado": nuevo_estado},
        headers=get_headers()
    )
    print("\nRespuesta del servidor:", response.json())

def listar_cuentas():
    print("\n--- LISTA DE CUENTAS ---")
    response = requests.get(f"{BASE_URL}/cuentas", headers=get_headers())
    print("\nRespuesta del servidor:", response.json())

def menu():
    while True:
        print("\n" + "="*35)
        print(" SISTEMA DISTRIBUIDO - CAJA DE AHORRO ")
        print("="*35)
        print("1. Autenticar (Login)")
        print("2. Consultar Saldo")
        print("3. Depositar")
        print("4. Retirar")
        print("5. Consultar Resultado (Polling)")
        print("6. Crear Nueva Cuenta")
        print("7. Activar/Desactivar Cuenta")
        print("8. Listar Todas las Cuentas")
        print("9. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            login()
        elif opcion in ['2', '3', '4', '5', '6', '7', '8'] and not TOKEN:
            print("\nAtención: Necesitas autenticarte (Opción 1) antes de usar esta función.")
        elif opcion == '2':
            consultar_saldo()
        elif opcion == '3':
            depositar()
        elif opcion == '4':
            retirar()
        elif opcion == '5':
            consultar_resultado()
        elif opcion == '6':
            crear_cuenta()
        elif opcion == '7':
            cambiar_estado()
        elif opcion == '8':
            listar_cuentas()
        elif opcion == '9':
            print("Saliendo del cliente interactivo...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()