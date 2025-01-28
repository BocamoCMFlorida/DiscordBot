import discord
from discord.ui import Button, View
from discord.interactions import Interaction
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import datetime
from datetime import datetime, timedelta
import json
from typing import Dict, Optional, List, Any
import uuid
import os
from discord.ext import commands, tasks
def tiene_rol_dictador():
    async def predicate(interaction: discord.Interaction) -> bool:
        rol_dictador = discord.utils.get(interaction.guild.roles, name="Dictador")
        if rol_dictador is None:
            await interaction.response.send_message("El rol 'Dictador' no existe en este servidor.", ephemeral=True)
            return False
        return rol_dictador in interaction.user.roles
    return app_commands.check(predicate)
def get_multiplier_text(user_id: int) -> tuple[float, str]:
    inventario = sistema_objetos.obtener_inventario(user_id)
    multiplicadores = inventario.obtener_efectos_activos("multiplicador")
    if multiplicadores:
        return multiplicadores[0].valor, f" (¡multiplicador x{multiplicadores[0].valor} activo!)"
    return 1.0, ""
class EconomySystem:
    def __init__(self, filename: str = "economy.json"):
        self.filename = filename
        self.accounts = self.load_accounts()

    def load_accounts(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_accounts(self):
        with open(self.filename, 'w') as f:
            json.dump(self.accounts, f)

    def get_balance(self, user_id: str):
        return self.accounts.get(str(user_id), 0)

    def add_money(self, user_id: str, amount: int, check_multiplier: bool = True):
        if check_multiplier:
            # Verificar multiplicador activo
            inventario = sistema_objetos.obtener_inventario(int(user_id))
            multiplicadores = inventario.obtener_efectos_activos("multiplicador")
            
            if multiplicadores:
                multiplicador = multiplicadores[0].valor
                amount = int(amount * multiplicador)
        
        self.accounts[str(user_id)] = self.get_balance(user_id) + amount
        self.save_accounts()
        return amount  # Retornamos la cantidad final añadida

    def remove_money(self, user_id: str, amount: int):
        if self.get_balance(user_id) >= amount:
            self.accounts[str(user_id)] = self.get_balance(user_id) - amount
            self.save_accounts()
            return True
        return False

class JobSystem:
    def __init__(self):
        self.jobs = {
            # Trabajos básicos
            "minero": {
                "min": 100,
                "max": 200,
                "description": "Trabajas como minero, extrayendo minerales.",
                "cooldown_minutes": 15
            },
            "pescador": {
                "min": 50,
                "max": 150,
                "description": "Sales a pescar y traes una buena captura.",
                "cooldown_minutes": 10
            },
            "programador": {
                "min": 200,
                "max": 400,
                "description": "Creas código y resuelves problemas.",
                "cooldown_minutes": 30
            },
            
            # Nuevos trabajos
            "chef": {
                "min": 150,
                "max": 300,
                "description": "Cocinas deliciosos platillos en un restaurante.",
                "cooldown_minutes": 20
            },
            "astronomo": {
                "min": 300,
                "max": 600,
                "description": "Estudias las estrellas y descubres nuevos planetas.",
                "cooldown_minutes": 45
            },
            "cazador": {
                "min": 175,
                "max": 350,
                "description": "Te adentras en el bosque en busca de presas.",
                "cooldown_minutes": 25
            },
            "alquimista": {
                "min": 250,
                "max": 500,
                "description": "Creas pociones y elixires mágicos.",
                "cooldown_minutes": 35
            },
            "arqueólogo": {
                "min": 400,
                "max": 800,
                "description": "Exploras ruinas antiguas en busca de tesoros.",
                "cooldown_minutes": 60
            },
            "mercader": {
                "min": 125,
                "max": 250,
                "description": "Comercias con bienes en el mercado local.",
                "cooldown_minutes": 18
            },
            "inventor": {
                "min": 350,
                "max": 700,
                "description": "Creas ingeniosos aparatos y máquinas.",
                "cooldown_minutes": 50
            },
            "guardián": {
                "min": 200,
                "max": 400,
                "description": "Proteges la ciudad de peligros.",
                "cooldown_minutes": 30
            },
            "mago": {
                "min": 275,
                "max": 550,
                "description": "Realizas trucos de magia para entretener.",
                "cooldown_minutes": 40
            },
            "granjero": {
                "min": 150,
                "max": 300,
                "description": "Cultivas y cosechas productos frescos.",
                "cooldown_minutes": 20
            },
            "artista": {
                "min": 225,
                "max": 450,
                "description": "Creas hermosas obras de arte.",
                "cooldown_minutes": 35
            }
        }
        self.user_cooldowns = {}
        self.special_events = {
            "lluvia_de_oro": {"boost": 2.0, "chance": 0.1},
            "crisis_economica": {"boost": 0.5, "chance": 0.05},
            "festival": {"boost": 1.5, "chance": 0.15},
            "luna_llena": {"boost": 1.8, "chance": 0.08}
        }

    def get_job_bonus(self, job_name: str) -> float:
        """Calcula bonus especiales basados en condiciones"""
        bonus = 1.0
        
        # Eventos aleatorios
        for event, data in self.special_events.items():
            if random.random() < data["chance"]:
                bonus *= data["boost"]
                return bonus, f"¡{event.replace('_', ' ').title()}! (x{data['boost']})"
        
        # Bonus por hora del día
        hora_actual = datetime.now().hour
        if 22 <= hora_actual or hora_actual < 4:  # Trabajo nocturno
            bonus *= 1.3
            return bonus, "¡Bonus nocturno! (x1.3)"
        
        return bonus, ""

    def perform_job(self, user_id: str, job_name: str, economy: EconomySystem, sistema_objetos) -> tuple[int, str]:
        if not self.can_work(user_id, job_name):
            return 0, ""
            
        job = self.jobs[job_name]
        base_earnings = random.randint(job["min"], job["max"])
        
        # Obtener bonus del trabajo
        bonus, bonus_message = self.get_job_bonus(job_name)
        earnings = int(base_earnings * bonus)
        
        # Verificar multiplicador activo del inventario
        inventario = sistema_objetos.obtener_inventario(int(user_id))
        multiplicadores = inventario.obtener_efectos_activos("multiplicador")
        
        # Aplicar multiplicador si existe
        if multiplicadores:
            multiplicador = multiplicadores[0].valor
            earnings = int(earnings * multiplicador)
        
        # Actualizar cooldown
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = {}
        self.user_cooldowns[user_id][job_name] = datetime.now()
        
        # Probabilidad de encuentro especial (5%)
        encuentro_especial = ""
        if random.random() < 0.05:
            recompensas_especiales = [
                ("💎 ¡Has encontrado una gema brillante!", 500),
                ("📜 ¡Has descubierto un pergamino antiguo!", 400),
                ("🏺 ¡Has desenterrado una reliquia!", 600),
                ("🗝️ ¡Has encontrado una llave misteriosa!", 300),
                ("📱 ¡Has encontrado un dispositivo extraño!", 450)
            ]
            encuentro, bonus_extra = random.choice(recompensas_especiales)
            earnings += bonus_extra
            encuentro_especial = f"\n{encuentro} +{bonus_extra} monedas"
        
        economy.add_money(user_id, earnings)
        return earnings, bonus_message + encuentro_especial
class Efecto:
    def __init__(self, 
             tipo: str, 
             valor: Any, 
             duracion: Optional[int] = None, 
             apilable: bool = False):
        self.id = str(uuid.uuid4())
        self.tipo = tipo
        self.valor = valor
        self.tiempo_inicio = datetime.now()
        self.duracion = duracion
        self.apilable = apilable

    def esta_activo(self) -> bool:
        if self.duracion is None:
            return True
        return datetime.now() < self.tiempo_inicio + timedelta(seconds=self.duracion)

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "valor": self.valor,
            "tiempo_inicio": self.tiempo_inicio.isoformat(),
            "duracion": self.duracion,
            "apilable": self.apilable
        }

    @classmethod
    def from_dict(cls, data):
        efecto = cls(
            data["tipo"],
            data["valor"],
            data["duracion"],
            data["apilable"]
        )
        efecto.id = data["id"]
        efecto.tiempo_inicio = datetime.fromisoformat(data["tiempo_inicio"])
        return efecto

class Objeto:
    def __init__(self, 
                 nombre: str, 
                 descripcion: str, 
                 precio: int, 
                 efectos: List[Efecto], 
                 emoji: str = None,
                 max_apilamiento: int = 1, 
                 consumible: bool = True):
        self.id = str(uuid.uuid4())
        self.nombre = nombre.lower()
        self.descripcion = descripcion
        self.precio = precio
        self.efectos = efectos
        self.emoji = emoji
        self.max_apilamiento = max_apilamiento
        self.consumible = consumible

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "efectos": [efecto.to_dict() for efecto in self.efectos],
            "emoji": self.emoji,
            "max_apilamiento": self.max_apilamiento,
            "consumible": self.consumible
        }

    @classmethod
    def from_dict(cls, data):
        efectos = [Efecto.from_dict(efecto_data) for efecto_data in data["efectos"]]
        objeto = cls(
            data["nombre"],
            data["descripcion"],
            data["precio"],
            efectos,
            data["emoji"],
            data["max_apilamiento"],
            data["consumible"]
        )
        objeto.id = data["id"]
        return objeto

class Mascota:
    def __init__(self, nombre: str, tipo: str):
        self.nombre = nombre
        self.tipo = tipo
        self.nivel = 1
        self.exp = 0
        self.hambre = 100
        self.felicidad = 100
        self.ultima_comida = datetime.now()
        self.ultima_caricia = datetime.now()

    def exp_necesaria(self) -> int:
        return self.nivel * 100

    def puede_subir_nivel(self) -> bool:
        return self.exp >= self.exp_necesaria()

    def subir_nivel(self) -> bool:
        if self.puede_subir_nivel():
            self.exp -= self.exp_necesaria()
            self.nivel += 1
            return True
        return False

    def actualizar_estado(self):
        tiempo_sin_comer = (datetime.now() - self.ultima_comida).total_seconds() / 3600
        tiempo_sin_caricias = (datetime.now() - self.ultima_caricia).total_seconds() / 3600

        self.hambre = max(0, self.hambre - tiempo_sin_comer * 5)
        self.felicidad = max(0, self.felicidad - tiempo_sin_caricias * 2)

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "tipo": self.tipo,
            "nivel": self.nivel,
            "exp": self.exp,
            "hambre": self.hambre,
            "felicidad": self.felicidad,
            "ultima_comida": self.ultima_comida.isoformat(),
            "ultima_caricia": self.ultima_caricia.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict):
        mascota = cls(data["nombre"], data["tipo"])
        mascota.nivel = data["nivel"]
        mascota.exp = data["exp"]
        mascota.hambre = data["hambre"]
        mascota.felicidad = data["felicidad"]
        mascota.ultima_comida = datetime.fromisoformat(data["ultima_comida"])
        mascota.ultima_caricia = datetime.fromisoformat(data["ultima_caricia"])
        return mascota
