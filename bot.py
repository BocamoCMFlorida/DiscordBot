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

    def add_money(self, user_id: str, amount: int):
        self.accounts[str(user_id)] = self.get_balance(user_id) + amount
        self.save_accounts()

    def remove_money(self, user_id: str, amount: int):
        if self.get_balance(user_id) >= amount:
            self.accounts[str(user_id)] = self.get_balance(user_id) - amount
            self.save_accounts()
            return True
        return False

class JobSystem:
    def __init__(self):
        self.jobs = {
            "minero": {"min": 100, "max": 200, "description": "Trabajas como minero, extrayendo minerales.", "cooldown_minutes": 15},
            "pescador": {"min": 50, "max": 150, "description": "Sales a pescar y traes una buena captura.", "cooldown_minutes": 10},
            "programador": {"min": 200, "max": 400, "description": "Creas código y resuelves problemas.", "cooldown_minutes": 30},
        }
        self.user_cooldowns = {}

    def can_work(self, user_id: str, job_name: str) -> bool:
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = {}
            return True
            
        if job_name not in self.user_cooldowns[user_id]:
            return True
            
        last_work_time = self.user_cooldowns[user_id].get(job_name)
        cooldown_minutes = self.jobs[job_name]["cooldown_minutes"]
        return datetime.now() - last_work_time >= timedelta(minutes=cooldown_minutes)

    def get_remaining_cooldown(self, user_id: str, job_name: str) -> timedelta:
        if user_id not in self.user_cooldowns or job_name not in self.user_cooldowns[user_id]:
            return timedelta(0)
            
        last_work_time = self.user_cooldowns[user_id][job_name]
        cooldown_minutes = self.jobs[job_name]["cooldown_minutes"]
        cooldown_end = last_work_time + timedelta(minutes=cooldown_minutes)
        
        if datetime.now() >= cooldown_end:
            return timedelta(0)
        return cooldown_end - datetime.now()

    def perform_job(self, user_id: str, job_name: str, economy: EconomySystem) -> int:
        if not self.can_work(user_id, job_name):
            return 0
            
        job = self.jobs[job_name]
        earnings = random.randint(job["min"], job["max"])
        
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = {}
        self.user_cooldowns[user_id][job_name] = datetime.now()
        
        economy.add_money(user_id, earnings)
        return earnings

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
    def from_dict(cls, data):
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
        # Verificar si tenemos el objeto y si hay suficiente cantidad
        if objeto.nombre not in self.objetos or self.objetos[objeto.nombre]["cantidad"] < 1:
            return []

        # Si el objeto es consumible, reducir la cantidad
        if self.objetos[objeto.nombre]["consumible"]:
            self.objetos[objeto.nombre]["cantidad"] -= 1
            if self.objetos[objeto.nombre]["cantidad"] == 0:
                del self.objetos[objeto.nombre]

        efectos_aplicados = []
        for efecto in objeto.efectos:
            # Crear una nueva instancia del efecto
            nuevo_efecto = Efecto(
                tipo=efecto.tipo,
                valor=efecto.valor,
                duracion=efecto.duracion,
                apilable=efecto.apilable
            )
            
            # Añadir el efecto a los efectos activos
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
        efectos=[Efecto(tipo="monedas_instantaneas", valor=500, duracion=None)],
        emoji="💵",
        max_apilamiento=5,
        consumible=True
    )

    return sistema
