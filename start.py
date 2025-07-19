#!/usr/bin/env python3
"""
REFRESCOBOT ML - SCRIPT DE INICIO RÁPIDO
Script principal para iniciar servicios y gestionar el sistema

FUNCIONALIDADES:
- Inicio rápido de servicios (backend + frontend)
- Acceso a panel de administración
- Acceso a sistema de testing
- Inicialización completa del sistema
- Diagnósticos rápidos
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import signal
import atexit

class RefrescoBotManager:
    """Gestor principal del sistema RefrescoBot ML"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = Path(__file__).parent
        
        # Registrar función de limpieza
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Manejar señales del sistema"""
        print("\n🛑 Cerrando servicios...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Limpiar procesos al cerrar"""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except:
                try:
                    self.backend_process.kill()
                except:
                    pass
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except:
                try:
                    self.frontend_process.kill()
                except:
                    pass
    
    def show_main_menu(self):
        """Mostrar menú principal"""
        print("\n" + "="*70)
        print("🤖 REFRESCOBOT ML - GESTOR DEL SISTEMA")
        print("="*70)
        print("1. 🚀 INICIO RÁPIDO (Backend + Frontend)")
        print("2. 🔧 Solo Backend")
        print("3. 🎨 Solo Frontend") 
        print("4. ⚙️  Inicializar Sistema Completo")
        print("5. 🛠️  Panel de Administración")
        print("6. 🧪 Sistema de Testing")
        print("7. 📊 Diagnósticos Rápidos")
        print("8. 📋 Estado del Sistema")
        print("9. 🚪 Salir")
        print("="*70)
    
    def quick_start(self):
        """Inicio rápido de ambos servicios"""
        print("\n🚀 INICIANDO SERVICIOS...")
        print("-" * 50)
        
        # Verificar dependencias
        if not self.check_dependencies():
            return False
        
        try:
            # Cambiar al directorio backend
            backend_dir = self.base_dir / "backend"
            os.chdir(backend_dir)
            
            # Iniciar backend
            print("🔧 Iniciando backend...")
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "server:app", 
                "--host", "0.0.0.0", 
                "--port", "8001", 
                "--reload"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Esperar a que el backend esté listo
            print("⏳ Esperando a que el backend esté listo...")
            backend_ready = False
            for i in range(30):  # Esperar hasta 30 segundos
                try:
                    import requests
                    response = requests.get("http://localhost:8001/status", timeout=2)
                    if response.status_code == 200:
                        backend_ready = True
                        break
                except:
                    pass
                time.sleep(1)
                print(f"   Esperando... {i+1}/30")
            
            if not backend_ready:
                print("❌ Backend no respondió en tiempo esperado")
                return False
            
            print("✅ Backend iniciado en http://localhost:8001")
            
            # Cambiar al directorio frontend
            frontend_dir = self.base_dir / "frontend"
            os.chdir(frontend_dir)
            
            # Iniciar frontend
            print("🎨 Iniciando frontend...")
            env = os.environ.copy()
            env['BROWSER'] = 'none'  # No abrir navegador automáticamente
            
            self.frontend_process = subprocess.Popen([
                "yarn", "start"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            
            # Esperar a que el frontend esté listo
            print("⏳ Esperando a que el frontend esté listo...")
            frontend_ready = False
            for i in range(60):  # Esperar hasta 60 segundos
                try:
                    import requests
                    response = requests.get("http://localhost:3000", timeout=2)
                    if response.status_code == 200:
                        frontend_ready = True
                        break
                except:
                    pass
                time.sleep(1)
                if i % 5 == 0:  # Mostrar progreso cada 5 segundos
                    print(f"   Esperando... {i+1}/60")
            
            if frontend_ready:
                print("✅ Frontend iniciado en http://localhost:3000")
            else:
                print("⚠️  Frontend no respondió, pero puede estar iniciando...")
            
            print("\n🎉 SERVICIOS INICIADOS")
            print("-" * 50)
            print("🔧 Backend: http://localhost:8001")
            print("🎨 Frontend: http://localhost:3000")
            print("📖 API Docs: http://localhost:8001/docs")
            print("\n💡 Presiona Ctrl+C para detener los servicios")
            
            # Mantener servicios ejecutándose
            try:
                while True:
                    # Verificar si los procesos siguen activos
                    if self.backend_process.poll() is not None:
                        print("❌ Backend se detuvo inesperadamente")
                        break
                    if self.frontend_process.poll() is not None:
                        print("❌ Frontend se detuvo inesperadamente")
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Deteniendo servicios...")
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando servicios: {e}")
            return False
        finally:
            self.cleanup()
    
    def start_backend_only(self):
        """Iniciar solo el backend"""
        print("\n🔧 INICIANDO SOLO BACKEND...")
        
        try:
            backend_dir = self.base_dir / "backend"
            os.chdir(backend_dir)
            
            # Iniciar backend
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "server:app",
                "--host", "0.0.0.0",
                "--port", "8001",
                "--reload"
            ])
            
        except KeyboardInterrupt:
            print("\n🛑 Backend detenido")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def start_frontend_only(self):
        """Iniciar solo el frontend"""
        print("\n🎨 INICIANDO SOLO FRONTEND...")
        
        try:
            frontend_dir = self.base_dir / "frontend"
            os.chdir(frontend_dir)
            
            # Verificar que existan las dependencias
            if not (frontend_dir / "node_modules").exists():
                print("📦 Instalando dependencias...")
                subprocess.run(["yarn", "install"], check=True)
            
            # Iniciar frontend
            subprocess.run(["yarn", "start"])
            
        except KeyboardInterrupt:
            print("\n🛑 Frontend detenido")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def initialize_system(self):
        """Inicializar sistema completo"""
        print("\n⚙️  INICIALIZANDO SISTEMA COMPLETO...")
        
        try:
            os.chdir(self.base_dir)
            result = subprocess.run([sys.executable, "initialize_system.py"])
            
            if result.returncode == 0:
                print("✅ Sistema inicializado exitosamente")
            else:
                print("❌ Error en inicialización")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def admin_panel(self):
        """Abrir panel de administración"""
        print("\n🛠️  ABRIENDO PANEL DE ADMINISTRACIÓN...")
        
        try:
            os.chdir(self.base_dir)
            subprocess.run([sys.executable, "admin_system.py"])
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def testing_system(self):
        """Abrir sistema de testing"""
        print("\n🧪 ABRIENDO SISTEMA DE TESTING...")
        
        try:
            os.chdir(self.base_dir)
            subprocess.run([sys.executable, "testing_system.py"])
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def quick_diagnostics(self):
        """Diagnósticos rápidos"""
        print("\n📊 DIAGNÓSTICOS RÁPIDOS")
        print("-" * 40)
        
        # Test 1: Archivos principales
        print("🔍 Verificando archivos principales...")
        key_files = [
            "backend/server.py",
            "backend/config.py", 
            "backend/data/bebidas.json",
            "backend/data/preguntas.json",
            "frontend/src/App.js",
            "frontend/package.json"
        ]
        
        for file_path in key_files:
            full_path = self.base_dir / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path}")
        
        # Test 2: Dependencias Python
        print("\n🐍 Verificando dependencias Python...")
        try:
            import fastapi, uvicorn, motor, sklearn, pandas, numpy
            print("   ✅ Dependencias principales instaladas")
        except ImportError as e:
            print(f"   ❌ Falta dependencia: {e}")
        
        # Test 3: Variables de entorno
        print("\n🔧 Verificando configuración...")
        env_file = self.base_dir / "backend" / ".env"
        if env_file.exists():
            print("   ✅ Archivo .env existe")
            
            # Verificar contenido básico
            content = env_file.read_text()
            if "MONGO_URL" in content and "DB_NAME" in content:
                print("   ✅ Variables de entorno configuradas")
            else:
                print("   ❌ Variables de entorno incompletas")
        else:
            print("   ❌ Archivo .env no encontrado")
        
        # Test 4: Puertos disponibles
        print("\n🔌 Verificando puertos...")
        try:
            import socket
            
            # Test puerto 8001 (backend)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8001))
            if result == 0:
                print("   🟡 Puerto 8001 (backend) en uso")
            else:
                print("   ✅ Puerto 8001 (backend) disponible")
            sock.close()
            
            # Test puerto 3000 (frontend)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 3000))
            if result == 0:
                print("   🟡 Puerto 3000 (frontend) en uso")
            else:
                print("   ✅ Puerto 3000 (frontend) disponible")
            sock.close()
            
        except Exception as e:
            print(f"   ❌ Error verificando puertos: {e}")
    
    def system_status(self):
        """Mostrar estado del sistema"""
        print("\n📋 ESTADO DEL SISTEMA")
        print("-" * 40)
        
        # Verificar servicios
        print("🔍 Verificando servicios...")
        try:
            import requests
            
            # Backend
            try:
                response = requests.get("http://localhost:8001/status", timeout=3)
                if response.status_code == 200:
                    print("   ✅ Backend activo (http://localhost:8001)")
                else:
                    print("   🟡 Backend responde pero con error")
            except:
                print("   ❌ Backend no accesible")
            
            # Frontend
            try:
                response = requests.get("http://localhost:3000", timeout=3)
                if response.status_code == 200:
                    print("   ✅ Frontend activo (http://localhost:3000)")
                else:
                    print("   🟡 Frontend responde pero con error")
            except:
                print("   ❌ Frontend no accesible")
                
        except ImportError:
            print("   ❌ Módulo 'requests' no disponible")
        
        # Información del sistema
        print(f"\n💻 Información del sistema:")
        print(f"   Python: {sys.version}")
        print(f"   Directorio: {self.base_dir}")
        print(f"   Scripts disponibles:")
        scripts = [
            "initialize_system.py",
            "admin_system.py", 
            "testing_system.py",
            "fix_bebidas_structure.py"
        ]
        for script in scripts:
            if (self.base_dir / script).exists():
                print(f"     ✅ {script}")
            else:
                print(f"     ❌ {script}")
    
    def check_dependencies(self):
        """Verificar dependencias básicas"""
        try:
            # Backend dependencies
            import fastapi, uvicorn, motor
            
            # Frontend check
            frontend_dir = self.base_dir / "frontend"
            if not (frontend_dir / "package.json").exists():
                print("❌ Frontend no configurado correctamente")
                return False
            
            # Check if yarn is available
            result = subprocess.run(["yarn", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Yarn no está instalado")
                return False
            
            return True
            
        except ImportError as e:
            print(f"❌ Falta dependencia Python: {e}")
            return False
    
    def run(self):
        """Ejecutar gestor principal"""
        os.chdir(self.base_dir)
        
        print("🤖 RefrescoBot ML - Gestor del Sistema")
        print(f"📁 Directorio: {self.base_dir}")
        
        try:
            while True:
                self.show_main_menu()
                choice = input("\nSelecciona una opción: ")
                
                if choice == "1":
                    self.quick_start()
                elif choice == "2":
                    self.start_backend_only()
                elif choice == "3":
                    self.start_frontend_only()
                elif choice == "4":
                    self.initialize_system()
                elif choice == "5":
                    self.admin_panel()
                elif choice == "6":
                    self.testing_system()
                elif choice == "7":
                    self.quick_diagnostics()
                elif choice == "8":
                    self.system_status()
                elif choice == "9":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida")
                
                if choice not in ["1", "2", "3"]:  # No pausar para servicios que siguen ejecutándose
                    input("\nPresiona Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n👋 Gestor cerrado por el usuario")
        finally:
            self.cleanup()

def main():
    """Función principal"""
    manager = RefrescoBotManager()
    manager.run()

if __name__ == "__main__":
    main()