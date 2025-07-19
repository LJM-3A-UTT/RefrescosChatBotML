#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ejecutar RefrescoBot ML en Windows con MongoDB Atlas
Uso: python run_local.py
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def run_command_background(command, description=""):
    """Ejecutar comando en background"""
    if description:
        print(f"[START] {description}...")
    
    try:
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            process = subprocess.Popen(command, shell=True)
        
        return process
    except Exception as e:
        print(f"[ERROR] Error ejecutando {description}: {e}")
        return None

def test_connection(url, max_retries=10):
    """Probar conexion a una URL"""
    import urllib.request
    import urllib.error
    
    for i in range(max_retries):
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 200:
                    return True
        except:
            time.sleep(1)
    return False

def create_env_files():
    """Crear archivos .env si no existen"""
    
    # Backend .env
    backend_env = '''MONGO_URL="mongodb+srv://LJM:ljm542136@cluster0.7mlbi.mongodb.net/refrescos_chat_bot"
DB_NAME="refrescos_chat_bot"'''
    
    if not os.path.exists("backend/.env"):
        with open("backend/.env", "w", encoding='utf-8') as f:
            f.write(backend_env)
        print("[OK] backend/.env creado")
    
    # Frontend .env
    frontend_env = """REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000"""
    
    if not os.path.exists("frontend/.env"):
        with open("frontend/.env", "w", encoding='utf-8') as f:
            f.write(frontend_env)
        print("[OK] frontend/.env creado")

def main():
    """Funcion principal"""
    
    print("RefrescoBot ML - Ejecutor para Windows")
    print("=" * 50)
    
    # Verificar directorio
    if not os.path.exists("backend/server.py") or not os.path.exists("frontend/package.json"):
        print("[ERROR] Ejecuta este script desde la raiz del proyecto")
        return False
    
    # Crear archivos .env
    create_env_files()
    
    # Verificar dependencias
    print("\n[CHECK] Verificando dependencias...")
    
    # Configurar comandos segun el entorno
    if os.path.exists("backend/venv"):
        if os.name == 'nt':
            backend_cmd = "cd backend && venv\\Scripts\\activate && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
        else:
            backend_cmd = "cd backend && source venv/bin/activate && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
    else:
        backend_cmd = "cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
    
    frontend_cmd = "cd frontend && npm start"
    
    print("\n[START] Iniciando servicios...")
    
    # Iniciar backend
    print("[BACKEND] Iniciando en puerto 8001...")
    backend_process = run_command_background(backend_cmd, "Backend FastAPI")
    
    if not backend_process:
        print("[ERROR] No se pudo iniciar el backend")
        return False
    
    # Esperar a que el backend inicie
    print("[WAIT] Esperando que el backend inicie...")
    time.sleep(10)
    
    # Verificar que el backend responde
    if test_connection("http://localhost:8001/api/health"):
        print("[OK] Backend funcionando correctamente")
    else:
        print("[ERROR] Backend no responde")
        backend_process.terminate()
        return False
    
    # Iniciar frontend
    print("[FRONTEND] Iniciando en puerto 3000...")
    frontend_process = run_command_background(frontend_cmd, "Frontend React")
    
    if not frontend_process:
        print("[ERROR] No se pudo iniciar el frontend")
        backend_process.terminate()
        return False
    
    print("\n" + "=" * 50)
    print("RefrescoBot ML FUNCIONANDO!")
    print("=" * 50)
    print("Frontend: http://localhost:3000")
    print("Backend:  http://localhost:8001")
    print("API Docs: http://localhost:8001/docs")
    print("Base de datos: refrescos_chat_bot (Atlas)")
    print("")
    print("Presiona Ctrl+C para detener todos los servicios")
    print("=" * 50)
    
    try:
        # Mantener corriendo hasta Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] Deteniendo servicios...")
        backend_process.terminate()
        frontend_process.terminate()
        print("[OK] Servicios detenidos")
        return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)