class EventSystem:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id
        self.evento_activo = None
        self.eventos_disponibles = [
            {
                "nombre": "lluvia_monedas",
                "titulo": "🌧️ ¡Lluvia de Monedas!",
                "descripcion": "Escribe 'recoger' para obtener monedas aleatorias",
                "duracion": 5,
                "comando": "recoger"
            },
            {
                "nombre": "carrera_veloz",
                "titulo": "🏃 ¡Carrera Veloz!",
                "descripcion": "El primero en escribir 'correr' gana el premio",
                "duracion": 3,
                "comando": "correr"
            },
            {
                "nombre": "cofre_tesoro",
                "titulo": "🎁 ¡Cofre del Tesoro!",
                "descripcion": "Escribe 'abrir' para intentar abrir el cofre",
                "duracion": 4,
                "comando": "abrir"
            },
            {
                "nombre": "invasion_zombies",
                "titulo": "🧟 ¡Invasión Zombie!",
                "descripcion": "Escribe 'disparar' para eliminar zombies",
                "duracion": 5,
                "comando": "disparar"
            },
            {
                "nombre": "loteria_flash",
                "titulo": "🎫 ¡Lotería Flash!",
                "descripcion": "Escribe 'ticket' para participar",
                "duracion": 3,
                "comando": "ticket"
            }
        ]

    async def iniciar_evento_aleatorio(self):
        if self.evento_activo:
            return

        evento = random.choice(self.eventos_disponibles)
        channel = self.bot.get_channel(self.channel_id)
        
        if not channel:
            return

        self.evento_activo = {
            "tipo": evento["nombre"],
            "fin": datetime.now() + timedelta(minutes=evento["duracion"]),
            "participantes": set()
        }

        # Anunciar evento
        embed = discord.Embed(
            title=evento["titulo"],
            description=evento["descripcion"],
            color=discord.Color.gold()
        )
        embed.add_field(
            name="⏱️ Duración",
            value=f"{evento['duracion']} minutos"
        )

        await channel.send(embed=embed)

        # Manejar el evento según su tipo
        if evento["nombre"] == "lluvia_monedas":
            await self.manejar_lluvia_monedas(channel, evento["duracion"])
        elif evento["nombre"] == "carrera_veloz":
            await self.manejar_carrera_veloz(channel, evento["duracion"])
        elif evento["nombre"] == "cofre_tesoro":
            await self.manejar_cofre_tesoro(channel, evento["duracion"])
        elif evento["nombre"] == "invasion_zombies":
            await self.manejar_invasion_zombies(channel, evento["duracion"])
        elif evento["nombre"] == "loteria_flash":
            await self.manejar_loteria_flash(channel, evento["duracion"])

        self.evento_activo = None

    async def manejar_lluvia_monedas(self, channel, duracion):
        fin = datetime.now() + timedelta(minutes=duracion)
        
        while datetime.now() < fin:
            try:
                mensaje = await self.bot.wait_for(
                    'message',
                    timeout=60,
                    check=lambda m: m.channel == channel and m.content.lower() == "recoger"
                )

                if mensaje.author.id not in self.evento_activo["participantes"]:
                    monedas = random.randint(50, 200)
                    economy.add_money(str(mensaje.author.id), monedas)
                    self.evento_activo["participantes"].add(mensaje.author.id)
                    await channel.send(f"🌧️ ¡{mensaje.author.mention} ha recogido {monedas} monedas!")

            except asyncio.TimeoutError:
                continue

        await channel.send("🌧️ ¡La lluvia de monedas ha terminado!")

    async def manejar_carrera_veloz(self, channel, duracion):
        try:
            mensaje = await self.bot.wait_for(
                'message',
                timeout=duracion * 60,
                check=lambda m: m.channel == channel and m.content.lower() == "correr"
            )
            
            premio = random.randint(300, 600)
            economy.add_money(str(mensaje.author.id), premio)
            await channel.send(f"🏃 ¡{mensaje.author.mention} ha ganado la carrera y {premio} monedas!")
        
        except asyncio.TimeoutError:
            await channel.send("🏃 Nadie completó la carrera...")

    async def manejar_cofre_tesoro(self, channel, duracion):
        fin = datetime.now() + timedelta(minutes=duracion)
        
        while datetime.now() < fin:
            try:
                mensaje = await self.bot.wait_for(
                    'message',
                    timeout=60,
                    check=lambda m: m.channel == channel and m.content.lower() == "abrir"
                )

                if mensaje.author.id not in self.evento_activo["participantes"]:
                    if random.random() < 0.3:  # 30% de probabilidad de éxito
                        premio = random.randint(200, 1000)
                        economy.add_money(str(mensaje.author.id), premio)
                        await channel.send(f"🎁 ¡{mensaje.author.mention} ha encontrado {premio} monedas en el cofre!")
                    else:
                        await channel.send(f"🎁 {mensaje.author.mention} no logró abrir el cofre...")
                    
                    self.evento_activo["participantes"].add(mensaje.author.id)

            except asyncio.TimeoutError:
                continue

        await channel.send("🎁 El cofre del tesoro ha desaparecido...")

    async def manejar_invasion_zombies(self, channel, duracion):
        fin = datetime.now() + timedelta(minutes=duracion)
        puntuaciones = {}
        
        while datetime.now() < fin:
            try:
                mensaje = await self.bot.wait_for(
                    'message',
                    timeout=60,
                    check=lambda m: m.channel == channel and m.content.lower() == "disparar"
                )

                zombies = random.randint(1, 5)
                author_id = str(mensaje.author.id)
                puntuaciones[author_id] = puntuaciones.get(author_id, 0) + zombies
                await channel.send(f"🧟 ¡{mensaje.author.mention} ha eliminado {zombies} zombies!")

            except asyncio.TimeoutError:
                continue

        # Premiar a los participantes
        if puntuaciones:
            for user_id, zombies in puntuaciones.items():
                premio = zombies * 50
                economy.add_money(user_id, premio)
                user = await self.bot.fetch_user(int(user_id))
                await channel.send(f"🏆 {user.mention} eliminó {zombies} zombies y ganó {premio} monedas!")

        await channel.send("🧟 ¡La invasión zombie ha terminado!")

    async def manejar_loteria_flash(self, channel, duracion):
        participantes = []
        
        # Fase de registro
        await channel.send("🎫 ¡Registrándose participantes para la lotería flash!")
        
        fin = datetime.now() + timedelta(minutes=duracion)
        while datetime.now() < fin:
            try:
                mensaje = await self.bot.wait_for(
                    'message',
                    timeout=60,
                    check=lambda m: m.channel == channel and m.content.lower() == "ticket"
                )

                if mensaje.author.id not in [p.id for p in participantes]:
                    participantes.append(mensaje.author)
                    await channel.send(f"🎫 {mensaje.author.mention} se ha registrado para la lotería!")

            except asyncio.TimeoutError:
                continue

        # Seleccionar ganador
        if participantes:
            ganador = random.choice(participantes)
            premio = len(participantes) * 100  # Premio basado en cantidad de participantes
            economy.add_money(str(ganador.id), premio)
            await channel.send(f"🎉 ¡{ganador.mention} ha ganado la lotería flash y {premio} monedas!")
        else:
            await channel.send("🎫 Nadie participó en la lotería flash...")


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.user_cooldowns = {}

    async def setup_hook(self):
        try:
            guild = discord.Object(id=1305217034619060304)
            # Primero limpiamos los comandos existentes
            self.tree.clear_commands(guild=guild)
            # Luego sincronizamos
            await self.tree.sync(guild=guild)
        except Exception as e:
            print(f"Error en setup_hook: {e}")

