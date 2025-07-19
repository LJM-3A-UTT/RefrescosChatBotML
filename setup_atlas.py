#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuracion completa para RefrescoBot ML con MongoDB Atlas
Configura desarrollo local + base de datos Atlas
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description=""):
    """Ejecutar comando y mostrar resultado"""
    if description:
        print(f"[CONFIG] {description}...")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"[OK] {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error en {description}: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def create_env_files():
    """Crear archivos .env para desarrollo local + Atlas"""
    
    # Backend .env - MongoDB Atlas
    backend_env = '''MONGO_URL="mongodb+srv://LJM:ljm542136@cluster0.7mlbi.mongodb.net/refrescos_chat_bot"
DB_NAME="refrescos_chat_bot"'''
    
    with open("backend/.env", "w", encoding='utf-8') as f:
        f.write(backend_env)
    print("[OK] backend/.env creado (Atlas)")
    
    # Frontend .env - Local
    frontend_env = """REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000"""
    
    with open("frontend/.env", "w", encoding='utf-8') as f:
        f.write(frontend_env)
    print("[OK] frontend/.env creado (Local)")

def test_atlas_connection():
    """Probar conexion a MongoDB Atlas"""
    
    test_script = '''import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test():
    try:
        client = AsyncIOMotorClient("mongodb+srv://LJM:ljm542136@cluster0.7mlbi.mongodb.net/refrescos_chat_bot")
        await client.admin.command("ismaster")
        print("[OK] Conexion a Atlas exitosa")
        client.close()
        return True
    except Exception as e:
        print(f"[ERROR] Error conectando a Atlas: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    exit(0 if success else 1)
'''
    
    with open("test_atlas_temp.py", "w", encoding='utf-8') as f:
        f.write(test_script)
    
    try:
        result = subprocess.run("python test_atlas_temp.py", shell=True, capture_output=True, text=True)
        success = result.returncode == 0
        print(result.stdout)
        if not success:
            print("[INFO] Verifica tu conexion a internet y las credenciales de Atlas")
        return success
    finally:
        if os.path.exists("test_atlas_temp.py"):
            os.remove("test_atlas_temp.py")


def main():
    """Configuracion principal"""
    
    print("RefrescoBot ML - Configuracion Local + MongoDB Atlas")
    print("=" * 65)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("backend/server.py") or not os.path.exists("frontend/package.json"):
        print("[ERROR] Ejecuta este script desde la raiz del proyecto")
        return False
    
    # 1. Crear archivos .env
    print("\n[STEP 1] Configurando variables de entorno...")
    create_env_files()
    
    # 2. Probar conexion Atlas
    print("\n[STEP 2] Probando conexion a MongoDB Atlas...")
    if not test_atlas_connection():
        print("[WARN] No se pudo conectar a Atlas, pero continuando configuracion...")
    
    # 3. Configurar backend Python
    print("\n[STEP 3] Configurando backend Python...")
    
    if not os.path.exists("backend/venv"):
        if run_command("cd backend && python -m venv venv", "Creando entorno virtual"):
            print("[OK] Entorno virtual creado")
    
    # Usar el activador correcto para Windows
    if os.name == 'nt':
        venv_python = "backend\\venv\\Scripts\\python"
        venv_pip = "backend\\venv\\Scripts\\pip"
    else:
        venv_python = "backend/venv/bin/python"
        venv_pip = "backend/venv/bin/pip"
    
    if os.path.exists(venv_python):
        run_command(f"{venv_pip} install -r backend/requirements.txt", "Instalando dependencias Python")
    else:
        run_command("cd backend && pip install -r requirements.txt", "Instalando dependencias Python (sistema)")
    
    # 4. Configurar frontend
    print("\n[STEP 4] Configurando frontend React...")
    
    if not os.path.exists("frontend/node_modules"):
        if run_command("cd frontend && yarn install", "Instalando dependencias con Yarn"):
            print("[OK] Dependencias React instaladas con Yarn")
        elif run_command("cd frontend && npm install", "Instalando dependencias con npm"):
            print("[OK] Dependencias React instaladas con npm")
    
    # 5. Setup completado
    
    print("\n" + "=" * 65)
    print("CONFIGURACION COMPLETADA!")
    print("=" * 65)
    print("Configuracion hibrida:")
    print("  [OK] Backend: Local (localhost:8001)")
    print("  [OK] Frontend: Local (localhost:3000)")
    print("  [OK] Imagenes: Locales (sin internet)")
    print("  [OK] Modelos ML: Locales (sin internet)")
    print("  [OK] Base de datos: Atlas refrescos_chat_bot (requiere internet)")
    print("")
    print("EJECUTAR EL PROYECTO:")
    print("  Windows: python run_local.py")
    print("  Linux/Mac: ./run_local.sh")
    print("")
    print("URLs:")
    print("  Frontend: http://localhost:3000")
    print("  Backend:  http://localhost:8001")
    print("  API Docs: http://localhost:8001/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)