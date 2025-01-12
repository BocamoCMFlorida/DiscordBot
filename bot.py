import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random

def tiene_rol_dictador():
    async def predicate(interaction: discord.Interaction) -> bool:
        rol_dictador = discord.utils.get(interaction.guild.roles, name="Dictador")
        if rol_dictador is None:
            await interaction.response.send_message("El rol 'Dictador' no existe en este servidor.", ephemeral=True)
            return False

        return rol_dictador in interaction.user.roles
    return app_commands.check(predicate)

# Configuración de intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Lista de mensajes a detectar
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

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        try:
            guild = discord.Object(id=1305217034619060304)  
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        except Exception as e:
            print(f"Error en setup_hook: {e}")

client = Bot()

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")
    print(f"ID del bot: {client.user.id}")

    # Enviar mensaje a un canal específico al iniciar el bot
    canal_id = 1305217034619060306  
    canal = client.get_channel(canal_id)
    if canal:
        await canal.send("Buenos dias la paga os quiten chacho")

@client.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == client.user:
        return

    # Convertir el mensaje a minúsculas para mejor detección
    contenido = message.content.lower()

    # Verificar si el mensaje contiene alguna palabra o frase a detectar
    if any(mensaje.lower() in contenido for mensaje in MENSAJES_A_DETECTAR):
        # Seleccionar una respuesta aleatoria
        respuesta = random.choice(RESPUESTAS)
        await message.channel.send(respuesta)

    # Procesar comandos
    await client.process_commands(message)

@client.tree.command(name="sync", description="Sincroniza los comandos del bot")
@app_commands.checks.has_permissions(administrator=True)
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

@client.tree.command(name="decir", description="El bot repetirá lo que digas")
@tiene_rol_dictador()
async def decir(interaction: discord.Interaction, mensaje: str):
    try:
        await interaction.response.send_message("Mensaje enviado.", ephemeral=True)
        await interaction.channel.send(mensaje)
    except Exception as e:
        await interaction.response.send_message(
            "No tienes el rol de Dictador para usar este comando.",
            ephemeral=True
        )

TOKEN = ""  
client.run(TOKEN)