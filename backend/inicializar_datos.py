#!/usr/bin/env python3
"""
Script para inicializar la base de datos de RefrescoBot con datos de ejemplo
Ejecutar: python inicializar_datos.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
import uuid
from datetime import datetime

# Cargar variables de entorno
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def inicializar_base_datos():
    """Inicializa la base de datos con datos de ejemplo"""
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"🔗 Conectando a MongoDB Atlas: {db_name}")
    
    # Ensure we're using UUIDs for all IDs
    def create_uuid():
        return str(uuid.uuid4())
    
    # ===== CREAR PREGUNTAS =====
    print("📝 Creando preguntas...")
    
    preguntas = [
        # PREGUNTA FIJA (OBLIGATORIA) - Sobre consumo de refrescos
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Con qué frecuencia tomas refrescos normalmente?",
            "opciones": [
                "Diariamente, me encantan los refrescos",
                "Varias veces por semana",
                "Ocasionalmente, en fiestas o reuniones",
                "Muy raramente, prefiero otras bebidas",
                "Nunca, no me gustan los refrescos"
            ],
            "es_fija": True,
            "peso_algoritmo": 3.0,
            "categoria": "preferencias",
            "created_at": datetime.utcnow()
        },
        
        # PREGUNTAS ALEATORIAS - Rutinas
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Cómo describirías tu nivel de actividad física hoy?",
            "opciones": [
                "Muy activo, hice ejercicio intenso",
                "Activo, caminé bastante o hice ejercicio ligero",
                "Moderado, actividades normales del día",
                "Poco activo, día tranquilo en casa",
                "Sedentario, casi no me moví en todo el día"
            ],
            "es_fija": False,
            "peso_algoritmo": 2.0,
            "categoria": "rutina",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Cómo ha sido tu día en términos de estrés?",
            "opciones": [
                "Muy relajado, día perfecto",
                "Tranquilo, sin mayores complicaciones",
                "Normal, con los típicos altibajos",
                "Algo estresante, con varios desafíos",
                "Muy estresante, día muy complicado"
            ],
            "es_fija": False,
            "peso_algoritmo": 2.5,
            "categoria": "estado_animo",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Qué tiempo hace hoy donde te encuentras?",
            "opciones": [
                "Muy caluroso, hace mucho calor",
                "Cálido, temperatura agradable pero alta",
                "Templado, clima perfecto",
                "Fresco, un poco frío pero agradable",
                "Frío, necesito algo que me caliente"
            ],
            "es_fija": False,
            "peso_algoritmo": 2.0,
            "categoria": "temporal",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Cuál es tu sabor favorito en general?",
            "opciones": [
                "Dulce, me encantan los sabores azucarados",
                "Cítrico, limón, naranja, lima",
                "Refrescante, menta, hierbabuena",
                "Natural, sabores suaves y puros",
                "Amargo o fuerte, café, té sin azúcar"
            ],
            "es_fija": False,
            "peso_algoritmo": 2.5,
            "categoria": "preferencias",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Cuál es tu color favorito?",
            "opciones": [
                "Rojo, color intenso y energético",
                "Azul, tranquilo y refrescante",
                "Verde, natural y relajante",
                "Amarillo/Naranja, alegre y vibrante",
                "Colores neutros, blanco, negro, gris"
            ],
            "es_fija": False,
            "peso_algoritmo": 1.5,
            "categoria": "preferencias",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Cómo te sientes físicamente en este momento?",
            "opciones": [
                "Con mucha energía y vitalidad",
                "Bien, con energía normal",
                "Neutral, ni muy energético ni cansado",
                "Un poco cansado, necesito un boost",
                "Muy cansado, sin energía"
            ],
            "es_fija": False,
            "peso_algoritmo": 2.0,
            "categoria": "fisico",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Qué hiciste principalmente hoy?",
            "opciones": [
                "Trabajé o estudié intensamente",
                "Actividades normales de trabajo/estudio",
                "Tareas del hogar y actividades cotidianas",
                "Descansar, ver TV, tiempo libre",
                "Socializar, estar con amigos/familia"
            ],
            "es_fija": False,
            "peso_algoritmo": 1.8,
            "categoria": "rutina",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Cuál es tu estado de ánimo actual?",
            "opciones": [
                "Muy feliz y emocionado",
                "Contento y de buen humor",
                "Tranquilo y relajado",
                "Un poco decaído o melancólico",
                "Triste o con ganas de consentirme"
            ],
            "es_fija": False,
            "peso_algoritmo": 2.2,
            "categoria": "estado_animo",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Qué tanto te gustan las burbujas en las bebidas?",
            "opciones": [
                "Me encantan, entre más gas mejor",
                "Me gustan, pero no necesariamente",
                "Me da igual, con o sin gas",  
                "Prefiero bebidas sin gas",
                "No me gustan nada las bebidas gaseosas"
            ],
            "es_fija": False,
            "peso_algoritmo": 2.5,
            "categoria": "preferencias",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Cuánta azúcar prefieres en tus bebidas?",
            "opciones": [
                "Muy dulce, me gusta mucha azúcar",
                "Dulce, pero no excesivo",
                "Punto medio, ni muy dulce ni sin azúcar",
                "Poco dulce, prefiero sabores naturales",
                "Sin azúcar, prefiero opciones saludables"
            ],
            "es_fija": False,
            "peso_algoritmo": 2.8,
            "categoria": "preferencias",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Cómo dormiste anoche?",
            "opciones": [
                "Excelente, me desperté súper descansado",
                "Bien, dormí las horas necesarias",
                "Regular, desperté algunas veces",
                "Mal, no dormí lo suficiente",
                "Terrible, casi no pude dormir"
            ],
            "es_fija": False,
            "peso_algoritmo": 1.5,
            "categoria": "fisico",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Qué tan aventurero eres con sabores nuevos?",
            "opciones": [
                "Muy aventurero, me gusta probar todo",
                "Adventurero, pero con cuidado",
                "Moderado, algunos sabores nuevos sí",
                "Conservador, prefiero lo conocido",
                "Nada adventurero, solo mis favoritos"
            ],
            "es_fija": False,
            "peso_algoritmo": 2.0,
            "categoria": "preferencias",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Qué momento del día es?",
            "opciones": [
                "Mañana temprano, empezando el día",
                "Media mañana, ya en actividades",
                "Mediodía/tarde, en plena actividad",
                "Tarde-noche, terminando actividades",
                "Noche, tiempo de relajarse"
            ],
            "es_fija": False,
            "peso_algoritmo": 1.8,
            "categoria": "temporal",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "texto": "¿Cómo te gusta celebrar los buenos momentos?",
            "opciones": [
                "Con algo especial y diferente",
                "Con algo rico que me guste mucho",
                "Simple, pero que me haga feliz",
                "Tranquilo, sin muchas complicaciones",
                "Prefiero celebrar de otras formas"
            ],
            "es_fija": False,
            "peso_algoritmo": 1.7,
            "categoria": "estado_animo",
            "created_at": datetime.utcnow()
        }
    ]
    
    # Limpiar colección de preguntas existente
    await db.preguntas.delete_many({})
    
    # Insertar preguntas
    await db.preguntas.insert_many(preguntas)
    print(f"✅ Creadas {len(preguntas)} preguntas (1 fija + {len(preguntas)-1} aleatorias)")
    
    # ===== CREAR BEBIDAS =====
    print("🥤 Creando bebidas...")
    
    bebidas = [
        # REFRESCOS CLÁSICOS
        {
            "id": str(uuid.uuid4()),
            "nombre": "Coca-Cola Clásica",
            "descripcion_base": "El refresco de cola clásico y original que ha conquistado el mundo.",
            "presentaciones": [
                {
                    "ml": 355,
                    "precio": 25.00,
                    "imagen_local": "/static/images/bebidas/coca_cola_355.webp",
                    "descripcion_presentacion": "Lata perfecta para el día a día. Ideal para comidas o meriendas."
                },
                {
                    "ml": 500,
                    "precio": 30.00,
                    "imagen_local": "/static/images/bebidas/coca_cola_500.webp", 
                    "descripcion_presentacion": "Botella personal de plástico. Perfecta para llevar y compartir."
                },
                {
                    "ml": 600,
                    "precio": 35.00,
                    "imagen_local": "/static/images/bebidas/coca_cola_600.webp",
                    "descripcion_presentacion": "Botella familiar pequeña. Ideal para acompañar comidas en casa."
                },
                {
                    "ml": 1000,
                    "precio": 45.00,
                    "imagen_local": "/static/images/bebidas/coca_cola_1000.webp",
                    "descripcion_presentacion": "Botella de 1 litro. Perfecta para familia o reuniones pequeñas."
                },
                {
                    "ml": 2000,
                    "precio": 65.00,
                    "imagen_local": "/static/images/bebidas/coca_cola_2000.webp",
                    "descripcion_presentacion": "Botella familiar de 2 litros. Ideal para fiestas y reuniones grandes."
                }
            ],
            "tipo": "refresco",
            "es_carbonatada": True,
            "es_azucarada": True,
            "sabor_principal": "cola",
            "puntuacion_promedio": 0.0,
            "total_puntuaciones": 0,
            "es_refresco_real": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "nombre": "Pepsi",
            "descripcion_base": "Refresco de cola con un sabor único y refrescante que desafía lo convencional.",
            "presentaciones": [
                {
                    "ml": 355,
                    "precio": 24.00,
                    "imagen_local": "/static/images/bebidas/pepsi_355.webp",
                    "descripcion_presentacion": "Lata clásica con el sabor distintivo de Pepsi."
                },
                {
                    "ml": 500,
                    "precio": 29.00,
                    "imagen_local": "/static/images/bebidas/pepsi_500.webp",
                    "descripcion_presentacion": "Botella personal para disfrutar en cualquier momento."
                },
                {
                    "ml": 600,
                    "precio": 34.00,
                    "imagen_local": "/static/images/bebidas/pepsi_600.webp",
                    "descripcion_presentacion": "Botella mediana perfecta para compartir."
                },
                {
                    "ml": 1250,
                    "precio": 48.00,
                    "imagen_local": "/static/images/bebidas/pepsi_1250.webp",
                    "descripcion_presentacion": "Botella de 1.25L con más para disfrutar."
                },
                {
                    "ml": 2000,
                    "precio": 67.00,
                    "imagen_local": "/static/images/bebidas/pepsi_2000.webp",
                    "descripcion_presentacion": "Botella familiar grande para ocasiones especiales."
                }
            ],
            "tipo": "refresco",
            "es_carbonatada": True,
            "es_azucarada": True,
            "sabor_principal": "cola",
            "puntuacion_promedio": 0.0,
            "total_puntuaciones": 0,
            "es_refresco_real": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "nombre": "Sprite",
            "descripcion_base": "Refresco de lima-limón transparente y refrescante. Sin cafeína, pura frescura.",
            "presentaciones": [
                {
                    "ml": 355,
                    "precio": 23.00,
                    "imagen_local": "/static/images/bebidas/sprite_355.webp",
                    "descripcion_presentacion": "Lata refrescante con sabor cítrico natural."
                },
                {
                    "ml": 500,
                    "precio": 28.00,
                    "imagen_local": "/static/images/bebidas/sprite_500.webp",
                    "descripcion_presentacion": "Botella personal perfecta para hidratarse."
                },
                {
                    "ml": 600,
                    "precio": 33.00,
                    "imagen_local": "/static/images/bebidas/sprite_600.webp",
                    "descripcion_presentacion": "Botella familiar con más frescura cítrica."
                },
                {
                    "ml": 1000,
                    "precio": 44.00,
                    "imagen_local": "/static/images/bebidas/sprite_1000.webp",
                    "descripcion_presentacion": "1 litro de pura refrescancia para toda la familia."
                },
                {
                    "ml": 2000,
                    "precio": 64.00,
                    "imagen_local": "/static/images/bebidas/sprite_2000.webp",
                    "descripcion_presentacion": "Botella grande para fiestas y reuniones."
                }
            ],
            "tipo": "refresco",
            "es_carbonatada": True,
            "es_azucarada": True,
            "sabor_principal": "limon",
            "puntuacion_promedio": 0.0,
            "total_puntuaciones": 0,
            "es_refresco_real": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "nombre": "Fanta Naranja",
            "descripcion_base": "Refresco de naranja con sabor frutal intenso y color vibrante.",
            "presentaciones": [
                {
                    "ml": 355,
                    "precio": 23.00,
                    "imagen_local": "/static/images/bebidas/fanta_355.webp",
                    "descripcion_presentacion": "Lata con el sabor explosivo de naranja."
                },
                {
                    "ml": 500,
                    "precio": 28.00,
                    "imagen_local": "/static/images/bebidas/fanta_500.webp",
                    "descripcion_presentacion": "Botella personal con más diversión naranja."
                },
                {
                    "ml": 600,
                    "precio": 33.00,
                    "imagen_local": "/static/images/bebidas/fanta_600.webp",
                    "descripcion_presentacion": "Tamaño perfecto para disfrutar en familia."
                },
                {
                    "ml": 1000,
                    "precio": 44.00,
                    "imagen_local": "/static/images/bebidas/fanta_1000.webp",
                    "descripcion_presentacion": "1 litro de sabor frutal para todos."
                },
                {
                    "ml": 2000,
                    "precio": 64.00,
                    "imagen_local": "/static/images/bebidas/fanta_2000.webp",
                    "descripcion_presentacion": "Botella familiar para fiestas coloridas."
                }
            ],
            "tipo": "refresco",
            "es_carbonatada": True,
            "es_azucarada": True,
            "sabor_principal": "naranja",
            "puntuacion_promedio": 0.0,
            "total_puntuaciones": 0,
            "es_refresco_real": True,
            "created_at": datetime.utcnow()
        },
        
        # AGUAS Y BEBIDAS SALUDABLES (ALTERNATIVAS)
        {
            "id": str(uuid.uuid4()),
            "nombre": "Agua Mineral Topo Chico",
            "descripcion_base": "Agua mineral natural con gas, directa de manantiales mexicanos.",
            "presentaciones": [
                {
                    "ml": 355,
                    "precio": 18.00,
                    "imagen_local": "/static/images/bebidas/topo_chico_355.webp",
                    "descripcion_presentacion": "Botella icónica de vidrio con mineralización perfecta."
                },
                {
                    "ml": 500,
                    "precio": 22.00,
                    "imagen_local": "/static/images/bebidas/topo_chico_500.webp",
                    "descripcion_presentacion": "Más agua mineral para una hidratación completa."
                },
                {
                    "ml": 1000,
                    "precio": 35.00,
                    "imagen_local": "/static/images/bebidas/topo_chico_1000.webp",
                    "descripcion_presentacion": "Botella familiar de agua mineral premium."
                }
            ],
            "tipo": "agua",
            "es_carbonatada": True,
            "es_azucarada": False,
            "sabor_principal": "agua",
            "puntuacion_promedio": 0.0,
            "total_puntuaciones": 0,
            "es_refresco_real": False,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "nombre": "Agua Natural Bonafont",
            "descripcion_base": "Agua purificada natural, la opción más saludable para tu hidratación diaria.",
            "presentaciones": [
                {
                    "ml": 500,
                    "precio": 15.00,
                    "imagen_local": "/static/images/bebidas/bonafont_500.webp",
                    "descripcion_presentacion": "Botella personal de agua pura y cristalina."
                },
                {
                    "ml": 1000,
                    "precio": 20.00,
                    "imagen_local": "/static/images/bebidas/bonafont_1000.webp",
                    "descripcion_presentacion": "1 litro de hidratación saludable."
                },
                {
                    "ml": 1500,
                    "precio": 25.00,
                    "imagen_local": "/static/images/bebidas/bonafont_1500.webp",
                    "descripcion_presentacion": "Botella grande para hidratación prolongada."
                }
            ],
            "tipo": "agua",
            "es_carbonatada": False,
            "es_azucarada": False,
            "sabor_principal": "agua",
            "puntuacion_promedio": 0.0,
            "total_puntuaciones": 0,
            "es_refresco_real": False,
            "created_at": datetime.utcnow()
        },
        
        # JUGOS Y BEBIDAS FRUTALES (ALTERNATIVAS)
        {
            "id": str(uuid.uuid4()),
            "nombre": "Jugo Del Valle Naranja",
            "descripcion_base": "Jugo de naranja natural con vitamina C, sabor auténtico de fruta.",
            "presentaciones": [
                {
                    "ml": 400,
                    "precio": 28.00,
                    "imagen_local": "/static/images/bebidas/del_valle_400.webp",
                    "descripcion_presentacion": "Tetra pack personal con 100% jugo de naranja."
                },
                {
                    "ml": 1000,
                    "precio": 45.00,
                    "imagen_local": "/static/images/bebidas/del_valle_1000.webp",
                    "descripcion_presentacion": "1 litro de jugo natural para toda la familia."
                }
            ],
            "tipo": "jugo",
            "es_carbonatada": False,
            "es_azucarada": True,
            "sabor_principal": "naranja",
            "puntuacion_promedio": 0.0,
            "total_puntuaciones": 0,
            "es_refresco_real": False,
            "created_at": datetime.utcnow()
        },
        
        # BEBIDAS SIN AZÚCAR (REFRESCOS ESPECIALES)
        {
            "id": str(uuid.uuid4()),
            "nombre": "Coca-Cola Zero",
            "descripcion_base": "Todo el sabor de Coca-Cola sin azúcar ni calorías. Cero compromisos.",
            "presentaciones": [
                {
                    "ml": 355,
                    "precio": 25.00,
                    "imagen_local": "/static/images/bebidas/coca_zero_355.webp",
                    "descripcion_presentacion": "Lata con sabor original pero sin calorías."
                },
                {
                    "ml": 500,
                    "precio": 30.00,
                    "imagen_local": "/static/images/bebidas/coca_zero_500.webp",
                    "descripcion_presentacion": "Botella personal para cuidar tu línea."
                },
                {
                    "ml": 600,
                    "precio": 35.00,
                    "imagen_local": "/static/images/bebidas/coca_zero_600.webp",
                    "descripcion_presentacion": "Más sabor sin azúcar para disfrutar sin culpa."
                }
            ],
            "tipo": "refresco",
            "es_carbonatada": True,
            "es_azucarada": False,
            "sabor_principal": "cola",
            "puntuacion_promedio": 0.0,
            "total_puntuaciones": 0,
            "es_refresco_real": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    # Limpiar colección de bebidas existente
    await db.bebidas.delete_many({})
    
    # Insertar bebidas
    await db.bebidas.insert_many(bebidas)
    print(f"✅ Creadas {len(bebidas)} bebidas variadas")
    
    # ===== LIMPIAR SESIONES ANTERIORES =====
    await db.sesiones.delete_many({})
    print("🧹 Limpieza de sesiones anteriores completada")
    
    # ===== VERIFICAR CONEXIÓN =====
    print("\n🔍 Verificando conexión y datos...")
    
    total_preguntas = await db.preguntas.count_documents({})
    total_bebidas = await db.bebidas.count_documents({})
    pregunta_fija = await db.preguntas.count_documents({"es_fija": True})
    
    print(f"📊 Resumen de la base de datos:")
    print(f"   • Total de preguntas: {total_preguntas}")
    print(f"   • Pregunta fija: {pregunta_fija}")
    print(f"   • Preguntas aleatorias: {total_preguntas - pregunta_fija}")
    print(f"   • Total de bebidas: {total_bebidas}")
    
    # Mostrar distribución de bebidas por tipo
    tipos_bebidas = await db.bebidas.aggregate([
        {"$group": {"_id": "$tipo", "count": {"$sum": 1}}}
    ]).to_list(1000)
    
    print(f"   • Distribución por tipo:")
    for tipo in tipos_bebidas:
        print(f"     - {tipo['_id']}: {tipo['count']} bebidas")
    
    client.close()
    print(f"\n🎉 ¡Base de datos '{db_name}' inicializada exitosamente!")
    print(f"🚀 Ya puedes usar RefrescoBot ML")

if __name__ == "__main__":
    asyncio.run(inicializar_base_datos())