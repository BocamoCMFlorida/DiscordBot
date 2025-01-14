import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import datetime
import pyjokes

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
        self.user_cooldowns = {}

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


@client.tree.command(name="ruleta", description="Juega a la ruleta rusa (timeout)")
@app_commands.checks.cooldown(1, 30)  # Una vez cada 30 segundos
async def ruleta(interaction: discord.Interaction):
    try:
        # Sistema de racha de supervivencia
        if not hasattr(client, 'ruleta_counters'):
            client.ruleta_counters = {}
        
        user_id = str(interaction.user.id)
        if user_id not in client.ruleta_counters:
            client.ruleta_counters[user_id] = 0
            
        # Mensajes dramáticos para añadir tensión
        mensajes_tension = [
            "🎭 *Girando el tambor lentamente...*",
            "🎲 *El tambor da vueltas...*",
            "🔄 *Click... click... click...*",
            "🎯 *El destino está en juego...*"
        ]
        
        # Mensaje inicial con racha
        racha_texto = f" (Racha de supervivencia: {client.ruleta_counters[user_id]})" if client.ruleta_counters[user_id] > 0 else ""
        await interaction.response.send_message(f"🔫 {interaction.user.mention} toma el revólver con mano temblorosa...{racha_texto}")
        
        # Pausa dramática con mensaje de tensión
        mensaje_tension = random.choice(mensajes_tension)
        await asyncio.sleep(1.5)
        await interaction.channel.send(mensaje_tension)
        await asyncio.sleep(1.5)

        # Determinar el resultado (1/6 de probabilidad)
        if random.randint(1, 6) == 1:
            # El usuario "pierde"
            try:
                timeout_duration = datetime.timedelta(minutes=1)
                await interaction.user.timeout(timeout_duration, reason="Perdió en la ruleta rusa")
                
                # Resetear contador de racha
                client.ruleta_counters[user_id] = 0
                
                # Mensajes dramáticos de derrota
                mensajes_derrota = [
                    f"💥 ¡BANG! {interaction.user.mention} ha perdido y estará en silencio durante 1 minuto! (Racha perdida)",
                    f"💀 ¡BOOM! La suerte no estuvo del lado de {interaction.user.mention}. ¡1 minuto de silencio! (Racha perdida)",
                    f"🎭 ¡PAM! {interaction.user.mention} apostó y perdió. 1 minuto de reflexión en silencio... (Racha perdida)",
                    f"☠️ ¡BANG! {interaction.user.mention} debería haber elegido mejor... 1 minuto de timeout. (Racha perdida)"
                ]
                
                await interaction.channel.send(random.choice(mensajes_derrota))
                
            except discord.errors.Forbidden:
                await interaction.channel.send("💥 ¡BANG! ¡Has perdido! Pero no tengo permisos para silenciarte 😅")
        else:
            # Incrementar contador de racha
            client.ruleta_counters[user_id] += 1
            nueva_racha = client.ruleta_counters[user_id]
            
            # Mensajes de supervivencia con racha
            mensajes_supervivencia = [
                f"😅 *Click* - {interaction.user.mention} respira aliviado... (Racha: {nueva_racha})",
                f"😌 *Click* - La suerte sonríe a {interaction.user.mention} esta vez (Racha: {nueva_racha})",
                f"😎 *Click* - {interaction.user.mention} vive para jugar otro día (Racha: {nueva_racha})",
                f"🍀 *Click* - {interaction.user.mention} ha sobrevivido de milagro (Racha: {nueva_racha})"
            ]
            
            # Mensajes especiales para rachas altas
            if nueva_racha >= 10:
                await interaction.channel.send(f"{random.choice(mensajes_supervivencia)}\n🏆 ¡Impresionante racha de supervivencia!")
            elif nueva_racha >= 5:
                await interaction.channel.send(f"{random.choice(mensajes_supervivencia)}\n⭐ ¡Gran racha!")
            else:
                await interaction.channel.send(random.choice(mensajes_supervivencia))

    except Exception as e:
        print(f"Error en el comando ruleta: {str(e)}")
        try:
            await interaction.channel.send("❌ Ha ocurrido un error al procesar el comando. Por favor, inténtalo de nuevo.")
        except:
            pass