class SistemaMascotas:
    def __init__(self, filename: str = "mascotas.json"):
        self.filename = filename
        self.mascotas = {}
        self.tipos = {
            "perro": {"precio": 1000, "bonus_exp": 1.2},
            "gato": {"precio": 1000, "bonus_monedas": 1.2},
            "dragon": {"precio": 5000, "bonus_exp": 1.5, "bonus_monedas": 1.5}
        }
        self.load_data()

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.mascotas = {
                    user_id: Mascota.from_dict(mascota_data)
                    for user_id, mascota_data in data.items()
                }
        except FileNotFoundError:
            self.mascotas = {}

    def save_data(self):
        data = {
            user_id: mascota.to_dict()
            for user_id, mascota in self.mascotas.items()
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def crear_mascota(self, user_id: str, nombre: str, tipo: str) -> bool:
        if user_id in self.mascotas or tipo not in self.tipos:
            return False
        self.mascotas[user_id] = Mascota(nombre, tipo)
        self.save_data()
        return True

    def alimentar_mascota(self, user_id: str) -> bool:
        if user_id not in self.mascotas:
            return False
        mascota = self.mascotas[user_id]
        mascota.hambre = min(100, mascota.hambre + 30)
        mascota.ultima_comida = datetime.now()
        mascota.exp += 10
        self.save_data()
        return True

    def acariciar_mascota(self, user_id: str) -> bool:
        if user_id not in self.mascotas:
            return False
        mascota = self.mascotas[user_id]
        mascota.felicidad = min(100, mascota.felicidad + 20)
        mascota.ultima_caricia = datetime.now()
        mascota.exp += 5
        self.save_data()
        return True

class InventarioUsuario:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.objetos: Dict[str, Dict[str, Any]] = {}
        self.efectos_activos: Dict[str, List[Efecto]] = {}

    def agregar_objeto(self, objeto: Objeto, cantidad: int = 1) -> bool:
        if objeto.nombre not in self.objetos:
            self.objetos[objeto.nombre] = {
                "id": objeto.id,
                "nombre": objeto.nombre,
                "descripcion": objeto.descripcion,
                "precio": objeto.precio,
                "emoji": objeto.emoji,
                "cantidad": 0,
                "max_apilamiento": objeto.max_apilamiento,
                "consumible": objeto.consumible
            }
        
        nueva_cantidad = self.objetos[objeto.nombre]["cantidad"] + cantidad
        if nueva_cantidad > objeto.max_apilamiento:
            return False
        
        self.objetos[objeto.nombre]["cantidad"] = nueva_cantidad
        return True

    def obtener_efectos_activos(self, tipo_efecto: Optional[str] = None) -> List[Efecto]:
        if tipo_efecto:
            return [efecto for efecto in self.efectos_activos.get(tipo_efecto, []) 
                   if isinstance(efecto, Efecto) and efecto.esta_activo()]
        
        efectos_activos = []
        for lista_efectos in self.efectos_activos.values():
            efectos_activos.extend([efecto for efecto in lista_efectos 
                                  if isinstance(efecto, Efecto) and efecto.esta_activo()])
        
        return efectos_activos

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "objetos": self.objetos,
            "efectos_activos": {
                tipo: [efecto.to_dict() for efecto in efectos]
                for tipo, efectos in self.efectos_activos.items()
            }
        }

    def usar_objeto(self, objeto: Objeto) -> List[Efecto]:
        if objeto.nombre not in self.objetos or self.objetos[objeto.nombre]["cantidad"] < 1:
            return []

        # Reducir cantidad si es consumible
        if self.objetos[objeto.nombre]["consumible"]:
            self.objetos[objeto.nombre]["cantidad"] -= 1
            if self.objetos[objeto.nombre]["cantidad"] == 0:
                del self.objetos[objeto.nombre]

        efectos_aplicados = []
        
        # Verificar si hay un multiplicador de duración activo
        multiplicador_duracion = 1.0
        for efecto in self.obtener_efectos_activos("duracion_efectos"):
            multiplicador_duracion *= efecto.valor

        for efecto in objeto.efectos:
            # Crear nueva instancia del efecto
            duracion_ajustada = None
            if efecto.duracion:
                duracion_ajustada = int(efecto.duracion * multiplicador_duracion)

            nuevo_efecto = Efecto(
                tipo=efecto.tipo,
                valor=efecto.valor,
                duracion=duracion_ajustada,
                apilable=efecto.apilable
            )
            
            if efecto.tipo not in self.efectos_activos:
                self.efectos_activos[efecto.tipo] = []
                
            # Si el efecto es apilable o no hay efectos de este tipo
            if efecto.apilable or not self.efectos_activos[efecto.tipo]:
                self.efectos_activos[efecto.tipo].append(nuevo_efecto)
                efectos_aplicados.append(nuevo_efecto)

        return efectos_aplicados

    @classmethod
    def from_dict(cls, data):
        inventario = cls(data["user_id"])
        inventario.objetos = data.get("objetos", {})
        inventario.efectos_activos = {
            tipo: [Efecto.from_dict(efecto_data) for efecto_data in efectos]
            for tipo, efectos in data.get("efectos_activos", {}).items()
        }
        return inventario