# Inicializar sistemas ANTES de crear el cliente
sistema_objetos = inicializar_sistema_objetos()
sistema_mascotas = SistemaMascotas()
economy = EconomySystem()
job_system = JobSystem()
# Crear cliente de bot
client = Bot()

# Definir eventos
@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")
    print(f"ID del bot: {client.user.id}")

    canal_id = 1305217034619060306
    canal = client.get_channel(canal_id)
    if canal:
        await canal.send("Buenos dias la paga os quiten chacho")
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



@client.tree.command(name="balance", description="Muestra tu balance de monedas")
async def balance(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    user_id = str(usuario.id)
    balance = economy.get_balance(user_id)
    
    if usuario == interaction.user:
        await interaction.response.send_message(f"💰 Tu balance actual es de {balance} monedas.")
    else:
        await interaction.response.send_message(f"💰 El balance de {usuario.mention} es de {balance} monedas.")
@client.tree.command(name="daily", description="Reclama tus monedas diarias")
@app_commands.checks.cooldown(1, 86400)
async def daily(interaction: discord.Interaction):
    amount = random.randint(100, 500)
    user_id = str(interaction.user.id)
    # Agrega monedas
    economy.add_money(user_id, amount)
    # Responde al usuario
    await interaction.response.send_message(
        f"✨ ¡Has reclamado tus {amount} monedas diarias!\n"
        f"💰 Balance actual: {economy.get_balance(user_id)} monedas"
    )

@client.tree.command(name="trabajar", description="Realiza un trabajo para ganar monedas")
async def trabajar(interaction: discord.Interaction, trabajo: str):
    user_id = str(interaction.user.id)

    if trabajo not in job_system.jobs:
        await interaction.response.send_message(
            "❌ Trabajo no válido. Trabajos disponibles:\n" +
            ", ".join(f"**{job}**" for job in job_system.jobs.keys())
        )
        return
    if not job_system.can_work(user_id, trabajo):
        remaining = job_system.get_remaining_cooldown(user_id, trabajo)
        await interaction.response.send_message(
            f"⏳ Debes esperar {int(remaining.total_seconds() // 60)} minutos y "
            f"{int(remaining.total_seconds() % 60)} segundos para trabajar de nuevo."
        )
        return
    earnings = job_system.perform_job(user_id, trabajo, economy)
    await interaction.response.send_message(
        f"💼 Has trabajado como {trabajo} y ganaste {earnings} monedas.\n"
        f"💰 Balance actual: {economy.get_balance(user_id)} monedas"
    )

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
            self.economy.add_money(self.user_id, winnings)
            result = (f"🎲 Tu dado: {user_roll}\n🎲 Mi dado: {bot_roll}\n"
                     f"🎉 ¡Ganaste {winnings} monedas!")
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

        if all(s == result[0] for s in result):
            winnings = self.apuesta * 5
            self.economy.add_money(self.user_id, winnings)
            message = f"🎰 [{' | '.join(result)}]\n🎉 ¡JACKPOT! Ganaste {winnings} monedas"
        elif result.count(result[0]) == 2 or result.count(result[1]) == 2:
            winnings = self.apuesta * 2
            self.economy.add_money(self.user_id, winnings)
            message = f"🎰 [{' | '.join(result)}]\n🎉 ¡Dos iguales! Ganaste {winnings} monedas"
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
            self.economy.add_money(self.user_id, winnings)
            result_message += f"🎉 ¡Ganaste {winnings} monedas!"
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

    efectos = inventario.usar_objeto(objeto_encontrado)
    if not efectos:
        await interaction.response.send_message("❌ No tienes ese objeto en tu inventario")
        return

    # Aplicar efectos inmediatos
    for efecto in efectos:
        if efecto.tipo == "monedas_instantaneas":
            economy.add_money(str(user_id), efecto.valor)

    # Guardar los cambios en el inventario
    sistema_objetos.save_data()

    # Mensaje de éxito
    embed = discord.Embed(
        title=f"✨ Has usado {objeto_encontrado.nombre}",
        color=discord.Color.green()
    )

    # Mostrar efectos aplicados
    efectos_texto = []
    for efecto in efectos:
        if efecto.duracion:
            efectos_texto.append(f"• {efecto.tipo.capitalize()}: Activo por {efecto.duracion//60} minutos")
        else:
            efectos_texto.append(f"• {efecto.tipo.capitalize()}: Efecto aplicado")

    if efectos_texto:
        embed.add_field(name="Efectos", value="\n".join(efectos_texto), inline=False)

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

    # Matriz del rasca
    simbolos = ["💎", "💰", "🎰", "⭐", "🎲"]
    rasca = [[random.choice(simbolos) for _ in range(3)] for _ in range(3)]

    premio = 0
    mensaje = "🎫 Tu rasca:\n\n"

    # Mostrar el rasca
    for fila in rasca:
        mensaje += " ".join(fila) + "\n"

    # Comprobar filas
    for fila in rasca:
        if len(set(fila)) == 1:
            premio += 200

    # Comprobar columnas
    for j in range(3):
        columna = [rasca[i][j] for i in range(3)]
        if len(set(columna)) == 1:
            premio += 200

    # Comprobar diagonales
    diagonal1 = [rasca[i][i] for i in range(3)]
    diagonal2 = [rasca[i][2-i] for i in range(3)]
    
    if len(set(diagonal1)) == 1:
        premio += 300
    if len(set(diagonal2)) == 1:
        premio += 300

    if premio > 0:
        economy.add_money(user_id, premio)
        mensaje += f"\n🎉 ¡Has ganado {premio} monedas!"
    else:
        mensaje += "\n😔 No hay premio"

    mensaje += f"\n💰 Balance: {economy.get_balance(user_id)} monedas"
    await interaction.response.send_message(mensaje)

@client.tree.command(name="loteria", description="Compra un boleto de lotería")
@app_commands.checks.cooldown(1, 86400)  # Una vez al día
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

    if numero_jugador == numero_ganador:
        premio = precio_boleto * 50
        economy.add_money(user_id, premio)
        await interaction.channel.send(
            f"🎉 ¡{interaction.user.mention} ha ganado la lotería!\n"
            f"Número ganador: {numero_ganador:02d}\n"
            f"Premio: {premio} monedas"
        )
    else:
        await interaction.channel.send(
            f"📢 Resultado de la lotería:\n"
            f"Tu número: {numero_jugador:02d}\n"
            f"Número ganador: {numero_ganador:02d}\n"
            "Mejor suerte la próxima vez..."
        )

@client.tree.command(name="robar", description="Intenta robar monedas a otro usuario")
@app_commands.checks.cooldown(1, 3600)  # 1 hora de cooldown
async def robar(interaction: discord.Interaction, victima: discord.Member):
    if victima.id == interaction.user.id:
        await interaction.response.send_message("❌ No puedes robarte a ti mismo")
        return

    ladron_id = str(interaction.user.id)
    victima_id = str(victima.id)

    # Verificar si la víctima tiene protección
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

    # Probabilidad de éxito base del 40%
    exito = random.random() < 0.4

    if exito:
        cantidad = random.randint(10, min(100, balance_victima))
        economy.remove_money(victima_id, cantidad)
        economy.add_money(ladron_id, cantidad)
        await interaction.response.send_message(
            f"🦹 ¡Robo exitoso! Le has robado {cantidad} monedas a {victima.mention}"
        )
    else:
        multa = random.randint(50, 200)
        if economy.remove_money(ladron_id, multa):
            economy.add_money(victima_id, multa // 2)  # La víctima recibe la mitad
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
    ganador = interaction.user if vida_retador > vida_oponente else oponente
    ganador_id = str(ganador.id)
    economy.add_money(ganador_id, total_pot)

    await interaction.channel.send(
        f"🏆 ¡{ganador.mention} gana el duelo y {total_pot} monedas!"
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
    if resultado == eleccion.lower():
        winnings = apuesta * 2
        economy.add_money(user_id, winnings)
        await interaction.response.send_message(
            f"🎲 Salió {resultado}!\n"
            f"🎉 ¡Has ganado {winnings} monedas!\n"
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
        economy.add_money(user_id, premio)
        await view.interaction.channel.send(
            f"🎉 ¡Tu caballo {caballos[ganador]} ha ganado!\n"
            f"Has ganado {premio} monedas!\n"
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

TOKEN = ""
client.run(TOKEN)