@client.tree.command(name="ruleta_vs", description="Juega a la ruleta rusa contra otro jugador")
async def ruleta_vs(interaction: discord.Interaction, oponente: discord.Member):
    if oponente == interaction.user:
        await interaction.response.send_message("No puedes jugar contra ti mismo 🤔")
        return
        
    if oponente.bot:
        await interaction.response.send_message("No puedes jugar contra un bot 🤖")
        return

    # Inicializar la ruleta
    balas = list(range(6))  # 6 recámaras
    bala_mortal = random.randint(0, 5)  # Posición de la bala
    turno_actual = random.choice([interaction.user, oponente])  # Elegir quién empieza aleatoriamente
    
    await interaction.response.send_message(
        f"🎲 ¡Comienza el juego de la ruleta rusa entre {interaction.user.mention} y {oponente.mention}!\n"
        f"🎯 {turno_actual.mention} comienza..."
    )
    
    while True:
        # Esperar un momento para crear tensión
        await asyncio.sleep(2)
        
        # Girar el tambor
        posicion_actual = random.choice(balas)
        balas.remove(posicion_actual)  # Eliminar la posición usada
        
        # Verificar si es la bala mortal
        if posicion_actual == bala_mortal:
            try:
                # El jugador actual pierde
                timeout_duration = datetime.timedelta(minutes=1)
                await turno_actual.timeout(timeout_duration, reason="Perdió en la ruleta rusa vs")
                await interaction.channel.send(
                    f"💥 ¡BANG! {turno_actual.mention} ha perdido y estará en silencio durante 1 minuto!\n"
                    f"🏆 ¡{interaction.user.mention if turno_actual == oponente else oponente.mention} es el ganador!"
                )
            except discord.errors.Forbidden:
                await interaction.channel.send(
                    f"💥 ¡BANG! {turno_actual.mention} ha perdido!\n"
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import datetime
import pyjokes

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
        self.user_cooldowns = {}

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


@client.tree.command(name="ruleta", description="Juega a la ruleta rusa (timeout)")
@app_commands.checks.cooldown(1, 30)  # Una vez cada 30 segundos
async def ruleta(interaction: discord.Interaction):
    try:
        # Sistema de racha de supervivencia
        if not hasattr(client, 'ruleta_counters'):
            client.ruleta_counters = {}
        
        user_id = str(interaction.user.id)
        if user_id not in client.ruleta_counters:
            client.ruleta_counters[user_id] = 0
            
        # Mensajes dramáticos para añadir tensión
        mensajes_tension = [
            "🎭 *Girando el tambor lentamente...*",
            "🎲 *El tambor da vueltas...*",
            "🔄 *Click... click... click...*",
            "🎯 *El destino está en juego...*"
        ]
        
        # Mensaje inicial con racha
        racha_texto = f" (Racha de supervivencia: {client.ruleta_counters[user_id]})" if client.ruleta_counters[user_id] > 0 else ""
        await interaction.response.send_message(f"🔫 {interaction.user.mention} toma el revólver con mano temblorosa...{racha_texto}")
        
        # Pausa dramática con mensaje de tensión
        mensaje_tension = random.choice(mensajes_tension)
        await asyncio.sleep(1.5)
        await interaction.channel.send(mensaje_tension)
        await asyncio.sleep(1.5)

        # Determinar el resultado (1/6 de probabilidad)
        if random.randint(1, 6) == 1:
            # El usuario "pierde"
            try:
                timeout_duration = datetime.timedelta(minutes=1)
                await interaction.user.timeout(timeout_duration, reason="Perdió en la ruleta rusa")
                
                # Resetear contador de racha
                client.ruleta_counters[user_id] = 0
                
                # Mensajes dramáticos de derrota
                mensajes_derrota = [
                    f"💥 ¡BANG! {interaction.user.mention} ha perdido y estará en silencio durante 1 minuto! (Racha perdida)",
                    f"💀 ¡BOOM! La suerte no estuvo del lado de {interaction.user.mention}. ¡1 minuto de silencio! (Racha perdida)",
                    f"🎭 ¡PAM! {interaction.user.mention} apostó y perdió. 1 minuto de reflexión en silencio... (Racha perdida)",
                    f"☠️ ¡BANG! {interaction.user.mention} debería haber elegido mejor... 1 minuto de timeout. (Racha perdida)"
                ]
                
                await interaction.channel.send(random.choice(mensajes_derrota))
                
            except discord.errors.Forbidden:
                await interaction.channel.send("💥 ¡BANG! ¡Has perdido! Pero no tengo permisos para silenciarte 😅")
        else:
            # Incrementar contador de racha
            client.ruleta_counters[user_id] += 1
            nueva_racha = client.ruleta_counters[user_id]
            
            # Mensajes de supervivencia con racha
            mensajes_supervivencia = [
                f"😅 *Click* - {interaction.user.mention} respira aliviado... (Racha: {nueva_racha})",
                f"😌 *Click* - La suerte sonríe a {interaction.user.mention} esta vez (Racha: {nueva_racha})",
                f"😎 *Click* - {interaction.user.mention} vive para jugar otro día (Racha: {nueva_racha})",
                f"🍀 *Click* - {interaction.user.mention} ha sobrevivido de milagro (Racha: {nueva_racha})"
            ]
            
            # Mensajes especiales para rachas altas
            if nueva_racha >= 10:
                await interaction.channel.send(f"{random.choice(mensajes_supervivencia)}\n🏆 ¡Impresionante racha de supervivencia!")
            elif nueva_racha >= 5:
                await interaction.channel.send(f"{random.choice(mensajes_supervivencia)}\n⭐ ¡Gran racha!")
            else:
                await interaction.channel.send(random.choice(mensajes_supervivencia))

    except Exception as e:
        print(f"Error en el comando ruleta: {str(e)}")
        try:
            await interaction.channel.send("❌ Ha ocurrido un error al procesar el comando. Por favor, inténtalo de nuevo.")
        except:
            pass






@client.tree.command(name="ruleta_vs", description="Juega a la ruleta rusa contra otro jugador")
async def ruleta_vs(interaction: discord.Interaction, oponente: discord.Member):
    if oponente == interaction.user:
        await interaction.response.send_message("No puedes jugar contra ti mismo 🤔")
        return
        
    if oponente.bot:
        await interaction.response.send_message("No puedes jugar contra un bot 🤖")
        return

    # Inicializar la ruleta
    balas = list(range(6))  # 6 recámaras
    bala_mortal = random.randint(0, 5)  # Posición de la bala
    turno_actual = random.choice([interaction.user, oponente])  # Elegir quién empieza aleatoriamente
    
    await interaction.response.send_message(
        f"🎲 ¡Comienza el juego de la ruleta rusa entre {interaction.user.mention} y {oponente.mention}!\n"
        f"🎯 {turno_actual.mention} comienza..."
    )
    
    while True:
        # Esperar un momento para crear tensión
        await asyncio.sleep(2)
        
        # Girar el tambor
        posicion_actual = random.choice(balas)
        balas.remove(posicion_actual)  # Eliminar la posición usada
        
        # Verificar si es la bala mortal
        if posicion_actual == bala_mortal:
            try:
                # El jugador actual pierde
                timeout_duration = datetime.timedelta(minutes=1)
                await turno_actual.timeout(timeout_duration, reason="Perdió en la ruleta rusa vs")
                await interaction.channel.send(
                    f"💥 ¡BANG! {turno_actual.mention} ha perdido y estará en silencio durante 1 minuto!\n"
                    f"🏆 ¡{interaction.user.mention if turno_actual == oponente else oponente.mention} es el ganador!"
                )
            except discord.errors.Forbidden:
                await interaction.channel.send(
                    f"💥 ¡BANG! {turno_actual.mention} ha perdido!\n"
                    f"🏆 ¡{interaction.user.mention if turno_actual == oponente else oponente.mention} es el ganador!\n"
                    f"(No pude aplicar el timeout por falta de permisos)"
                )
            break
        else:
            await interaction.channel.send(
                f"*Click* - {turno_actual.mention} ha sobrevivido esta ronda..."
            )
            # Cambiar el turno
            turno_actual = oponente if turno_actual == interaction.user else interaction.user
            await interaction.channel.send(f"🎯 Turno de {turno_actual.mention}...")

@client.tree.command(name="pelea", description="Inicia una pelea con otro usuario")
async def pelea(interaction: discord.Interaction, oponente: discord.Member):
    if oponente == interaction.user:
        await interaction.response.send_message("¿Te quieres pegar a ti mismo? 🤔")
        return
        
    vida_jugador1 = 100
    vida_jugador2 = 100
    ataques = [
        ("un puñetazo", 10),
        ("una patada voladora", 15),
        ("un chanclazo", 20),
        ("un tortazo", 12),
        ("un mordisco", 8),
        ("un cabezazo", 18)
    ]
    
    await interaction.response.send_message(
        f"¡Comienza la pelea entre {interaction.user.mention} y {oponente.mention}!"
    )
    
    while vida_jugador1 > 0 and vida_jugador2 > 0:
        # Turno del jugador 1
        ataque, daño = random.choice(ataques)
        daño_real = random.randint(max(1, daño - 5), daño + 5)
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
        ataque, daño = random.choice(ataques)
        daño_real = random.randint(max(1, daño - 5), daño + 5)
        vida_jugador1 -= daño_real
        await interaction.channel.send(
            f"{oponente.mention} lanza {ataque} a {interaction.user.mention} y hace {daño_real} de daño! "
            f"(Vida restante: {max(0, vida_jugador1)})"
        )
        await asyncio.sleep(2)
        
        if vida_jugador1 <= 0:
            await interaction.channel.send(f"🏆 ¡{oponente.mention} ha ganado la pelea!")
            break
    
   
     

    
TOKEN = ""  
client.run(TOKEN)