class SistemaObjetos:
    def __init__(self, filename: str = "inventarios.json"):
        self.filename = filename
        self.objetos: Dict[str, Objeto] = {}
        self.inventarios: Dict[int, InventarioUsuario] = {}
        self.load_data()

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.inventarios = {
                    int(user_id): InventarioUsuario.from_dict(inv_data)
                    for user_id, inv_data in data.items()
                }
        except FileNotFoundError:
            self.inventarios = {}

    def save_data(self):
        data = {
            str(user_id): inventario.to_dict()
            for user_id, inventario in self.inventarios.items()
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def obtener_objeto(self, nombre: str) -> Optional[Objeto]:
        return self.objetos.get(nombre.lower())

    def crear_objeto(self, nombre: str, descripcion: str, precio: int,
                    efectos: List[Efecto], emoji: str = None,
                    max_apilamiento: int = 1, consumible: bool = True) -> Objeto:
        objeto = Objeto(
            nombre, descripcion, precio, efectos, emoji,
            max_apilamiento, consumible
        )
        # Guardar el objeto usando el nombre como clave
        self.objetos[nombre.lower()] = objeto
        return objeto

    def obtener_inventario(self, user_id: int) -> InventarioUsuario:
        if user_id not in self.inventarios:
            self.inventarios[user_id] = InventarioUsuario(user_id)
            self.save_data()
        return self.inventarios[user_id]

    def agregar_objeto_a_inventario(self, user_id: int, nombre_objeto: str, cantidad: int = 1) -> bool:
        inventario = self.obtener_inventario(user_id)
        objeto = self.objetos.get(nombre_objeto.lower())
        if not objeto:
            return False
            
        if inventario.agregar_objeto(objeto, cantidad):
            self.save_data()
            return True
        return False

def inicializar_sistema_objetos() -> SistemaObjetos:
    sistema = SistemaObjetos()

    # Crear objetos para la tienda
    sistema.crear_objeto(
        nombre="multiplicador", 
        descripcion="Duplica tus ganancias por 1 hora", 
        precio=1500,
        efectos=[Efecto(tipo="multiplicador", valor=2, duracion=3600)],
        emoji="💰",
        max_apilamiento=1,
        consumible=True
    )
    
    sistema.crear_objeto(
        nombre="bolsa", 
        descripcion="Gana 500 monedas instantáneamente", 
        precio=800,
        efectos=[Efecto(tipo="monedas_instantaneas", valor=500, duracion=1)],
        emoji="💵",
        max_apilamiento=5,
        consumible=True
    )
     # Objetos de ganancia inmediata
    sistema.crear_objeto(
        nombre="cofre_pequeno",
        descripcion="Abre un cofre pequeño con 1000 monedas",
        precio=900,
        efectos=[Efecto(tipo="monedas_instantaneas", valor=1000, duracion=1)],
        emoji="📦",
        max_apilamiento=3,
        consumible=True
    )

    sistema.crear_objeto(
        nombre="cofre_grande",
        descripcion="Abre un cofre grande con 2500 monedas",
        precio=2000,
        efectos=[Efecto(tipo="monedas_instantaneas", valor=2500, duracion=1)],
        emoji="🎁",
        max_apilamiento=2,
        consumible=True
    )

    # Multiplicadores de diferentes niveles
    sistema.crear_objeto(
        nombre="multiplicador_mega",
        descripcion="Triplica tus ganancias por 30 minutos",
        precio=2500,
        efectos=[Efecto(tipo="multiplicador", valor=3, duracion=1800)],
        emoji="💎",
        max_apilamiento=1,
        consumible=True
    )

    sistema.crear_objeto(
        nombre="multiplicador_ultra",
        descripcion="Multiplica tus ganancias x5 por 15 minutos",
        precio=5000,
        efectos=[Efecto(tipo="multiplicador", valor=5, duracion=900)],
        emoji="⭐",
        max_apilamiento=1,
        consumible=True
    )

    # Objetos de protección
    sistema.crear_objeto(
        nombre="escudo",
        descripcion="Te protege contra robos durante 2 horas",
        precio=1000,
        efectos=[Efecto(tipo="proteccion_robo", valor=True, duracion=7200)],
        emoji="🛡️",
        max_apilamiento=1,
        consumible=True
    )

    # Objetos de recompensa diaria
    sistema.crear_objeto(
        nombre="amuleto_suerte",
        descripcion="Duplica tu recompensa diaria por 24 horas",
        precio=3000,
        efectos=[Efecto(tipo="multiplicador_daily", valor=2, duracion=86400)],
        emoji="🍀",
        max_apilamiento=1,
        consumible=True
    )

    # Objetos especiales
    sistema.crear_objeto(
        nombre="libro_experiencia",
        descripcion="Tu mascota gana el doble de experiencia por 1 hora",
        precio=2000,
        efectos=[Efecto(tipo="multiplicador_exp_mascota", valor=2, duracion=3600)],
        emoji="📚",
        max_apilamiento=2,
        consumible=True
    )

    sistema.crear_objeto(
        nombre="pocion_felicidad",
        descripcion="Aumenta la felicidad de tu mascota al máximo",
        precio=800,
        efectos=[Efecto(tipo="felicidad_mascota", valor=100, duracion=1)],
        emoji="🧪",
        max_apilamiento=3,
        consumible=True
    )

    sistema.crear_objeto(
        nombre="festin",
        descripcion="Alimenta por completo a tu mascota",
        precio=800,
        efectos=[Efecto(tipo="hambre_mascota", valor=100, duracion=1)],
        emoji="🍖",
        max_apilamiento=3,
        consumible=True
    )

    sistema.crear_objeto(
        nombre="talisman_trabajo",
        descripcion="Reduce todos los cooldowns de trabajo a la mitad por 1 hora",
        precio=2500,
        efectos=[Efecto(tipo="reduccion_cooldown", valor=0.5, duracion=3600)],
        emoji="⌛",
        max_apilamiento=1,
        consumible=True
    )

    sistema.crear_objeto(
        nombre="estrella_legendaria",
        descripcion="Todos los efectos positivos duran 50% más por 24 horas",
        precio=10000,
        efectos=[Efecto(tipo="duracion_efectos", valor=1.5, duracion=86400)],
        emoji="🌟",
        max_apilamiento=1,
        consumible=True
    )

    return sistema

    
class EventSystem:
    def __init__(self, bot):
        self.bot = bot
        self.evento_activo = None
        self.participantes = set()
        self.timer_task = None
        self.eventos_disponibles = [
            {
                "nombre": "lluvia_monedas",
                "titulo": "🌧️ ¡Lluvia de Monedas!",
                "descripcion": "¡Rápido! Escribe 'recoger' para obtener monedas aleatorias.",
                "duracion": 2,
                "comando": "recoger",
                "min_premio": 50,
                "max_premio": 200
            },
            {
                "nombre": "carrera_veloz",
                "titulo": "🏃 ¡Carrera Veloz!",
                "descripcion": "¡El primero en escribir 'correr' gana el premio!",
                "duracion": 1,
                "comando": "correr",
                "premio": 300
            },
            {
                "nombre": "cofre_tesoro",
                "titulo": "🎁 ¡Cofre del Tesoro!",
                "descripcion": "Escribe 'abrir' para intentar abrir el cofre. ¡Cuidado, podría estar trampeado!",
                "duracion": 2,
                "comando": "abrir",
                "min_premio": 100,
                "max_premio": 500,
                "trampa_probabilidad": 0.3
            },
            {
                "nombre": "invasion_zombies",
                "titulo": "🧟 ¡Invasión Zombie!",
                "descripcion": "¡Los zombies atacan! Escribe 'disparar' para eliminarlos y ganar monedas.",
                "duracion": 3,
                "comando": "disparar",
                "premio_por_zombie": 50
            },
            {
                "nombre": "loteria_flash",
                "titulo": "🎫 ¡Lotería Flash!",
                "descripcion": "¡Participa escribiendo 'ticket' para ganar el premio acumulado!",
                "duracion": 2,
                "comando": "ticket",
                "premio_base": 200,
                "premio_por_participante": 50
            }
        ]

    async def iniciar_evento_aleatorio(self, channel_id):
        if self.evento_activo:
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            return

        evento = random.choice(self.eventos_disponibles)
        self.evento_activo = {
            "tipo": evento["nombre"],
            "fin": datetime.now() + timedelta(minutes=evento["duracion"]),
            "config": evento,
            "channel": channel
        }
        self.participantes.clear()

        embed = discord.Embed(
            title=evento["titulo"],
            description=evento["descripcion"],
            color=discord.Color.gold()
        )
        embed.add_field(
            name="⏱️ Duración",
            value=f"{evento['duracion']} minutos"
        )
        embed.add_field(
            name="📝 Comando",
            value=f"`{evento['comando']}`"
        )

        await channel.send(embed=embed)

        # Iniciar el temporizador para finalizar el evento
        if self.timer_task:
            self.timer_task.cancel()
        self.timer_task = asyncio.create_task(self.finalizar_evento_timer(evento["duracion"]))

    async def finalizar_evento_timer(self, duracion):
        await asyncio.sleep(duracion * 60)
        if self.evento_activo:
            await self.finalizar_evento()

    async def finalizar_evento(self):
        if not self.evento_activo:
            return

        channel = self.evento_activo["channel"]
        evento_tipo = self.evento_activo["tipo"]
        
        if evento_tipo == "invasion_zombies":
            # Dar recompensas finales para la invasión zombie
            for user_id in self.participantes:
                zombies_eliminados = random.randint(2, 10)
                premio = zombies_eliminados * self.evento_activo["config"]["premio_por_zombie"]
                economy.add_money(str(user_id), premio)
                user = await self.bot.fetch_user(user_id)
                await channel.send(f"🧟 {user.mention} eliminó {zombies_eliminados} zombies y ganó {premio} monedas!")
        
        elif evento_tipo == "loteria_flash":
            # Sortear ganador de la lotería
            if self.participantes:
                ganador_id = random.choice(list(self.participantes))
                premio = self.evento_activo["config"]["premio_base"] + (len(self.participantes) * self.evento_activo["config"]["premio_por_participante"])
                economy.add_money(str(ganador_id), premio)
                ganador = await self.bot.fetch_user(ganador_id)
                await channel.send(f"🎉 ¡{ganador.mention} ha ganado la lotería flash y {premio} monedas!")

        await channel.send(f"🔚 ¡El evento {self.evento_activo['config']['titulo']} ha terminado!")
        self.evento_activo = None
        self.participantes.clear()

    async def procesar_mensaje(self, message):
        if not self.evento_activo or message.author.bot:
            return

        if message.channel.id != self.evento_activo["channel"].id:
            return

        evento = self.evento_activo
        if message.content.lower() != evento["config"]["comando"]:
            return

        if datetime.now() > evento["fin"]:
            await self.finalizar_evento()
            return

        await self.manejar_participacion(message, evento)

    async def manejar_participacion(self, message, evento):
        user_id = message.author.id
        evento_tipo = evento["tipo"]
        
        if evento_tipo == "lluvia_monedas":
            if user_id not in self.participantes:
                monedas = random.randint(evento["config"]["min_premio"], evento["config"]["max_premio"])
                economy.add_money(str(user_id), monedas)
                self.participantes.add(user_id)
                await message.channel.send(f"🌧️ ¡{message.author.mention} ha recogido {monedas} monedas!")

        elif evento_tipo == "carrera_veloz":
            if not self.participantes:  # Si nadie ha ganado aún
                self.participantes.add(user_id)
                economy.add_money(str(user_id), evento["config"]["premio"])
                await message.channel.send(f"🏃 ¡{message.author.mention} ha ganado la carrera y {evento['config']['premio']} monedas!")
                await self.finalizar_evento()

        elif evento_tipo == "cofre_tesoro":
            if user_id not in self.participantes:
                self.participantes.add(user_id)
                if random.random() > evento["config"]["trampa_probabilidad"]:
                    premio = random.randint(evento["config"]["min_premio"], evento["config"]["max_premio"])
                    economy.add_money(str(user_id), premio)
                    await message.channel.send(f"🎁 ¡{message.author.mention} ha encontrado {premio} monedas en el cofre!")
                else:
                    await message.channel.send(f"💥 ¡El cofre estaba trampeado! {message.author.mention} no ha conseguido nada.")

        elif evento_tipo == "invasion_zombies":
            if user_id not in self.participantes:
                self.participantes.add(user_id)
            zombies = random.randint(1, 5)
            premio = zombies * evento["config"]["premio_por_zombie"]
            economy.add_money(str(user_id), premio)
            await message.channel.send(f"🧟 ¡{message.author.mention} ha eliminado {zombies} zombies y ganado {premio} monedas!")

        elif evento_tipo == "loteria_flash":
            if user_id not in self.participantes:
                self.participantes.add(user_id)
                await message.channel.send(f"🎫 {message.author.mention} ha comprado un ticket para la lotería flash.")
class DailyReward:
    def __init__(self, filename: str = "daily_rewards.json"):
        self.filename = filename
        self.last_claims = self.load_claims()

    def load_claims(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_claims(self):
        with open(self.filename, 'w') as f:
            json.dump(self.last_claims, f)

    def can_claim(self, user_id: str) -> bool:
        if user_id not in self.last_claims:
            return True
        
        last_claim = datetime.fromisoformat(self.last_claims[user_id])
        now = datetime.now()
        
        # Check if last claim was before today's reset (00:00)
        today_reset = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return last_claim < today_reset

    def claim(self, user_id: str):
        self.last_claims[user_id] = datetime.now().isoformat()
        self.save_claims()
        
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.user_cooldowns = {}

    async def setup_hook(self):
        try:
            # Solo sincronizamos con el servidor específico, no globalmente
            guild = discord.Object(id=1305217034619060304)
            await self.tree.sync(guild=guild)
            print("Comandos sincronizados en el servidor específico.")
        except Exception as e:
            print(f"Error en setup_hook: {e}")

# Inicializamos el cliente
client = Bot()

# Inicializamos todos los sistemas
economy = EconomySystem()
job_system = JobSystem()
sistema_mascotas = SistemaMascotas()
sistema_objetos = inicializar_sistema_objetos()
daily_reward = DailyReward()
event_system = EventSystem(client)

# Configuramos la tarea periódica de eventos
@tasks.loop(minutes=30)
async def eventos_automaticos():
    channel_id = 1305217034619060306  # Canal específico para eventos
    if not event_system.evento_activo and random.random() < 0.3:  # 30% de probabilidad
        await event_system.iniciar_evento_aleatorio(channel_id)
# Añadimos un before_loop para esperar antes del primer evento
@eventos_automaticos.before_loop
async def before_eventos_automaticos():
    await asyncio.sleep(300)  # Espera 5 minutos antes del primer intento
# Event handlers
@client.event
async def on_message(message):
    if message.author.bot:
        return
    await event_system.procesar_mensaje(message)
    await client.process_commands(message)

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")
    print(f"ID del bot: {client.user.id}")
    
    # Iniciar la tarea de eventos automáticos
    eventos_automaticos.start()

    # Enviar mensaje de bienvenida
    canal_id = 1305217034619060306
    canal = client.get_channel(canal_id)
    if canal:
        await canal.send("Buenos dias la paga os quiten chacho")

# Event handlers

MENSAJES_A_DETECTAR = [
    "Abrazafarolas", "Adefesio", "Adoquín", "Alelado", "Alfeñique", "Analfabeto",
    "Andurriasmo", "Apollardao", "Archipámpano", "Artabán", "Asaltacunas", "Asno",
    "Asqueroso", "Atontao", "Baboso", "Ballena", "Basilisco", "Batracio", "Bellaco",
    "Berzotas", "Bocachancla", "Bocallanta", "Bollera", "Bolo", "Boludo", "Boquimuelle",
    "Botarate", "Bribón", "Burricalvo", "Cabraloca", "Cabezabuque", "Cabezaalberca",
    "Cabrón", "Cagón", "Cagueta", "Calientaestufas", "Calientahielos", "Calzamonas",
    "Canalla", "Cansino", "Cantamañanas", "Cara- seguido de lo que sea", "Cazurro",
    "Cebollino", "Cenutrio", "Cernícalo", "Charrán", "Chupacables", "Chupasangre",
    "Chupóptero", "Chusma", "Cicatero", "Cierrabares", "Cobarde", "Comealbóndigas",
    "Comemierda", "Comepiedras", "Cornudo", "Cortito", "Cretinazo", "Cuatrojos",
    "Cuerpoescombro", "Cutre", "Deficiente", "Degenerado", "Desdichado", "Deslenguado",
    "Despojo", "Desustanciado", "Energúmeno", "Espantajo", "Espabilado", "Estúpido",
    "Escuchapedos", "Espantapájaros", "Facineroso", "Fantoche", "Feo", "Fósil", "Foca",
    "Fresco", "Gallina", "Ganapán", "Gaznápiro", "Gilipollas", "Giraesquinas", "Gorrón",
    "Granuja", "Hediondo", "Huelegateras", "Huevón", "Idiota", "Imbécil", "Infacundo",
    "Joputa", "Ladrón", "Lamecharcos", "Lameculos", "Lamparón", "Lechuguino", "Lerdo",
    "Lloramigas", "Loco", "Machirulo", "Majadero", "Malaje", "Malandrín", "Maldiciente",
    "Malmirado", "Malparido", "Mamarracho", "Mameluco", "Mamporrero", "Mandril",
    "Maricón", "Marisabidilla", "Mastuerzo", "Matasanos", "Meapilas", "Melindroso",
    "Melón", "Memo", "Mendrugo", "Mentecato", "Mequetrefe", "Merluzo", "Mindundi",
    "Mochufa", "Momia", "Monstruo", "Morlaco", "Morroestufa", "Ñoño", "Orangután",
    "Orate", "Orco", "Pagafantas", "Palurdo", "Panoli", "Papafrita", "Papanatas", "Paquete",
    "Parguelas", "Pardillo", "Pasmasuegras", "Pataliebre", "Patán", "Pazguato", "Peinabombillas",
    "Pelagatos", "Pelanas", "Pelmazo", "Pendejo", "Perroflauta", "Petardo", "Petimetre",
    "Pijotero", "Piltrafilla", "Pinchauvas", "Pinche", "Pintamonas", "Pisaverde", "Plasta",
    "Pollo", "Pollopera", "Primo", "Pringao", "Pusilánime", "Puta", "Quinqui", "Rastrero",
    "Retrasado", "Ruin", "Rústico", "Sabandija", "Sabelotodo", "Sanguijuela", "Sieso",
    "Simple", "Sinvergüenza", "Soplagaitas", "Soplaguindas", "Subnormal", "Tarugo", "Tiquismiquis",
    "Tocapelotas", "Tolai", "Tolili", "Tontaina", "Tontolaba", "Toro Bravo", "Tragaldabas",
    "Traidor", "Tuercebotas", "Tunante", "Vacaburra", "Vándalo", "Veleta", "Villano",
    "Zampabollos", "Zarrapastroso", "Zascandil", "Zoquete", "Zorra", "Zote"
]

# Lista de respuestas aleatorias
RESPUESTAS = [
    "Te partan las tripas ansias negras",
    "Mal follá te pegue un negro con la chucha torcia",
    "Ahi te caiga un rayo que te parta en 7 y te coman los ciervos de ojos rojos",
    "Mala diarrea te de y te tengan que llevar al hospital en garrafa",
    "Mala lluvia de chuminos te caigan con la polla escayolá",
    "Me cago en las 4 bombillas de las 4 farolas que alumbran la tumba de tu puta madre",
    "Un capazo mierda te comas a cuchara sopera",
    "Así te de un dolor que cuanto más corras más te duela y cuando te pares revientes",
    "La cabeza te corten y te pongan una gamba aliñada",
    "Te hagan la autosia con un boli",
    "Así te pise un camión de estiércol para que tengas una muerte de mierda",
    "Mala diarrea caldosa te dé",
    "Una avalancha de cagaos te pille bostezando",
    "Un cura te pille en la puerta de un colegio y te confunda con un niño",
    "Mis pedos te encorran en un callejón sin salida",
    "Te partan la cara con un mojón zeco",
    "Q dios t guarde y no sepa donde",
    "Allá te tragues un paraguas y lo cagues abierto",
    "Mala ruina sus venga en la punta los sesos y se te parta la vena del sueño",
    "Te comas un bocadillo de cáncer",
    "Cuchame tu muerto encadenao a la farola donde se protituye tu puta madre",
    "Ahí te jayes to' los riles de los perros de tu barrio, malasombra",
    "Mil perros te coman los fulleretes",
    "Me cago en tus muyales payo revenio",
    "Ahi t estes quemando y t apaguen con gasolina",
    "A peos te peinen",
    "Eres mas inutil que un Gitano sin primos",
    "Sigue así y te mando con la virgen negra"
]

@client.tree.command(name="iniciar_evento", description="Inicia un evento aleatorio manual")
@tiene_rol_dictador()
async def iniciar_evento(interaction: discord.Interaction):
    """Este comando reemplaza al anterior comando 'evento'"""
    await event_system.iniciar_evento_aleatorio(interaction.channel_id)
    await interaction.response.send_message("✅ Evento iniciado manualmente", ephemeral=True)
    
@client.tree.command(name="daily", description="Reclama tu recompensa diaria")
async def daily(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    if not daily_reward.can_claim(user_id):
        # Calculate time until next reset
        
        now = datetime.now()
        next_reset = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        time_until_reset = next_reset - now
        
        hours, remainder = divmod(time_until_reset.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        await interaction.response.send_message(
            f"⏳ Ya has reclamado tu recompensa diaria.\n"
            f"Vuelve en {hours} horas y {minutes} minutos."
        )
        return

    # Base reward amount
    reward_amount = 100
    inventario = sistema_objetos.obtener_inventario(int(user_id))
    for efecto in inventario.obtener_efectos_activos("multiplicador_daily"):
        reward_amount *= efecto.valor
    # Check if user has a pet for bonus
    if user_id in sistema_mascotas.mascotas:
        mascota = sistema_mascotas.mascotas[user_id]
        tipo_mascota = mascota.tipo
        
        # Apply pet bonus if applicable
        if tipo_mascota in sistema_mascotas.tipos:
            bonus_monedas = sistema_mascotas.tipos[tipo_mascota].get("bonus_monedas", 1.0)
            reward_amount = int(reward_amount * bonus_monedas)

    # Add streak system later if desired
    economy.add_money(user_id, reward_amount)
    daily_reward.claim(user_id)
    
    embed = discord.Embed(
        title="🎁 Recompensa Diaria",
        description=f"Has reclamado {reward_amount} monedas",
        color=discord.Color.green()
    )
    
    if reward_amount > 100:  # If bonus was applied
        embed.add_field(
            name="✨ Bonus",
            value=f"Tu mascota te dio un bonus en la recompensa!"
        )
    
    embed.add_field(
        name="💰 Balance",
        value=f"Balance actual: {economy.get_balance(user_id)} monedas"
    )
    
    await interaction.response.send_message(embed=embed)
@client.tree.command(name="balance", description="Muestra tu balance de monedas")
async def balance(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    user_id = str(usuario.id)
    balance = economy.get_balance(user_id)
    
    if usuario == interaction.user:
        await interaction.response.send_message(f"💰 Tu balance actual es de {balance} monedas.")
    else:
        await interaction.response.send_message(f"💰 El balance de {usuario.mention} es de {balance} monedas.")


@client.tree.command(name="trabajar", description="Realiza un trabajo para ganar monedas")
async def trabajar(interaction: discord.Interaction, trabajo: str):
    user_id = str(interaction.user.id)

    if trabajo not in job_system.jobs:
        trabajos_disponibles = "\n".join([f"**{job}** ({data['min']}-{data['max']} monedas, {data['cooldown_minutes']}min)" 
                                        for job, data in job_system.jobs.items()])
        await interaction.response.send_message(
            f"❌ Trabajo no válido. Trabajos disponibles:\n{trabajos_disponibles}"
        )
        return

    if not job_system.can_work(user_id, trabajo):
        remaining = job_system.get_remaining_cooldown(user_id, trabajo)
        await interaction.response.send_message(
            f"⏳ Debes esperar {int(remaining.total_seconds() // 60)} minutos y "
            f"{int(remaining.total_seconds() % 60)} segundos para trabajar de nuevo."
        )
        return

    earnings, special_message = job_system.perform_job(user_id, trabajo, economy, sistema_objetos)
    
    embed = discord.Embed(
        title=f"💼 Trabajo: {trabajo}",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="💰 Ganancias",
        value=f"{earnings} monedas",
        inline=False
    )
    
    if special_message:
        embed.add_field(
            name="✨ ¡Evento Especial!",
            value=special_message,
            inline=False
        )
    
    embed.add_field(
        name="💳 Balance Actual",
        value=f"{economy.get_balance(user_id)} monedas",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="trabajos", description="Muestra los trabajos disponibles")
async def trabajos(interaction: discord.Interaction):
    embed = discord.Embed(
        title="💼 Trabajos Disponibles",
        color=discord.Color.blue()
    )
    
    for name, data in job_system.jobs.items():
        embed.add_field(
            name=name.capitalize(),
            value=(f"💰 Ganancias: {data['min']}-{data['max']} monedas\n"
                  f"⏱️ Cooldown: {data['cooldown_minutes']} minutos\n"
                  f"📝 {data['description']}"),
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="top", description="Muestra el ranking de usuarios más ricos")
async def top(interaction: discord.Interaction):
    balances = [(user_id, amount) for user_id, amount in economy.accounts.items()]
    balances.sort(key=lambda x: x[1], reverse=True)
    
    embed = discord.Embed(
        title="🏆 Ranking de Riqueza",
        color=discord.Color.gold()
    )

    for i, (user_id, amount) in enumerate(balances[:10], 1):
        try:
            user = await client.fetch_user(int(user_id))
            emoji = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "💰"
            embed.add_field(
                name=f"{emoji} #{i}",
                value=f"{user.name}: {amount} monedas",
                inline=False
            )
        except:
            continue
    
    await interaction.response.send_message(embed=embed)

# Comandos de administrador
@client.tree.command(name="agregar_monedas", description="Agrega monedas a un usuario")
@tiene_rol_dictador()
async def agregar_monedas(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if cantidad <= 0:
        await interaction.response.send_message("❌ La cantidad debe ser positiva")
        return

    economy.add_money(str(usuario.id), cantidad)
    await interaction.response.send_message(
        f"✅ Se agregaron {cantidad} monedas a {usuario.mention}\n"
        f"💰 Nuevo balance: {economy.get_balance(str(usuario.id))} monedas"
    )

@client.tree.command(name="quitar_monedas", description="Quita monedas a un usuario")
@tiene_rol_dictador()
async def quitar_monedas(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if cantidad <= 0:
        await interaction.response.send_message("❌ La cantidad debe ser positiva")
        return

    if not economy.remove_money(str(usuario.id), cantidad):
        await interaction.response.send_message("❌ El usuario no tiene suficientes monedas")
        return

    await interaction.response.send_message(
        f"✅ Se quitaron {cantidad} monedas a {usuario.mention}\n"
        f"💰 Nuevo balance: {economy.get_balance(str(usuario.id))} monedas"
    )
    
# Comandos de juegos
class DiceView(View):
    def __init__(self, user_id: str, initial_bet: int, economy):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.apuesta = initial_bet
        self.economy = economy

        # Botones
        self.roll_button = Button(label="🎲 Tirar", style=discord.ButtonStyle.primary)
        self.increase_bet = Button(label="➕ Aumentar", style=discord.ButtonStyle.secondary)
        self.decrease_bet = Button(label="➖ Disminuir", style=discord.ButtonStyle.secondary)
        self.exit_button = Button(label="❌ Salir", style=discord.ButtonStyle.danger)

        # Callbacks
        self.roll_button.callback = self.roll_dice_callback
        self.increase_bet.callback = self.increase_bet_callback
        self.decrease_bet.callback = self.decrease_bet_callback
        self.exit_button.callback = self.exit_callback

        # Agregar botones
        self.add_item(self.roll_button)
        self.add_item(self.increase_bet)
        self.add_item(self.decrease_bet)
        self.add_item(self.exit_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == self.user_id

    async def roll_dice_callback(self, interaction: discord.Interaction):
        if not self.economy.remove_money(self.user_id, self.apuesta):
            await interaction.response.edit_message(content="❌ No tienes suficientes monedas", view=self)
            return

        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if user_roll > bot_roll:
            winnings = self.apuesta * 2
            final_winnings = self.economy.add_money(self.user_id, winnings)
            _, mult_text = get_multiplier_text(int(self.user_id))
            result = (f"🎲 Tu dado: {user_roll}\n🎲 Mi dado: {bot_roll}\n"
                     f"🎉 ¡Ganaste {final_winnings} monedas!{mult_text}")
        elif user_roll < bot_roll:
            result = (f"🎲 Tu dado: {user_roll}\n🎲 Mi dado: {bot_roll}\n"
                     f"😔 Perdiste {self.apuesta} monedas")
        else:
            self.economy.add_money(self.user_id, self.apuesta)
            result = (f"🎲 Tu dado: {user_roll}\n🎲 Mi dado: {bot_roll}\n"
                     f"🤝 ¡Empate! Recuperas tu apuesta")

        result += f"\n💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
        await interaction.response.edit_message(content=result, view=self)

    async def increase_bet_callback(self, interaction: discord.Interaction):
        new_bet = self.apuesta + 10
        if self.economy.get_balance(self.user_id) >= new_bet:
            self.apuesta = new_bet
            await interaction.response.edit_message(
                content=f"📈 Apuesta aumentada a {self.apuesta} monedas", view=self)
        else:
            await interaction.response.edit_message(
                content="❌ No tienes suficientes monedas", view=self)

    async def decrease_bet_callback(self, interaction: discord.Interaction):
        if self.apuesta > 10:
            self.apuesta -= 10
            await interaction.response.edit_message(
                content=f"📉 Apuesta reducida a {self.apuesta} monedas", view=self)
        else:
            await interaction.response.edit_message(
                content="❌ La apuesta mínima es 10 monedas", view=self)

    async def exit_callback(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="👋 ¡Gracias por jugar!", view=self)

@client.tree.command(name="dados", description="Juega a los dados")
async def dados(interaction: discord.Interaction, apuesta: int):
    if apuesta < 10:
        await interaction.response.send_message("❌ La apuesta mínima es 10 monedas")
        return

    user_id = str(interaction.user.id)
    if not economy.remove_money(user_id, apuesta):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    economy.add_money(user_id, apuesta)  # Devolver la apuesta inicial
    view = DiceView(user_id, apuesta, economy)
    await interaction.response.send_message(
        f"🎲 {interaction.user.mention} apuesta {apuesta} monedas\n"
        f"💰 Balance: {economy.get_balance(user_id)} monedas", 
        view=view
    )
class SlotMachineView(View):
    def __init__(self, user_id: str, initial_bet: int, economy):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.apuesta = initial_bet
        self.economy = economy
        
        # Botones
        self.spin_button = Button(label="🎰 Girar", style=discord.ButtonStyle.primary)
        self.increase_bet = Button(label="➕ Aumentar", style=discord.ButtonStyle.secondary)
        self.decrease_bet = Button(label="➖ Disminuir", style=discord.ButtonStyle.secondary)
        self.exit_button = Button(label="❌ Salir", style=discord.ButtonStyle.danger)

        # Callbacks
        self.spin_button.callback = self.spin_callback
        self.increase_bet.callback = self.increase_bet_callback
        self.decrease_bet.callback = self.decrease_bet_callback
        self.exit_button.callback = self.exit_callback
        # Agregar botones
        self.add_item(self.spin_button)
        self.add_item(self.increase_bet)
        self.add_item(self.decrease_bet)
        self.add_item(self.exit_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == self.user_id

    async def spin_callback(self, interaction: discord.Interaction):
        if not self.economy.remove_money(self.user_id, self.apuesta):
            await interaction.response.edit_message(content="❌ No tienes suficientes monedas", view=self)
            return

        symbols = ["🍒", "🍊", "🍋", "🍇", "💎", "7️⃣"]
        result = [random.choice(symbols) for _ in range(3)]
        _, mult_text = get_multiplier_text(int(self.user_id))

        if all(s == result[0] for s in result):
            winnings = self.apuesta * 5
            final_winnings = self.economy.add_money(self.user_id, winnings)
            message = f"🎰 [{' | '.join(result)}]\n🎉 ¡JACKPOT! Ganaste {final_winnings} monedas{mult_text}"
        elif result.count(result[0]) == 2 or result.count(result[1]) == 2:
            winnings = self.apuesta * 2
            final_winnings = self.economy.add_money(self.user_id, winnings)
            message = f"🎰 [{' | '.join(result)}]\n🎉 ¡Dos iguales! Ganaste {final_winnings} monedas{mult_text}"
        else:
            message = f"🎰 [{' | '.join(result)}]\n😔 Perdiste {self.apuesta} monedas"

        message += f"\n💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
        await interaction.response.edit_message(content=message, view=self)
    async def increase_bet_callback(self, interaction: discord.Interaction):
        new_bet = self.apuesta + 10
        if self.economy.get_balance(self.user_id) >= new_bet:
            self.apuesta = new_bet
            await interaction.response.edit_message(
                content=f"📈 Apuesta aumentada a {self.apuesta} monedas", view=self)
        else:
            await interaction.response.edit_message(
                content="❌ No tienes suficientes monedas", view=self)

    async def decrease_bet_callback(self, interaction: discord.Interaction):
        if self.apuesta > 10:
            self.apuesta -= 10
            await interaction.response.edit_message(
                content=f"📉 Apuesta reducida a {self.apuesta} monedas", view=self)
        else:
            await interaction.response.edit_message(
                content="❌ La apuesta mínima es 10 monedas", view=self)

    async def exit_callback(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="👋 ¡Gracias por jugar!", view=self)

@client.tree.command(name="sync", description="Sincroniza los comandos del bot")
@tiene_rol_dictador()
async def sync(interaction: discord.Interaction):
    try:
        guild = discord.Object(id=interaction.guild_id)
        synced = await client.tree.sync(guild=guild)
        await interaction.response.send_message(
            f"Sincronizados {len(synced)} comandos",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Error: {str(e)}",
            ephemeral=True
        )

# Manejo de errores para el comando /sync
@sync.error
async def sync_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("No tienes permisos para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Ocurrió un error: {error}", ephemeral=True)
@client.tree.command(name="tragaperras", description="Juega a la tragaperras")
async def tragaperras(interaction: discord.Interaction, apuesta: int):
    if apuesta < 10:
        await interaction.response.send_message("❌ La apuesta mínima es 10 monedas")
        return

    user_id = str(interaction.user.id)
    if not economy.remove_money(user_id, apuesta):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    economy.add_money(user_id, apuesta)  # Devolver la apuesta inicial
    view = SlotMachineView(user_id, apuesta, economy)
    await interaction.response.send_message(
        f"🎰 {interaction.user.mention} apuesta {apuesta} monedas\n"
        f"💰 Balance: {economy.get_balance(user_id)} monedas", 
        view=view
    )

class RouletteView(View):
    def __init__(self, user_id: str, bet_amount: int, economy):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.economy = economy

        self.add_item(Button(label="🔴 Rojo (x2)", style=discord.ButtonStyle.red, custom_id="red"))
        self.add_item(Button(label="⚫ Negro (x2)", style=discord.ButtonStyle.secondary, custom_id="black"))
        self.add_item(Button(label="🟢 Verde (x14)", style=discord.ButtonStyle.green, custom_id="green"))
        self.add_item(Button(label="👥 Par (x2)", style=discord.ButtonStyle.blurple, custom_id="even"))
        self.add_item(Button(label="👤 Impar (x2)", style=discord.ButtonStyle.blurple, custom_id="odd"))

        for item in self.children:
            item.callback = self.button_callback

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == self.user_id

    def get_number_color(self, number):
        if number == 0:
            return "🟢 verde"
        elif number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
            return "🔴 rojo"
        else:
            return "⚫ negro"

    async def button_callback(self, interaction: discord.Interaction):
        bet_type = interaction.data["custom_id"]
        number = random.randint(0, 36)
        color = self.get_number_color(number)
        _, mult_text = get_multiplier_text(int(self.user_id))

        result_message = f"🎲 La bola ha caído en el {number} ({color})\n"
        won = False
        multiplier = 0

        if bet_type == "red" and "rojo" in color:
            won = True
            multiplier = 2
        elif bet_type == "black" and "negro" in color:
            won = True
            multiplier = 2
        elif bet_type == "green" and "verde" in color:
            won = True
            multiplier = 14
        elif bet_type == "even" and number != 0 and number % 2 == 0:
            won = True
            multiplier = 2
        elif bet_type == "odd" and number != 0 and number % 2 != 0:
            won = True
            multiplier = 2

        if won:
            winnings = self.bet_amount * multiplier
            final_winnings = self.economy.add_money(self.user_id, winnings)
            result_message += f"🎉 ¡Ganaste {final_winnings} monedas!{mult_text}"
        else:
            result_message += f"😔 Perdiste {self.bet_amount} monedas"

        result_message += f"\n💰 Balance: {self.economy.get_balance(self.user_id)} monedas"

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(content=result_message, view=self)


@client.tree.command(name="ruleta", description="Juega a la ruleta")
async def ruleta(interaction: discord.Interaction, apuesta: int):
    if apuesta < 10:
        await interaction.response.send_message("❌ La apuesta mínima es 10 monedas")
        return

    user_id = str(interaction.user.id)
    if not economy.remove_money(user_id, apuesta):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    view = RouletteView(user_id, apuesta, economy)
    await interaction.response.send_message(
        f"🎰 {interaction.user.mention} apuesta {apuesta} monedas\n"
        "Elige tu apuesta:\n"
        "- 🔴 Rojo (x2): Números rojos\n"
        "- ⚫ Negro (x2): Números negros\n"
        "- 🟢 Verde (x14): El número 0\n"
        "- 👥 Par (x2): Números pares\n"
        "- 👤 Impar (x2): Números impares", 
        view=view
    )
@client.tree.command(name="comprar_mascota", description="Compra una mascota")
async def comprar_mascota(interaction: discord.Interaction, nombre: str, tipo: str):
    if tipo not in sistema_mascotas.tipos:
        await interaction.response.send_message(
            f"❌ Tipo no válido. Tipos disponibles: {', '.join(sistema_mascotas.tipos.keys())}"
        )
        return

    user_id = str(interaction.user.id)
    precio = sistema_mascotas.tipos[tipo]["precio"]

    if not economy.remove_money(user_id, precio):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    if sistema_mascotas.crear_mascota(user_id, nombre, tipo):
        await interaction.response.send_message(
            f"🐾 ¡Has adoptado a {nombre} ({tipo})!\n"
            "Usa /mascota para ver su estado"
        )
    else:
        economy.add_money(user_id, precio)
        await interaction.response.send_message("❌ Ya tienes una mascota")

@client.tree.command(name="mascota", description="Ver el estado de tu mascota")
async def mascota(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    if user_id not in sistema_mascotas.mascotas:
        await interaction.response.send_message(
            "❌ No tienes mascota. Usa /comprar_mascota"
        )
        return

    mascota = sistema_mascotas.mascotas[user_id]
    mascota.actualizar_estado()

    # Emojis basados en estado
    hambre_emoji = "😋" if mascota.hambre > 70 else "😐" if mascota.hambre > 30 else "😫"
    felicidad_emoji = "😊" if mascota.felicidad > 70 else "😐" if mascota.felicidad > 30 else "😢"

    embed = discord.Embed(
        title=f"🐾 {mascota.nombre}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Tipo", value=mascota.tipo.capitalize(), inline=True)
    embed.add_field(name="Nivel", value=f"{mascota.nivel} ({mascota.exp}/{mascota.exp_necesaria()} EXP)", inline=True)
    embed.add_field(name="Hambre", value=f"{hambre_emoji} {mascota.hambre:.1f}%", inline=True)
    embed.add_field(name="Felicidad", value=f"{felicidad_emoji} {mascota.felicidad:.1f}%", inline=True)

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="alimentar", description="Alimenta a tu mascota")
@app_commands.checks.cooldown(1, 3600)
async def alimentar(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    costo = 50

    if not economy.remove_money(user_id, costo):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    if sistema_mascotas.alimentar_mascota(user_id):
        mascota = sistema_mascotas.mascotas[user_id]
        await interaction.response.send_message(
            f"🍖 Has alimentado a {mascota.nombre}\n"
            f"Hambre: {mascota.hambre:.1f}%\n"
            f"EXP: +10"
        )
    else:
        economy.add_money(user_id, costo)
        await interaction.response.send_message("❌ No tienes mascota")

@client.tree.command(name="acariciar", description="Acaricia a tu mascota")
@app_commands.checks.cooldown(1, 1800)
async def acariciar(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if sistema_mascotas.acariciar_mascota(user_id):
        mascota = sistema_mascotas.mascotas[user_id]
        await interaction.response.send_message(
            f"💝 Has acariciado a {mascota.nombre}\n"
            f"Felicidad: {mascota.felicidad:.1f}%\n"
            f"EXP: +5"
        )
    else:
        await interaction.response.send_message("❌ No tienes mascota")

@client.tree.command(name="tienda", description="Ver objetos disponibles en la tienda")
async def tienda(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏪 Tienda de Objetos",
        description="Compra objetos especiales para potenciar tu experiencia",
        color=discord.Color.gold()
    )

    for objeto in sistema_objetos.objetos.values():
        emoji = objeto.emoji or "🎁"
        embed.add_field(
            name=f"{emoji} {objeto.nombre} - {objeto.precio} monedas",
            value=objeto.descripcion,
            inline=False
        )

    embed.set_footer(text="Usa /comprar [nombre] para adquirir un objeto")
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="comprar", description="Comprar un objeto de la tienda")
async def comprar(interaction: discord.Interaction, objeto: str):
    objeto_encontrado = sistema_objetos.obtener_objeto(objeto.lower())
    
    if not objeto_encontrado:
        await interaction.response.send_message(
            "❌ Objeto no encontrado. Usa /tienda para ver los objetos disponibles"
        )
        return

    user_id = str(interaction.user.id)
    if not economy.remove_money(user_id, objeto_encontrado.precio):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    if sistema_objetos.agregar_objeto_a_inventario(interaction.user.id, objeto_encontrado.nombre):
        await interaction.response.send_message(
            f"✅ Has comprado {objeto_encontrado.nombre}\n"
            f"💰 Balance: {economy.get_balance(user_id)} monedas"
        )
    else:
        economy.add_money(user_id, objeto_encontrado.precio)
        await interaction.response.send_message(
            "❌ No puedes tener más unidades de este objeto"
        )

@client.tree.command(name="inventario", description="Ver tu inventario")
async def inventario(interaction: discord.Interaction):
    inventario = sistema_objetos.obtener_inventario(interaction.user.id)
    
    embed = discord.Embed(
        title=f"🎒 Inventario de {interaction.user.name}",
        color=discord.Color.blue()
    )

    if not inventario.objetos:
        embed.description = "Tu inventario está vacío"
    else:
        for objeto_data in inventario.objetos.values():
            if objeto_data["cantidad"] > 0:  # Solo mostrar objetos que tenemos
                emoji = objeto_data["emoji"] or "🎁"
                embed.add_field(
                    name=f"{emoji} {objeto_data['nombre']} (x{objeto_data['cantidad']})",
                    value=objeto_data["descripcion"],
                    inline=False
                )

    # Mostrar efectos activos
    efectos_activos = inventario.obtener_efectos_activos()
    if efectos_activos:
        efectos_texto = []
        for efecto in efectos_activos:
            if efecto.duracion:
                tiempo_restante = efecto.tiempo_inicio + timedelta(seconds=efecto.duracion) - datetime.now()
                efectos_texto.append(f"{efecto.tipo.capitalize()}: {int(tiempo_restante.total_seconds() / 60)} minutos restantes")
            else:
                efectos_texto.append(f"{efecto.tipo.capitalize()}: Activo")
        
        embed.add_field(
            name="⚡ Efectos Activos",
            value="\n".join(efectos_texto),
            inline=False
        )

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="usar", description="Usar un objeto de tu inventario")
async def usar(interaction: discord.Interaction, objeto: str):
    user_id = interaction.user.id
    inventario = sistema_objetos.obtener_inventario(user_id)
    objeto_encontrado = sistema_objetos.obtener_objeto(objeto.lower())

    if not objeto_encontrado:
        await interaction.response.send_message("❌ Objeto no encontrado")
        return

    # Verificar si el usuario tiene el objeto
    efectos = inventario.usar_objeto(objeto_encontrado)
    if not efectos:
        await interaction.response.send_message("❌ No tienes ese objeto en tu inventario")
        return

    # Crear el mensaje de resultado
    embed = discord.Embed(
        title=f"✨ Has usado {objeto_encontrado.nombre}",
        color=discord.Color.green()
    )

    # Aplicar efectos según el tipo
    for efecto in efectos:
        mensaje_efecto = ""

        if efecto.tipo == "monedas_instantaneas":
            # Dar monedas instantáneas
            cantidad_final = economy.add_money(str(user_id), efecto.valor)
            mensaje_efecto = f"Has ganado {cantidad_final} monedas"

        elif efecto.tipo == "multiplicador":
            # El multiplicador se aplica automáticamente en el sistema económico
            horas = efecto.duracion // 3600
            minutos = (efecto.duracion % 3600) // 60
            mensaje_efecto = f"Multiplicador x{efecto.valor} activo por {horas}h {minutos}m"

        elif efecto.tipo == "proteccion_robo":
            # La protección se verifica en el comando robar
            horas = efecto.duracion // 3600
            mensaje_efecto = f"Protección contra robos activa por {horas} horas"

        elif efecto.tipo == "multiplicador_daily":
            # Se aplicará en la próxima recompensa diaria
            horas = efecto.duracion // 3600
            mensaje_efecto = f"Tu próxima recompensa diaria será multiplicada por {efecto.valor}"

        elif efecto.tipo == "multiplicador_exp_mascota":
            # Verificar si el usuario tiene mascota
            if str(user_id) not in sistema_mascotas.mascotas:
                mensaje_efecto = "❌ Necesitas una mascota para usar este objeto"
            else:
                horas = efecto.duracion // 3600
                mensaje_efecto = f"Tu mascota ganará x{efecto.valor} experiencia por {horas} horas"

        elif efecto.tipo in ["felicidad_mascota", "hambre_mascota"]:
            # Verificar si el usuario tiene mascota
            if str(user_id) not in sistema_mascotas.mascotas:
                mensaje_efecto = "❌ Necesitas una mascota para usar este objeto"
            else:
                mascota = sistema_mascotas.mascotas[str(user_id)]
                if efecto.tipo == "felicidad_mascota":
                    mascota.felicidad = min(100, mascota.felicidad + efecto.valor)
                    mensaje_efecto = f"Felicidad de {mascota.nombre} aumentada a {mascota.felicidad}%"
                else:
                    mascota.hambre = min(100, mascota.hambre + efecto.valor)
                    mensaje_efecto = f"Hambre de {mascota.nombre} reducida a {mascota.hambre}%"
                sistema_mascotas.save_data()

        elif efecto.tipo == "reduccion_cooldown":
            # La reducción se aplica automáticamente en el sistema de trabajos
            horas = efecto.duracion // 3600
            porcentaje = int((1 - efecto.valor) * 100)
            mensaje_efecto = f"Cooldowns reducidos {porcentaje}% por {horas} horas"

        elif efecto.tipo == "duracion_efectos":
            # Este efecto se aplica a todos los nuevos efectos
            horas = efecto.duracion // 3600
            porcentaje = int((efecto.valor - 1) * 100)
            mensaje_efecto = f"Todos los efectos durarán {porcentaje}% más por {horas} horas"

        embed.add_field(
            name=f"{objeto_encontrado.emoji} Efecto Aplicado",
            value=mensaje_efecto,
            inline=False
        )

    # Guardar los cambios
    sistema_objetos.save_data()

    # Mostrar el balance actual
    embed.add_field(
        name="💰 Balance Actual",
        value=f"{economy.get_balance(str(user_id))} monedas",
        inline=False
    )

    await interaction.response.send_message(embed=embed)
@client.tree.command(name="regalar", description="Regala un objeto a otro usuario")
async def regalar(interaction: discord.Interaction, usuario: discord.Member, objeto: str):
    if usuario.id == interaction.user.id:
        await interaction.response.send_message("❌ No puedes regalarte objetos a ti mismo")
        return

    objeto_encontrado = sistema_objetos.objetos.get(objeto.lower())
    if not objeto_encontrado:
        await interaction.response.send_message("❌ Objeto no encontrado")
        return

    # Verificar que el usuario tiene el objeto
    inventario_origen = sistema_objetos.obtener_inventario(interaction.user.id)
    if objeto_encontrado.id not in inventario_origen.objetos or inventario_origen.objetos[objeto_encontrado.id] < 1:
        await interaction.response.send_message("❌ No tienes ese objeto")
        return

    # Transferir el objeto
    inventario_destino = sistema_objetos.obtener_inventario(usuario.id)
    if not inventario_destino.agregar_objeto(objeto_encontrado, 1):
        await interaction.response.send_message("❌ El usuario no puede recibir más unidades de este objeto")
        return

    # Quitar el objeto del inventario del donante
    inventario_origen.objetos[objeto_encontrado.id] -= 1
    if inventario_origen.objetos[objeto_encontrado.id] == 0:
        del inventario_origen.objetos[objeto_encontrado.id]

    await interaction.response.send_message(
        f"🎁 Has regalado {objeto_encontrado.nombre} a {usuario.mention}"
    )

@client.tree.command(name="ruleta_rusa", description="Juega a la ruleta rusa (timeout)")
@app_commands.checks.cooldown(1, 30)
async def ruleta_rusa(interaction: discord.Interaction):
    try:
        # Sistema de racha de supervivencia
        if not hasattr(client, 'ruleta_counters'):
            client.ruleta_counters = {}

        user_id = str(interaction.user.id)
        if user_id not in client.ruleta_counters:
            client.ruleta_counters[user_id] = 0

        # Mensajes dramáticos
        mensajes_tension = [
            "🎭 *Girando el tambor lentamente...*",
            "🎲 *El tambor da vueltas...*",
            "🔄 *Click... click... click...*",
            "🎯 *El destino está en juego...*"
        ]

        racha_texto = f" (Racha: {client.ruleta_counters[user_id]})" if client.ruleta_counters[user_id] > 0 else ""
        await interaction.response.send_message(
            f"🔫 {interaction.user.mention} toma el revólver con mano temblorosa...{racha_texto}"
        )

        await asyncio.sleep(1.5)
        await interaction.channel.send(random.choice(mensajes_tension))
        await asyncio.sleep(1.5)

        # 1/6 de probabilidad
        if random.randint(1, 6) == 1:
            try:
                timeout_duration = datetime.timedelta(minutes=1)
                await interaction.user.timeout(timeout_duration, reason="Perdió en la ruleta rusa")
                client.ruleta_counters[user_id] = 0

                mensajes_derrota = [
                    f"💥 ¡BANG! {interaction.user.mention} ha perdido y estará en silencio durante 1 minuto!",
                    f"💀 ¡BOOM! La suerte no estuvo del lado de {interaction.user.mention}...",
                    f"🎭 ¡PAM! {interaction.user.mention} apostó y perdió...",
                    f"☠️ ¡BANG! {interaction.user.mention} debería haber elegido mejor..."
                ]
                await interaction.channel.send(f"{random.choice(mensajes_derrota)} (Racha perdida)")

            except discord.errors.Forbidden:
                await interaction.channel.send(
                    "💥 ¡BANG! ¡Has perdido! Pero no tengo permisos para silenciarte 😅"
                )
        else:
            client.ruleta_counters[user_id] += 1
            nueva_racha = client.ruleta_counters[user_id]

            mensajes_supervivencia = [
                f"😅 *Click* - {interaction.user.mention} respira aliviado...",
                f"😌 *Click* - La suerte sonríe a {interaction.user.mention} esta vez",
                f"😎 *Click* - {interaction.user.mention} vive para jugar otro día",
                f"🍀 *Click* - {interaction.user.mention} ha sobrevivido de milagro"
            ]

            mensaje_base = f"{random.choice(mensajes_supervivencia)} (Racha: {nueva_racha})"
            if nueva_racha >= 10:
                mensaje_base += "\n🏆 ¡Impresionante racha de supervivencia!"
            elif nueva_racha >= 5:
                mensaje_base += "\n⭐ ¡Gran racha!"

            await interaction.channel.send(mensaje_base)

    except Exception as e:
        print(f"Error en ruleta_rusa: {e}")
        await interaction.channel.send("❌ Ha ocurrido un error. Por favor, inténtalo de nuevo.")

# Manejo de errores para cooldowns
@client.event
async def on_application_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        await interaction.response.send_message(
            f"⏳ Debes esperar {int(minutes)} minutos y {int(seconds)} segundos para usar este comando de nuevo.",
            ephemeral=True
        )
    else:
        print(f"Error no manejado: {error}")
        
@client.tree.command(name="rasca", description="Compra un rasca y gana por 50 monedas")
async def rasca(interaction: discord.Interaction):
    precio = 50
    user_id = str(interaction.user.id)

    if not economy.remove_money(user_id, precio):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    simbolos = ["💎", "💰", "🎰", "⭐", "🎲"]
    rasca = [[random.choice(simbolos) for _ in range(3)] for _ in range(3)]

    premio = 0
    mensaje = "🎫 Tu rasca:\n\n"

    for fila in rasca:
        mensaje += " ".join(fila) + "\n"

    for fila in rasca:
        if len(set(fila)) == 1:
            premio += 200

    for j in range(3):
        columna = [rasca[i][j] for i in range(3)]
        if len(set(columna)) == 1:
            premio += 200

    diagonal1 = [rasca[i][i] for i in range(3)]
    diagonal2 = [rasca[i][2-i] for i in range(3)]
    
    if len(set(diagonal1)) == 1:
        premio += 300
    if len(set(diagonal2)) == 1:
        premio += 300

    _, mult_text = get_multiplier_text(interaction.user.id)

    if premio > 0:
        final_premio = economy.add_money(user_id, premio)
        mensaje += f"\n🎉 ¡Has ganado {final_premio} monedas!{mult_text}"
    else:
        mensaje += "\n😔 No hay premio"

    mensaje += f"\n💰 Balance: {economy.get_balance(user_id)} monedas"
    await interaction.response.send_message(mensaje)
@client.tree.command(name="loteria", description="Compra un boleto de lotería")
@app_commands.checks.cooldown(1, 86400)
async def loteria(interaction: discord.Interaction):
    precio_boleto = 100
    user_id = str(interaction.user.id)

    if not economy.remove_money(user_id, precio_boleto):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    numero_jugador = random.randint(1, 99)
    await interaction.response.send_message(
        f"🎫 Has comprado el boleto número {numero_jugador:02d}\n"
        "El sorteo será en 1 minuto..."
    )

    await asyncio.sleep(60)
    numero_ganador = random.randint(1, 99)
    _, mult_text = get_multiplier_text(interaction.user.id)

    if numero_jugador == numero_ganador:
        premio = precio_boleto * 50
        final_premio = economy.add_money(user_id, premio)
        await interaction.channel.send(
            f"🎉 ¡{interaction.user.mention} ha ganado la lotería!\n"
            f"Número ganador: {numero_ganador:02d}\n"
            f"Premio: {final_premio} monedas{mult_text}"
        )
    else:
        await interaction.channel.send(
            f"📢 Resultado de la lotería:\n"
            f"Tu número: {numero_jugador:02d}\n"
            f"Número ganador: {numero_ganador:02d}\n"
            "Mejor suerte la próxima vez..."
        )

@client.tree.command(name="robar", description="Intenta robar monedas a otro usuario")
@app_commands.checks.cooldown(1, 3600)
async def robar(interaction: discord.Interaction, victima: discord.Member):
    if victima.id == interaction.user.id:
        await interaction.response.send_message("❌ No puedes robarte a ti mismo")
        return

    ladron_id = str(interaction.user.id)
    victima_id = str(victima.id)

    inventario_victima = sistema_objetos.obtener_inventario(victima.id)
    efectos_proteccion = inventario_victima.obtener_efectos_activos("proteccion_robo")
    if efectos_proteccion:
        await interaction.response.send_message(
            f"❌ ¡{victima.mention} está protegido contra robos!"
        )
        return

    balance_victima = economy.get_balance(victima_id)
    if balance_victima < 50:
        await interaction.response.send_message(
            f"❌ {victima.mention} es demasiado pobre para robarle"
        )
        return

    exito = random.random() < 0.4
    _, mult_text = get_multiplier_text(interaction.user.id)

    if exito:
        cantidad = random.randint(10, min(100, balance_victima))
        economy.remove_money(victima_id, cantidad)
        final_cantidad = economy.add_money(ladron_id, cantidad)
        await interaction.response.send_message(
            f"🦹 ¡Robo exitoso! Le has robado {final_cantidad} monedas a {victima.mention}{mult_text}"
        )
    else:
        multa = random.randint(50, 200)
        if economy.remove_money(ladron_id, multa):
            economy.add_money(victima_id, multa // 2, check_multiplier=False)  # La víctima no recibe multiplicador
            await interaction.response.send_message(
                f"👮 ¡Te han pillado! Multa de {multa} monedas\n"
                f"{victima.mention} recibe {multa // 2} monedas de compensación"
            )
        else:
            await interaction.response.send_message(
                "❌ No tienes suficientes monedas para pagar la multa si te pillan"
            )


@client.tree.command(name="duelo", description="Desafía a otro usuario a un duelo por monedas")
async def duelo(interaction: discord.Interaction, oponente: discord.Member, apuesta: int):
    if oponente.id == interaction.user.id:
        await interaction.response.send_message("❌ No puedes desafiarte a ti mismo")
        return

    if apuesta <= 0:
        await interaction.response.send_message("❌ La apuesta debe ser mayor que 0")
        return

    retador_id = str(interaction.user.id)
    oponente_id = str(oponente.id)

    # Verificar fondos del retador
    if not economy.remove_money(retador_id, apuesta):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    await interaction.response.send_message(
        f"⚔️ {oponente.mention}, {interaction.user.mention} te desafía a un duelo por {apuesta} monedas\n"
        "Tienes 30 segundos para aceptar escribiendo 'aceptar'"
    )

    def check(m):
        return m.author.id == oponente.id and m.content.lower() == "aceptar"

    try:
        await client.wait_for('message', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        economy.add_money(retador_id, apuesta)
        await interaction.channel.send("❌ Duelo cancelado por falta de respuesta")
        return

    # Verificar fondos del oponente
    if not economy.remove_money(oponente_id, apuesta):
        economy.add_money(retador_id, apuesta)
        await interaction.channel.send(f"❌ {oponente.mention} no tiene suficientes monedas")
        return

    vida_retador = 100
    vida_oponente = 100
    total_pot = apuesta * 2

    await interaction.channel.send("⚔️ ¡El duelo comienza!")

    while vida_retador > 0 and vida_oponente > 0:
        # Sistema de combate con críticos y esquivas
        for jugador, objetivo in [(interaction.user, oponente), (oponente, interaction.user)]:
            # 20% de probabilidad de esquivar
            if random.random() < 0.2:
                await interaction.channel.send(f"💨 ¡{objetivo.mention} esquiva el ataque!")
                continue

            daño = random.randint(15, 25)
            # 15% de probabilidad de crítico
            if random.random() < 0.15:
                daño *= 2
                await interaction.channel.send(f"⚡ ¡Golpe crítico de {jugador.mention}!")

            if jugador == interaction.user:
                vida_oponente -= daño
            else:
                vida_retador -= daño

            await interaction.channel.send(
                f"🗡️ {jugador.mention} ataca a {objetivo.mention} por {daño} de daño!\n"
                f"Vida restante: {max(0, vida_oponente if jugador == interaction.user else vida_retador)}"
            )
            await asyncio.sleep(2)

    # Determinar ganador
    # Al momento de dar el premio:
    ganador = interaction.user if vida_retador > vida_oponente else oponente
    ganador_id = str(ganador.id)
    _, mult_text = get_multiplier_text(ganador.id)
    final_premio = economy.add_money(ganador_id, total_pot)

    await interaction.channel.send(
        f"🏆 ¡{ganador.mention} gana el duelo y {final_premio} monedas!{mult_text}"
    )
@client.tree.command(name="flip", description="Apuesta a cara o cruz")
async def flip(interaction: discord.Interaction, eleccion: str, apuesta: int):
    if eleccion.lower() not in ['cara', 'cruz']:
        await interaction.response.send_message("❌ Debes elegir 'cara' o 'cruz'")
        return

    if apuesta <= 0:
        await interaction.response.send_message("❌ La apuesta debe ser mayor que 0")
        return

    user_id = str(interaction.user.id)
    if not economy.remove_money(user_id, apuesta):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    resultado = random.choice(['cara', 'cruz'])
    _, mult_text = get_multiplier_text(interaction.user.id)
    
    if resultado == eleccion.lower():
        winnings = apuesta * 2
        final_winnings = economy.add_money(user_id, winnings)
        await interaction.response.send_message(
            f"🎲 Salió {resultado}!\n"
            f"🎉 ¡Has ganado {final_winnings} monedas!{mult_text}\n"
            f"💰 Balance: {economy.get_balance(user_id)} monedas"
        )
    else:
        await interaction.response.send_message(
            f"🎲 Salió {resultado}!\n"
            f"😔 Has perdido {apuesta} monedas\n"
            f"💰 Balance: {economy.get_balance(user_id)} monedas"
        )

@client.tree.command(name="transferir", description="Transfiere monedas a otro usuario")
async def transferir(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if usuario.id == interaction.user.id:
        await interaction.response.send_message("❌ No puedes transferirte monedas a ti mismo")
        return

    if cantidad <= 0:
        await interaction.response.send_message("❌ La cantidad debe ser mayor que 0")
        return

    sender_id = str(interaction.user.id)
    receiver_id = str(usuario.id)

    if not economy.remove_money(sender_id, cantidad):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    economy.add_money(receiver_id, cantidad)
    await interaction.response.send_message(
        f"💸 Has transferido {cantidad} monedas a {usuario.mention}\n"
        f"💰 Tu nuevo balance: {economy.get_balance(sender_id)} monedas"
    )
@client.tree.command(name="ranking_mascotas", description="Muestra el ranking de mascotas por nivel")
async def ranking_mascotas(interaction: discord.Interaction):
    # Obtener todas las mascotas y ordenarlas por nivel
    mascotas_list = []
    for user_id, mascota in sistema_mascotas.mascotas.items():
        try:
            user = await client.fetch_user(int(user_id))
            mascotas_list.append((user, mascota))
        except:
            continue

    if not mascotas_list:
        await interaction.response.send_message("❌ No hay mascotas registradas")
        return

    mascotas_list.sort(key=lambda x: (x[1].nivel, x[1].exp), reverse=True)
    
    embed = discord.Embed(
        title="🏆 Ranking de Mascotas",
        color=discord.Color.gold()
    )

    for i, (user, mascota) in enumerate(mascotas_list[:10], 1):
        emoji = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "⭐"
        embed.add_field(
            name=f"{emoji} #{i} - {mascota.nombre}",
            value=f"Dueño: {user.name}\n"
                  f"Nivel: {mascota.nivel}\n"
                  f"EXP: {mascota.exp}/{mascota.exp_necesaria()}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="estado", description="Muestra tu estado completo")
async def estado(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    embed = discord.Embed(
        title=f"📊 Estado de {interaction.user.name}",
        color=discord.Color.blue()
    )

    # Información económica
    balance = economy.get_balance(user_id)
    embed.add_field(name="💰 Balance", value=f"{balance} monedas", inline=True)

    # Información de mascotas
    if user_id in sistema_mascotas.mascotas:
        mascota = sistema_mascotas.mascotas[user_id]
        embed.add_field(
            name="🐾 Mascota",
            value=f"Nombre: {mascota.nombre}\n"
                  f"Tipo: {mascota.tipo}\n"
                  f"Nivel: {mascota.nivel}\n"
                  f"EXP: {mascota.exp}/{mascota.exp_necesaria()}\n"
                  f"Hambre: {mascota.hambre:.1f}%\n"
                  f"Felicidad: {mascota.felicidad:.1f}%",
            inline=False
        )

    # Información de efectos activos
    inventario = sistema_objetos.obtener_inventario(interaction.user.id)
    efectos_activos = inventario.obtener_efectos_activos()
    if efectos_activos:
        efectos_texto = []
        for efecto in efectos_activos:
            if efecto.duracion:
                tiempo_restante = efecto.tiempo_inicio + timedelta(seconds=efecto.duracion) - datetime.now()
                efectos_texto.append(f"{efecto.tipo.capitalize()}: {int(tiempo_restante.total_seconds() / 60)} minutos")
            else:
                efectos_texto.append(f"{efecto.tipo.capitalize()}: Permanente")
        
        embed.add_field(
            name="⚡ Efectos Activos",
            value="\n".join(efectos_texto),
            inline=False
        )

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="ruleta_vs", description="Desafía a otro usuario a la ruleta rusa")
async def ruleta_vs(interaction: discord.Interaction, oponente: discord.Member):
    if oponente.id == interaction.user.id:
        await interaction.response.send_message("❌ No puedes desafiarte a ti mismo")
        return

    if oponente.bot:
        await interaction.response.send_message("❌ No puedes desafiar a un bot")
        return

    await interaction.response.send_message(
        f"🎲 {oponente.mention}, {interaction.user.mention} te desafía a una ruleta rusa\n"
        "Tienes 30 segundos para aceptar escribiendo 'aceptar'"
    )

    def check(m):
        return m.author.id == oponente.id and m.content.lower() == "aceptar"

    try:
        await client.wait_for('message', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await interaction.channel.send("❌ Desafío cancelado por falta de respuesta")
        return

    # Inicializar la ruleta
    posicion_bala = random.randint(0, 5)  # Posición de la bala en el tambor
    posicion_actual = 0  # Posición actual del tambor
    turno_actual = random.choice([interaction.user, oponente])

    await interaction.channel.send(
        f"🎯 ¡Comienza el juego!\n"
        f"🎲 {turno_actual.mention} empieza..."
    )

    while True:
        await asyncio.sleep(2)
        
        # Mensajes de tensión aleatorios
        mensajes_tension = [
            f"🎭 *{turno_actual.name} toma el revólver con mano temblorosa...*",
            f"🎲 *{turno_actual.name} hace girar el tambor...*",
            f"🔄 *{turno_actual.name} apunta el revólver...*",
            f"🎯 *{turno_actual.name} contiene la respiración...*"
        ]
        await interaction.channel.send(random.choice(mensajes_tension))
        await asyncio.sleep(1)

        if posicion_actual == posicion_bala:
            try:
                timeout_duration = datetime.timedelta(minutes=1)
                await turno_actual.timeout(timeout_duration, reason="Perdió en la ruleta rusa VS")
                
                mensajes_muerte = [
                    f"💥 ¡BANG! {turno_actual.mention} ha caído",
                    f"💀 ¡BOOM! {turno_actual.mention} no sobrevivió",
                    f"☠️ ¡PAM! {turno_actual.mention} ha sido eliminado",
                    f"🎭 ¡BANG! {turno_actual.mention} ha perdido el juego"
                ]
                
                await interaction.channel.send(
                    f"{random.choice(mensajes_muerte)} y estará en silencio durante 1 minuto!\n"
                    f"🏆 ¡{interaction.user.mention if turno_actual == oponente else oponente.mention} es el ganador!"
                )
            except discord.errors.Forbidden:
                await interaction.channel.send(
                    f"💥 ¡BANG! {turno_actual.mention} ha perdido!\n"
                    f"🏆 ¡{interaction.user.mention if turno_actual == oponente else oponente.mention} es el ganador!\n"
                    "(No tengo permisos para aplicar el timeout)"
                )
            break
        else:
            mensajes_supervivencia = [
                f"😅 *Click* - {turno_actual.mention} sobrevive... por ahora",
                f"😌 *Click* - {turno_actual.mention} respira aliviado",
                f"😎 *Click* - {turno_actual.mention} sonríe confiado",
                f"🍀 *Click* - La suerte acompaña a {turno_actual.mention}"
            ]
            await interaction.channel.send(random.choice(mensajes_supervivencia))
            await asyncio.sleep(1)
            
            # Avanzar la posición del tambor
            posicion_actual = (posicion_actual + 1) % 6
            
            # Cambiar turno
            turno_actual = oponente if turno_actual == interaction.user else interaction.user
            await interaction.channel.send(f"🎯 Turno de {turno_actual.mention}...")

@client.tree.command(name="pelea", description="Inicia una pelea con otro usuario")
async def pelea(interaction: discord.Interaction, oponente: discord.Member):
    if oponente.id == interaction.user.id:
        await interaction.response.send_message("❌ No puedes pelear contigo mismo")
        return

    vida_jugador1 = 100
    vida_jugador2 = 100
    
    ataques = [
        ("un puñetazo", 10),
        ("una patada voladora", 15),
        ("un chanclazo", 20),
        ("un tortazo", 12),
        ("un mordisco", 8),
        ("un cabezazo", 18),
        ("un pollazo de 50cm de profundidad", 28),
        ("un beso del xapa", 19)
    ]

    await interaction.response.send_message(
        f"⚔️ ¡Comienza la pelea entre {interaction.user.mention} y {oponente.mention}!"
    )

    while vida_jugador1 > 0 and vida_jugador2 > 0:
        # Turno del jugador 1
        ataque, daño_base = random.choice(ataques)
        daño_real = random.randint(max(1, daño_base - 5), daño_base + 5)
        vida_jugador2 -= daño_real
        
        await interaction.channel.send(
            f"{interaction.user.mention} lanza {ataque} a {oponente.mention} y hace {daño_real} de daño! "
            f"(Vida restante: {max(0, vida_jugador2)})"
        )
        await asyncio.sleep(2)

        if vida_jugador2 <= 0:
            await interaction.channel.send(f"🏆 ¡{interaction.user.mention} ha ganado la pelea!")
            break

        # Turno del jugador 2
        ataque, daño_base = random.choice(ataques)
        daño_real = random.randint(max(1, daño_base - 5), daño_base + 5)
        vida_jugador1 -= daño_real
        
        await interaction.channel.send(
            f"{oponente.mention} lanza {ataque} a {interaction.user.mention} y hace {daño_real} de daño! "
            f"(Vida restante: {max(0, vida_jugador1)})"
        )
        await asyncio.sleep(2)

        if vida_jugador1 <= 0:
            await interaction.channel.send(f"🏆 ¡{oponente.mention} ha ganado la pelea!")
            break

@client.tree.command(name="carrera", description="Apuesta en una carrera de caballos")
async def carrera(interaction: discord.Interaction, apuesta: int):
    if apuesta <= 0:
        await interaction.response.send_message("❌ La apuesta debe ser mayor que 0")
        return

    user_id = str(interaction.user.id)
    if not economy.remove_money(user_id, apuesta):
        await interaction.response.send_message("❌ No tienes suficientes monedas")
        return

    caballos = [
        "🐎 Vera",
        "🐎 Vincent",
        "🐎 JuanPablo",
        "🐎 Borja",
        "🐎 Lyubo",
        "🐎 Bruno",
        "🐎 Berlinas"
    ]

    class CarreraView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.caballo_elegido = None
            self.interaction = None

        @discord.ui.select(
            placeholder="Elige tu caballo...",
            options=[discord.SelectOption(label=caballo, value=str(i)) for i, caballo in enumerate(caballos)]
        )
        async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
            self.caballo_elegido = int(select.values[0])
            self.interaction = interaction
            await interaction.response.edit_message(
                content=f"Has elegido a {caballos[self.caballo_elegido]}!\nLa carrera comenzará en 3 segundos...",
                view=None
            )
            self.stop()

        async def on_timeout(self):
            economy.add_money(user_id, apuesta)
            await self.message.edit(content="❌ Tiempo agotado. Tu apuesta ha sido devuelta.", view=None)

    view = CarreraView()
    message = await interaction.response.send_message(
        f"🏇 Bienvenido a las carreras, {interaction.user.mention}!\n"
        f"Has apostado {apuesta} monedas.\n"
        "Selecciona tu caballo:",
        view=view
    )
    view.message = await interaction.original_response()

    # Esperar a que se seleccione un caballo
    await view.wait()
    
    if view.caballo_elegido is None:
        return

    await asyncio.sleep(3)

    # Simular la carrera
    posiciones = [0] * len(caballos)
    meta = 20
    ganador = None
    mensaje_carrera = await view.interaction.channel.send("🏁 Iniciando carrera...")

    while not ganador:
        mensaje = "🏁 Estado de la carrera:\n\n"
        
        for i, caballo in enumerate(caballos):
            if random.random() < 0.7:
                posiciones[i] += random.randint(1, 3)
            
            if posiciones[i] >= meta and not ganador:
                ganador = i
            
            mensaje += f"{caballo}: {'‒' * posiciones[i]}🔵{'‒' * (meta - posiciones[i])}\n"
        
        await mensaje_carrera.edit(content=mensaje)
        await asyncio.sleep(1)

    # Determinar resultado
    if ganador == view.caballo_elegido:
        premio = apuesta * 5
        _, mult_text = get_multiplier_text(interaction.user.id)
        final_premio = economy.add_money(user_id, premio)
        await view.interaction.channel.send(
            f"🎉 ¡Tu caballo {caballos[ganador]} ha ganado!\n"
            f"Has ganado {final_premio} monedas!{mult_text}\n"
            f"💰 Balance: {economy.get_balance(user_id)} monedas"
        )
    else:
        await view.interaction.channel.send(
            f"😔 Ha ganado {caballos[ganador]}. Has perdido {apuesta} monedas.\n"
            f"💰 Balance: {economy.get_balance(user_id)} monedas"
        )
@client.tree.command(name="ayuda", description="Muestra todos los comandos disponibles")
async def ayuda(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Comandos Disponibles",
        description="Aquí tienes una lista de todos los comandos",
        color=discord.Color.blue()
    )

    # Comandos de Economía
    economia = (
        "`/balance` - Ver tu balance de monedas\n"
        "`/daily` - Reclamar monedas diarias\n"
        "`/trabajar` - Realizar un trabajo\n"
        "`/trabajos` - Ver trabajos disponibles\n"
        "`/top` - Ranking de usuarios más ricos\n"
        "`/transferir` - Transferir monedas a otro usuario"
    )
    embed.add_field(name="💰 Economía", value=economia, inline=False)

    # Comandos de Juegos
    juegos = (
        "`/dados` - Jugar a los dados\n"
        "`/tragaperras` - Jugar a la tragaperras\n"
        "`/ruleta` - Jugar a la ruleta\n"
        "`/carrera` - Apostar en carreras de caballos\n"
        "`/loteria` - Comprar un boleto de lotería\n"
        "`/rasca` - Comprar un rasca y gana\n"
        "`/flip` - Apostar a cara o cruz\n"
        "`/duelo` - Desafiar a otro usuario\n"
        "`/pelea` - Pelear contra otro usuario"
    )
    embed.add_field(name="🎮 Juegos", value=juegos, inline=False)

    # Comandos de Mascotas
    mascotas = (
        "`/comprar_mascota` - Comprar una mascota\n"
        "`/mascota` - Ver estado de tu mascota\n"
        "`/alimentar` - Alimentar a tu mascota\n"
        "`/acariciar` - Acariciar a tu mascota\n"
        "`/ranking_mascotas` - Ver ranking de mascotas"
    )
    embed.add_field(name="🐾 Mascotas", value=mascotas, inline=False)

    # Comandos de Objetos
    objetos = (
        "`/tienda` - Ver objetos disponibles\n"
        "`/comprar` - Comprar un objeto\n"
        "`/inventario` - Ver tu inventario\n"
        "`/usar` - Usar un objeto\n"
        "`/regalar` - Regalar un objeto"
    )
    embed.add_field(name="🎁 Objetos", value=objetos, inline=False)

    # Comandos de Eventos
    eventos = (
        "`/ruleta_rusa` - Jugar a la ruleta rusa\n"
        "`/ruleta_vs` - Desafiar a ruleta rusa\n"
        "`/apostar` - Hacer una apuesta con otro usuario\n"
        "`/evento` - Ver evento actual"
    )
    embed.add_field(name="🎉 Eventos", value=eventos, inline=False)

    # Comandos de Admin (solo visibles para admins)
    if interaction.user.guild_permissions.administrator:
        admin = (
            "`/sync` - Sincronizar comandos\n"
            "`/agregar_monedas` - Dar monedas a un usuario\n"
            "`/quitar_monedas` - Quitar monedas a un usuario\n"
            "`/decir` - Hacer que el bot diga algo\n"
            "`/desilenciar` - Quitar timeout a un usuario\n"
            "`/castigo` - Castigar a un usuario\n"
            "`/evento crear` - Crear un nuevo evento"
        )
        embed.add_field(name="⚡ Administración", value=admin, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)
@client.tree.command(name="perfil", description="Ver perfil detallado de un usuario")
async def perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    user_id = str(usuario.id)
    
    embed = discord.Embed(
        title=f"📊 Perfil de {usuario.name}",
        color=usuario.color
    )
    embed.set_thumbnail(url=usuario.display_avatar.url)

    # Estadísticas económicas
    balance = economy.get_balance(user_id)
    embed.add_field(name="💰 Balance", value=f"{balance} monedas", inline=True)

    # Información de mascota
    if user_id in sistema_mascotas.mascotas:
        mascota = sistema_mascotas.mascotas[user_id]
        embed.add_field(
            name="🐾 Mascota",
            value=f"Nombre: {mascota.nombre}\n"
                  f"Tipo: {mascota.tipo}\n"
                  f"Nivel: {mascota.nivel}",
            inline=True
        )

    # Efectos activos
    inventario = sistema_objetos.obtener_inventario(usuario.id)
    efectos_activos = inventario.obtener_efectos_activos()
    if efectos_activos:
        efectos_texto = []
        for efecto in efectos_activos:
            if efecto.duracion:
                tiempo_restante = efecto.tiempo_inicio + timedelta(seconds=efecto.duracion) - datetime.now()
                efectos_texto.append(f"{efecto.tipo}: {int(tiempo_restante.total_seconds() // 60)}m")
            else:
                efectos_texto.append(f"{efecto.tipo}: ∞")
        
        embed.add_field(name="⚡ Efectos", value="\n".join(efectos_texto), inline=True)

    # Estadísticas del servidor
    member = interaction.guild.get_member(usuario.id)
    if member:
        embed.add_field(
            name="📈 Estadísticas",
            value=f"Unido: {discord.utils.format_dt(member.joined_at, 'R')}\n"
                  f"Creado: {discord.utils.format_dt(usuario.created_at, 'R')}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)
@client.tree.command(name="castigo", description="Castigar a un usuario")
@tiene_rol_dictador()  
async def castigo(interaction: discord.Interaction, usuario: discord.Member, duracion: int, razon: str = None):
    try:
        await usuario.timeout(
            datetime.timedelta(minutes=duracion),
            reason=razon or f"Castigado por {interaction.user}"
        )
        
        await interaction.response.send_message(
            f"✅ {usuario.mention} ha sido castigado por {duracion} minutos\n"
            f"Razón: {razon or 'No especificada'}"
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ No tengo permisos para castigar a este usuario"
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error al aplicar el castigo: {str(e)}"
        )
@client.tree.command(name="ruleta_global", description="Inicia una ruleta rusa para todo el servidor")
async def ruleta_global(interaction: discord.Interaction):
    # Mensaje inicial
    await interaction.response.send_message(
        "🎯 ¡Comienza una ruleta rusa global!\n"
        "👥 Tienen 60 segundos para unirse escribiendo 'participo'\n"
        "💀 El perdedor recibirá un timeout de 5 minutos"
    )

    participantes = []
    start_time = datetime.now()
    
    # Fase de registro (60 segundos)
    def check(m):
        return (
            m.content.lower() == "participo" and 
            m.author not in participantes and 
            not m.author.bot
        )

    while (datetime.now() - start_time).seconds < 60:
        try:
            msg = await client.wait_for(
                'message', 
                timeout=(60 - (datetime.now() - start_time).seconds),
                check=check
            )
            participantes.append(msg.author)
            await interaction.channel.send(
                f"✅ {msg.author.mention} se ha unido a la ruleta rusa\n"
                f"👥 Participantes actuales: {len(participantes)}"
            )
        except asyncio.TimeoutError:
            break

    # Verificar si hay suficientes participantes
    if len(participantes) < 2:
        await interaction.channel.send("❌ No hay suficientes participantes para iniciar la ruleta rusa")
        return

    # Anunciar inicio del juego
    await interaction.channel.send(
        f"🎯 ¡La ruleta rusa comienza con {len(participantes)} participantes!\n"
        "💀 Que la suerte esté de su lado..."
    )
    await asyncio.sleep(2)

    # Proceso de eliminación
    ronda = 1
    while len(participantes) > 1:
        await interaction.channel.send(f"\n📍 Ronda {ronda}")
        await asyncio.sleep(1)

        # Por cada ronda, cada participante tira del gatillo
        for participante in participantes[:]:  # Usamos una copia para poder modificar la lista
            # Mensajes de tensión
            mensajes_tension = [
                f"🎭 *{participante.name} toma el revólver con mano temblorosa...*",
                f"🎲 *{participante.name} hace girar el tambor...*",
                f"🔄 *{participante.name} apunta el revólver...*",
                f"🎯 *{participante.name} contiene la respiración...*"
            ]
            await interaction.channel.send(random.choice(mensajes_tension))
            await asyncio.sleep(2)

            # 1/6 de probabilidad de morir
            if random.randint(1, 6) == 1:
                try:
                    # Aplicar timeout
                    await participante.timeout(
                        datetime.timedelta(minutes=5),
                        reason="Perdió en la ruleta rusa global"
                    )
                    participantes.remove(participante)
                    
                    # Mensajes de eliminación
                    mensajes_muerte = [
                        f"💥 ¡BANG! {participante.mention} ha caído",
                        f"💀 ¡BOOM! {participante.mention} no sobrevivió",
                        f"☠️ ¡PAM! {participante.mention} ha sido eliminado",
                        f"🎭 ¡BANG! {participante.mention} ha perdido el juego"
                    ]
                    await interaction.channel.send(
                        f"{random.choice(mensajes_muerte)}\n"
                        f"👥 Quedan {len(participantes)} participantes"
                    )
                except discord.Forbidden:
                    await interaction.channel.send(
                        f"💥 ¡BANG! {participante.mention} ha perdido, "
                        "¡pero no tengo permisos para silenciarlo!"
                    )
                break  # Si alguien muere, pasamos a la siguiente ronda
            else:
                # Mensajes de supervivencia
                mensajes_supervivencia = [
                    f"😅 *Click* - {participante.mention} sobrevive... por ahora",
                    f"😌 *Click* - {participante.mention} respira aliviado",
                    f"😎 *Click* - {participante.mention} sonríe confiado",
                    f"🍀 *Click* - La suerte acompaña a {participante.mention}"
                ]
                await interaction.channel.send(random.choice(mensajes_supervivencia))
                await asyncio.sleep(1)

        ronda += 1
        await asyncio.sleep(1)

    # Anunciar ganador
    if participantes:
        ganador = participantes[0]
        # Dar premio al ganador
        premio = 1000
        economy.add_money(str(ganador.id), premio)
        
        await interaction.channel.send(
            f"👑 ¡{ganador.mention} es el último superviviente!\n"
            f"💰 ¡Has ganado {premio} monedas por tu valentía!"
        )
    else:
        await interaction.channel.send("❌ ¡Todos los participantes han sido eliminados!")

TOKEN = "TU TOKEN"
client.run(TOKEN)
