import discord
from discord.ui import Button, View
from discord.interactions import Interaction
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import datetime

import json
from typing import Dict, Optional

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


# Primero el sistema de economía base
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

class DiceView(View):
    def __init__(self, user_id: str, initial_bet: int, economy):
        super().__init__()  # Quitamos el timeout para que no expire
        self.user_id = user_id
        self.apuesta = initial_bet
        self.economy = economy

        # Botón para tirar los dados
        self.roll_button = Button(
            label="🎲 Tirar dados",
            style=discord.ButtonStyle.primary,
            custom_id=f"roll_dice_{self.user_id}"
        )

        # Botón para aumentar apuesta
        self.increase_bet = Button(
            label="➕ Aumentar apuesta",
            style=discord.ButtonStyle.secondary,
            custom_id=f"increase_bet_{self.user_id}"
        )

        # Botón para disminuir apuesta
        self.decrease_bet = Button(
            label="➖ Disminuir apuesta",
            style=discord.ButtonStyle.secondary,
            custom_id=f"decrease_bet_{self.user_id}"
        )

        # Botón para salir
        self.exit_button = Button(
            label="❌ Salir",
            style=discord.ButtonStyle.danger,
            custom_id=f"exit_dice_{self.user_id}"
        )

        # Asignar callbacks
        self.roll_button.callback = self.roll_dice_callback
        self.increase_bet.callback = self.increase_bet_callback
        self.decrease_bet.callback = self.decrease_bet_callback
        self.exit_button.callback = self.exit_callback

        # Añadir botones
        self.add_item(self.roll_button)
        self.add_item(self.increase_bet)
        self.add_item(self.decrease_bet)
        self.add_item(self.exit_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == self.user_id

    async def roll_dice_callback(self, interaction: discord.Interaction):
        if not self.economy.remove_money(self.user_id, self.apuesta):
            await interaction.response.edit_message(
                content="❌ No tienes suficientes monedas para esta apuesta",
                view=self
            )
            return

        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if user_roll > bot_roll:
            winnings = self.apuesta * 2
            self.economy.add_money(self.user_id, winnings)
            result = (
                f"🎲 Tu dado: {user_roll}\n"
                f"🎲 Mi dado: {bot_roll}\n"
                f"🎉 ¡Has ganado! Recibes {winnings} monedas\n"
                f"💰 Balance actual: {self.economy.get_balance(self.user_id)} monedas\n"
                f"📍 Apuesta actual: {self.apuesta} monedas"
            )
        elif user_roll < bot_roll:
            result = (
                f"🎲 Tu dado: {user_roll}\n"
                f"🎲 Mi dado: {bot_roll}\n"
                f"💸 ¡Has perdido {self.apuesta} monedas!\n"
                f"💰 Balance actual: {self.economy.get_balance(self.user_id)} monedas\n"
                f"📍 Apuesta actual: {self.apuesta} monedas"
            )
        else:
            self.economy.add_money(self.user_id, self.apuesta)
            result = (
                f"🎲 Tu dado: {user_roll}\n"
                f"🎲 Mi dado: {bot_roll}\n"
                f"🤝 ¡Empate! Recuperas tu apuesta\n"
                f"💰 Balance actual: {self.economy.get_balance(self.user_id)} monedas\n"
                f"📍 Apuesta actual: {self.apuesta} monedas"
            )

        await interaction.response.edit_message(content=result, view=self)

    async def increase_bet_callback(self, interaction: discord.Interaction):
        new_bet = self.apuesta + 10
        if self.economy.get_balance(self.user_id) >= new_bet:
            self.apuesta = new_bet
            await interaction.response.edit_message(
                content=f"📈 Apuesta aumentada a {self.apuesta} monedas\n💰 Tu balance: {self.economy.get_balance(self.user_id)} monedas",
                view=self
            )
        else:
            await interaction.response.edit_message(
                content="❌ No tienes suficientes monedas para aumentar la apuesta",
                view=self
            )

    async def decrease_bet_callback(self, interaction: discord.Interaction):
        if self.apuesta > 10:
            self.apuesta -= 10
            await interaction.response.edit_message(
                content=f"📉 Apuesta reducida a {self.apuesta} monedas\n💰 Tu balance: {self.economy.get_balance(self.user_id)} monedas",
                view=self
            )
        else:
            await interaction.response.edit_message(
                content="❌ La apuesta mínima es de 10 monedas",
                view=self
            )

    async def exit_callback(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="👋 ¡Gracias por jugar a los dados!",
            view=self
        )


class SlotMachineView(View):
    def __init__(self, user_id: str, initial_bet: int, economy):
        super().__init__()  # Sin timeout
        self.user_id = user_id
        self.apuesta = initial_bet
        self.economy = economy

        # Botón para girar
        self.spin_button = Button(
            label="🎰 Girar",
            style=discord.ButtonStyle.primary,
            custom_id=f"spin_slots_{self.user_id}"
        )

        # Botón para aumentar apuesta
        self.increase_bet = Button(
            label="➕ Aumentar apuesta",
            style=discord.ButtonStyle.secondary,
            custom_id=f"increase_slots_{self.user_id}"
        )

        # Botón para disminuir apuesta
        self.decrease_bet = Button(
            label="➖ Disminuir apuesta",
            style=discord.ButtonStyle.secondary,
            custom_id=f"decrease_slots_{self.user_id}"
        )

        # Botón para salir
        self.exit_button = Button(
            label="❌ Salir",
            style=discord.ButtonStyle.danger,
            custom_id=f"exit_slots_{self.user_id}"
        )

        # Asignar callbacks
        self.spin_button.callback = self.spin_slots_callback
        self.increase_bet.callback = self.increase_bet_callback
        self.decrease_bet.callback = self.decrease_bet_callback
        self.exit_button.callback = self.exit_callback

        # Añadir botones
        self.add_item(self.spin_button)
        self.add_item(self.increase_bet)
        self.add_item(self.decrease_bet)
        self.add_item(self.exit_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == self.user_id

    async def spin_slots_callback(self, interaction: discord.Interaction):
        if not self.economy.remove_money(self.user_id, self.apuesta):
            await interaction.response.edit_message(
                content="❌ No tienes suficientes monedas para esta apuesta",
                view=self
            )
            return

        symbols = ["🍒", "🍊", "🍋", "🍇", "💎", "7️⃣"]
        result = [random.choice(symbols) for _ in range(3)]

        if all(s == result[0] for s in result):
            winnings = self.apuesta * 5
            self.economy.add_money(self.user_id, winnings)
            message = (
                f"🎰 [{result[0]} | {result[1]} | {result[2]}]\n"
                f"🎉 ¡JACKPOT! ¡Ganas {winnings} monedas!\n"
                f"💰 Balance actual: {self.economy.get_balance(self.user_id)} monedas\n"
                f"📍 Apuesta actual: {self.apuesta} monedas"
            )
        elif result.count(result[0]) == 2 or result.count(result[1]) == 2:
            winnings = self.apuesta * 2
            self.economy.add_money(self.user_id, winnings)
            message = (
                f"🎰 [{result[0]} | {result[1]} | {result[2]}]\n"
                f"🎉 ¡Dos iguales! ¡Ganas {winnings} monedas!\n"
                f"💰 Balance actual: {self.economy.get_balance(self.user_id)} monedas\n"
                f"📍 Apuesta actual: {self.apuesta} monedas"
            )
        else:
            message = (
                f"🎰 [{result[0]} | {result[1]} | {result[2]}]\n"
                f"💸 ¡Has perdido {self.apuesta} monedas!\n"
                f"💰 Balance actual: {self.economy.get_balance(self.user_id)} monedas\n"
                f"📍 Apuesta actual: {self.apuesta} monedas"
            )

        await interaction.response.edit_message(content=message, view=self)

    async def increase_bet_callback(self, interaction: discord.Interaction):
        new_bet = self.apuesta + 10
        if self.economy.get_balance(self.user_id) >= new_bet:
            self.apuesta = new_bet
            await interaction.response.edit_message(
                content=f"📈 Apuesta aumentada a {self.apuesta} monedas\n💰 Tu balance: {self.economy.get_balance(self.user_id)} monedas",
                view=self
            )
        else:
            await interaction.response.edit_message(
                content="❌ No tienes suficientes monedas para aumentar la apuesta",
                view=self
            )

    async def decrease_bet_callback(self, interaction: discord.Interaction):
        if self.apuesta > 10:
            self.apuesta -= 10
            await interaction.response.edit_message(
                content=f"📉 Apuesta reducida a {self.apuesta} monedas\n💰 Tu balance: {self.economy.get_balance(self.user_id)} monedas",
                view=self
            )
        else:
            await interaction.response.edit_message(
                content="❌ La apuesta mínima es de 10 monedas",
                view=self
            )

    async def exit_callback(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="👋 ¡Gracias por jugar a la tragaperras!",
            view=self
        )

# Inicializar el sistema de economía
economy = EconomySystem()

@client.tree.command(name="balance", description="Muestra tu balance de monedas")
async def balance(interaction: discord.Interaction):
    balance = economy.get_balance(str(interaction.user.id))
    await interaction.response.send_message(f"💰 Tu balance actual es de {balance} monedas")

@client.tree.command(name="daily", description="Reclama tus monedas diarias")
@app_commands.checks.cooldown(1, 86400)
async def daily(interaction: discord.Interaction):
    try:
        amount = random.randint(100, 500)
        economy.add_money(str(interaction.user.id), amount)
        await interaction.response.send_message(
            f"✨ ¡Has reclamado tus {amount} monedas diarias!\n"
            f"💰 Balance actual: {economy.get_balance(str(interaction.user.id))} monedas"
        )
    except Exception as e:
        await interaction.response.send_message(
            "❌ Ha ocurrido un error al reclamar tus monedas diarias.",
            ephemeral=True
        )

@client.tree.command(name="dados", description="Juega a los dados apostando monedas")
async def dados(interaction: discord.Interaction, apuesta: int):
    try:
        user_id = str(interaction.user.id)

        if apuesta <= 0:
            await interaction.response.send_message("❌ La apuesta debe ser mayor que 0", ephemeral=True)
            return

        if not economy.remove_money(user_id, apuesta):
            await interaction.response.send_message("❌ No tienes suficientes monedas", ephemeral=True)
            return

        # Devolver la apuesta inicial ya que se cobrará en el primer tiro
        economy.add_money(user_id, apuesta)

        view = DiceView(user_id, apuesta, economy)
        await interaction.response.send_message(
            f"🎲 {interaction.user.mention} comienza con {apuesta} monedas de apuesta...\n"
            f"💰 Tu balance actual: {economy.get_balance(user_id)} monedas\n"
            "Usa los botones para jugar!",
            view=view
        )

    except Exception as e:
        print(f"Error en dados: {e}")
        await interaction.response.send_message(
            "❌ Ha ocurrido un error jugando a los dados",
            ephemeral=True
        )

@client.tree.command(name="tragaperras", description="Juega a la tragaperras apostando monedas")
async def tragaperras(interaction: discord.Interaction, apuesta: int):
    try:
        user_id = str(interaction.user.id)

        if apuesta <= 0:
            await interaction.response.send_message("❌ La apuesta debe ser mayor que 0", ephemeral=True)
            return

        if not economy.remove_money(user_id, apuesta):
            await interaction.response.send_message("❌ No tienes suficientes monedas", ephemeral=True)
            return

        # Devolver la apuesta inicial ya que se cobrará en el primer giro
        economy.add_money(user_id, apuesta)

        view = SlotMachineView(user_id, apuesta, economy)
        await interaction.response.send_message(
            f"🎰 {interaction.user.mention} comienza con {apuesta} monedas de apuesta...\n"
            f"💰 Tu balance actual: {economy.get_balance(user_id)} monedas\n"
            "¡Usa los botones para jugar!",
            view=view
        )

    except Exception as e:
        print(f"Error en tragaperras: {e}")
        await interaction.response.send_message(
            "❌ Ha ocurrido un error en la tragaperras",
            ephemeral=True
        )

# Evento para ganar monedas por participación



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
        ("un cabezazo", 18),
        ("un pollazo de 50cm de profundidad", 28),
        ("un beso del xapa ",19)
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


@client.tree.command(name="desilenciar", description="Desilencia a un usuario silenciado (solo para Dictadores)")
@tiene_rol_dictador()
async def desilenciar(interaction: discord.Interaction, usuario: discord.Member):
    if usuario.timed_out_until:
        try:
            await usuario.edit(timed_out_until=None)  # Elimina el timeout
            await interaction.response.send_message(
                f"✅ {usuario.mention} ha sido desilenciado exitosamente.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ No se pudo desilenciar a {usuario.mention}. Error: {str(e)}",
                ephemeral=True
            )
    else:
        await interaction.response.send_message(
            f"ℹ️ {usuario.mention} no está silenciado.",
            ephemeral=True
        )

class HorseSelect(discord.ui.Select):
    def __init__(self, horses):
        options = [
            discord.SelectOption(label=horse, value=str(i))
            for i, horse in enumerate(horses)
        ]
        super().__init__(
            placeholder="Selecciona tu caballo...",
            min_values=1,
            max_values=1,
            options=options,
        )

class HorseRaceView(discord.ui.View):
    def __init__(self, user_id: str, bet_amount: int, economy):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.economy = economy
        self.horses = [
            "🐎 Vera",
            "🐎 Vincent",
            "🐎 JuanPablo",
            "🐎 Borja",
            "🐎 Lyubo",
            "🐎 Bruno",
            "🐎 Berlinas"
        ]
        self.selected_horse = None
        self.race_started = False

        # Añadir el menú de selección
        self.select = HorseSelect(self.horses)
        self.select.callback = self.horse_selected
        self.add_item(self.select)

        # Botón de inicio
        self.start_button = discord.ui.Button(
            label="¡Comenzar carrera!",
            style=discord.ButtonStyle.success,
            disabled=True
        )
        self.start_button.callback = self.start_race
        self.add_item(self.start_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "No puedes usar estos controles, no eres quien inició la carrera.",
                ephemeral=True
            )
            return False
        return True

    async def horse_selected(self, interaction: discord.Interaction):
        self.selected_horse = int(self.select.values[0])
        self.start_button.disabled = False

        await interaction.response.edit_message(
            content=f"Has seleccionado a {self.horses[self.selected_horse]}!\nPulsa el botón verde para comenzar la carrera.",
            view=self
        )

    async def start_race(self, interaction: discord.Interaction):
        if self.race_started:
            return

        self.race_started = True

        # Deshabilitar todos los controles
        self.select.disabled = True
        self.start_button.disabled = True
        await interaction.response.edit_message(view=self)

        # Configuración de la carrera
        positions = [0] * len(self.horses)
        track_length = 20

        # Mensaje inicial de la carrera
        race_track = "🏁 ¡Comienza la carrera!\n\n"
        for i, horse in enumerate(self.horses):
            race_track += f"{horse}: {'‒' * positions[i]}🔵{'‒' * (track_length - positions[i] - 1)}\n"

        race_message = await interaction.channel.send(race_track)

        # Simular la carrera
        winner = None
        rounds = 0
        max_rounds = 10

        while not winner and rounds < max_rounds:
            await asyncio.sleep(1.5)
            race_track = ""

            for i in range(len(self.horses)):
                if random.random() < 0.7:
                    positions[i] += random.randint(1, 3)

                if positions[i] >= track_length - 1:
                    positions[i] = track_length - 1
                    if not winner:
                        winner = i

                race_track += f"{self.horses[i]}: {'‒' * positions[i]}🔵{'‒' * (track_length - positions[i] - 1)}\n"

            await race_message.edit(content=race_track)
            rounds += 1

        # Si no hay ganador después de max_rounds, el caballo más adelantado gana
        if not winner:
            winner = positions.index(max(positions))

        # Determinar resultado
        if winner == self.selected_horse:
            winnings = self.bet_amount * 10
            self.economy.add_money(self.user_id, winnings)
            result_message = (
                f"🎉 ¡Tu caballo {self.horses[winner]} ha ganado!\n"
                f"¡Has ganado {winnings} monedas!\n"
                f"💰 Balance actual: {self.economy.get_balance(self.user_id)} monedas"
            )
        else:
            result_message = (
                f"😔 Tu caballo era {self.horses[self.selected_horse]}, pero ganó {self.horses[winner]}.\n"
                f"Has perdido {self.bet_amount} monedas.\n"
                f"💰 Balance actual: {self.economy.get_balance(self.user_id)} monedas"
            )

        await interaction.channel.send(result_message)

@client.tree.command(name="carrera", description="Apuesta en una carrera de caballos")
@app_commands.describe(apuesta="Cantidad de monedas a apostar")
async def carrera(interaction: discord.Interaction, apuesta: int):
    try:
        user_id = str(interaction.user.id)

        if apuesta <= 0:
            await interaction.response.send_message("❌ La apuesta debe ser mayor que 0", ephemeral=True)
            return

        if not economy.remove_money(user_id, apuesta):
            await interaction.response.send_message("❌ No tienes suficientes monedas", ephemeral=True)
            return

        view = HorseRaceView(user_id, apuesta, economy)
        await interaction.response.send_message(
            f"🏇 ¡Bienvenido a las carreras de caballos, {interaction.user.mention}!\n"
            f"Has apostado {apuesta} monedas.\n"
            "Selecciona tu caballo del menú desplegable:",
            view=view
        )

    except Exception as e:
        print(f"Error en carrera: {e}")
        economy.add_money(user_id, apuesta)
        await interaction.response.send_message(
            "❌ Ha ocurrido un error al iniciar la carrera. Tu apuesta ha sido devuelta.",
            ephemeral=True
        )
# Clase para el juego de Blackjack
class BlackjackView(View):
    def __init__(self, user_id: str, bet_amount: int, economy):
        super().__init__()
        self.user_id = user_id
        self.bet = bet_amount
        self.economy = economy
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False

        # Botones
        self.hit_button = Button(
            label="🎯 Pedir carta",
            style=discord.ButtonStyle.primary,
            custom_id="hit"
        )
        self.stand_button = Button(
            label="🛑 Plantarse",
            style=discord.ButtonStyle.danger,
            custom_id="stand"
        )

        self.hit_button.callback = self.hit
        self.stand_button.callback = self.stand

        self.add_item(self.hit_button)
        self.add_item(self.stand_button)

    def create_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = [(rank, suit) for suit in suits for rank in ranks]
        random.shuffle(deck)
        return deck

    def calculate_hand(self, hand):
        value = 0
        aces = 0

        for card in hand:
            if card[0] in ['J', 'Q', 'K']:
                value += 10
            elif card[0] == 'A':
                aces += 1
            else:
                value += int(card[0])

        for _ in range(aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1

        return value

    def format_hand(self, hand, hide_second=False):
        if hide_second and len(hand) > 1:
            return f"{hand[0][0]}{hand[0][1]} ??"
        return " ".join(f"{card[0]}{card[1]}" for card in hand)

    async def start_game(self):
        # Repartir cartas iniciales
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]

        player_value = self.calculate_hand(self.player_hand)

        # Verificar blackjack inicial
        if player_value == 21:
            self.game_over = True
            winnings = int(self.bet * 2.5)
            self.economy.add_money(self.user_id, winnings)
            return (
                f"Tu mano: {self.format_hand(self.player_hand)} (21)\n"
                f"Mano del dealer: {self.format_hand(self.dealer_hand)}\n"
                f"🎉 ¡Blackjack! Has ganado {winnings} monedas\n"
                f"💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
            )

        return (
            f"Tu mano: {self.format_hand(self.player_hand)} ({player_value})\n"
            f"Mano del dealer: {self.format_hand(self.dealer_hand, True)}"
        )

    async def hit(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            return

        self.player_hand.append(self.deck.pop())
        player_value = self.calculate_hand(self.player_hand)

        if player_value > 21:
            self.game_over = True
            message = (
                f"Tu mano: {self.format_hand(self.player_hand)} ({player_value})\n"
                f"Mano del dealer: {self.format_hand(self.dealer_hand)}\n"
                f"💸 ¡Te has pasado! Has perdido {self.bet} monedas\n"
                f"💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
            )
        else:
            message = (
                f"Tu mano: {self.format_hand(self.player_hand)} ({player_value})\n"
                f"Mano del dealer: {self.format_hand(self.dealer_hand, True)}"
            )

        if self.game_over:
            self.hit_button.disabled = True
            self.stand_button.disabled = True

        await interaction.response.edit_message(content=message, view=self)

    async def stand(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            return

        self.game_over = True
        dealer_value = self.calculate_hand(self.dealer_hand)
        player_value = self.calculate_hand(self.player_hand)

        # El dealer pide carta mientras tenga menos de 17
        while dealer_value < 17:
            self.dealer_hand.append(self.deck.pop())
            dealer_value = self.calculate_hand(self.dealer_hand)

        # Determinar ganador
        if dealer_value > 21:
            winnings = self.bet * 2
            self.economy.add_money(self.user_id, winnings)
            message = (
                f"Tu mano: {self.format_hand(self.player_hand)} ({player_value})\n"
                f"Mano del dealer: {self.format_hand(self.dealer_hand)} ({dealer_value})\n"
                f"🎉 ¡El dealer se pasó! Has ganado {winnings} monedas\n"
                f"💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
            )
        elif dealer_value < player_value:
            winnings = self.bet * 2
            self.economy.add_money(self.user_id, winnings)
            message = (
                f"Tu mano: {self.format_hand(self.player_hand)} ({player_value})\n"
                f"Mano del dealer: {self.format_hand(self.dealer_hand)} ({dealer_value})\n"
                f"🎉 ¡Has ganado! Recibes {winnings} monedas\n"
                f"💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
            )
        elif dealer_value > player_value:
            message = (
                f"Tu mano: {self.format_hand(self.player_hand)} ({player_value})\n"
                f"Mano del dealer: {self.format_hand(self.dealer_hand)} ({dealer_value})\n"
                f"💸 ¡Has perdido {self.bet} monedas!\n"
                f"💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
            )
        else:
            self.economy.add_money(self.user_id, self.bet)
            message = (
                f"Tu mano: {self.format_hand(self.player_hand)} ({player_value})\n"
                f"Mano del dealer: {self.format_hand(self.dealer_hand)} ({dealer_value})\n"
                f"🤝 ¡Empate! Recuperas tu apuesta\n"
                f"💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
            )

        self.hit_button.disabled = True
        self.stand_button.disabled = True
        await interaction.response.edit_message(content=message, view=self)

# Clase para el juego de Piedra, Papel o Tijeras
class RPSView(View):
    def __init__(self, user_id: str, bet_amount: int, economy):
        super().__init__()
        self.user_id = user_id
        self.bet = bet_amount
        self.economy = economy

        # Botones para cada opción
        self.rock_button = Button(
            label="🪨 Piedra",
            style=discord.ButtonStyle.primary,
            custom_id="rock"
        )
        self.paper_button = Button(
            label="📄 Papel",
            style=discord.ButtonStyle.primary,
            custom_id="paper"
        )
        self.scissors_button = Button(
            label="✂️ Tijeras",
            style=discord.ButtonStyle.primary,
            custom_id="scissors"
        )

        self.rock_button.callback = self.play_rock
        self.paper_button.callback = self.play_paper
        self.scissors_button.callback = self.play_scissors

        self.add_item(self.rock_button)
        self.add_item(self.paper_button)
        self.add_item(self.scissors_button)

    async def process_game(self, interaction: discord.Interaction, player_choice: str):
        if str(interaction.user.id) != self.user_id:
            return

        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)

        # Emojis para mostrar las elecciones
        choice_emojis = {
            "rock": "🪨",
            "paper": "📄",
            "scissors": "✂️"
        }

        # Determinar ganador
        if player_choice == bot_choice:
            self.economy.add_money(self.user_id, self.bet)
            result = (
                f"Tu elección: {choice_emojis[player_choice]}\n"
                f"Mi elección: {choice_emojis[bot_choice]}\n"
                f"🤝 ¡Empate! Recuperas tu apuesta\n"
                f"💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
            )
        elif (
            (player_choice == "rock" and bot_choice == "scissors") or
            (player_choice == "paper" and bot_choice == "rock") or
            (player_choice == "scissors" and bot_choice == "paper")
        ):
            winnings = self.bet * 2
            self.economy.add_money(self.user_id, winnings)
            result = (
                f"Tu elección: {choice_emojis[player_choice]}\n"
                f"Mi elección: {choice_emojis[bot_choice]}\n"
                f"🎉 ¡Has ganado! Recibes {winnings} monedas\n"
                f"💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
            )
        else:
            result = (
                f"Tu elección: {choice_emojis[player_choice]}\n"
                f"Mi elección: {choice_emojis[bot_choice]}\n"
                f"💸 ¡Has perdido {self.bet} monedas!\n"
                f"💰 Balance: {self.economy.get_balance(self.user_id)} monedas"
            )

        # Deshabilitar botones después de jugar
        self.rock_button.disabled = True
        self.paper_button.disabled = True
        self.scissors_button.disabled = True

        await interaction.response.edit_message(content=result, view=self)

    async def play_rock(self, interaction: discord.Interaction):
        await self.process_game(interaction, "rock")

    async def play_paper(self, interaction: discord.Interaction):
        await self.process_game(interaction, "paper")

    async def play_scissors(self, interaction: discord.Interaction):
        await self.process_game(interaction, "scissors")

# Comandos para los nuevos juegos
@client.tree.command(name="blackjack", description="Juega al Blackjack apostando monedas")
async def blackjack(interaction: discord.Interaction, apuesta: int):
    try:
        user_id = str(interaction.user.id)

        if apuesta <= 0:
            await interaction.response.send_message("❌ La apuesta debe ser mayor que 0", ephemeral=True)
            return

        if not economy.remove_money(user_id, apuesta):
            await interaction.response.send_message("❌ No tienes suficientes monedas", ephemeral=True)
            return

        view = BlackjackView(user_id, apuesta, economy)
        initial_state = await view.start_game()

        await interaction.response.send_message(
            f"🎲 Blackjack - Apuesta: {apuesta} monedas\n\n{initial_state}",
            view=view
        )

    except Exception as e:
        print(f"Error en blackjack: {e}")
        # Devolver la apuesta en caso de error
        economy.add_money(user_id, apuesta)
        await interaction.response.send_message(
            "❌ Ha ocurrido un error en el juego. Tu apuesta ha sido devuelta.",
            ephemeral=True
        )

@client.tree.command(name="ppt", description="Juega a Piedra, Papel o Tijeras apostando monedas")
async def ppt(interaction: discord.Interaction, apuesta: int):
    try:
        user_id = str(interaction.user.id)

        if apuesta <= 0:
            await interaction.response.send_message("❌ La apuesta debe ser mayor que 0", ephemeral=True)
            return

        if not economy.remove_money(user_id, apuesta):
            await interaction.response.send_message("❌ No tienes suficientes monedas", ephemeral=True)
            return

        view = RPSView(user_id, apuesta, economy)
        await interaction.response.send_message(
            f"🎮 Piedra, Papel o Tijeras - Apuesta: {apuesta} monedas\n"
            f"Elige tu jugada:",
            view=view
        )

    except Exception as e:
        print(f"Error en ppt: {e}")
        # Devolver la apuesta en caso de error
        economy.add_money(user_id, apuesta)
        await interaction.response.send_message(
            "❌ Ha ocurrido un error en el juego. Tu apuesta ha sido devuelta.",
            ephemeral=True
        )
class RouletteView(View):
    def __init__(self, user_id: str, bet_amount: int, economy):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.economy = economy

        # Configuración de botones para diferentes tipos de apuestas
        self.add_item(Button(label="🔴 Rojo (x2)", style=discord.ButtonStyle.red, custom_id="red"))
        self.add_item(Button(label="⚫ Negro (x2)", style=discord.ButtonStyle.secondary, custom_id="black"))
        self.add_item(Button(label="🟢 Verde (x14)", style=discord.ButtonStyle.green, custom_id="green"))
        self.add_item(Button(label="👥 Par (x2)", style=discord.ButtonStyle.blurple, custom_id="even"))
        self.add_item(Button(label="👤 Impar (x2)", style=discord.ButtonStyle.blurple, custom_id="odd"))

        # Asignar callbacks
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
        bet_type = interaction.data.get("custom_id")  # Accediendo al custom_id de forma correcta
        number = random.randint(0, 36)
        color = self.get_number_color(number)

        # Mensaje inicial
        result_message = f"🎲 La bola ha caído en el {number} ({color})\n"

        # Determinar si ganó
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
            result_message += (
                f"🎉 ¡Has ganado! Recibes {winnings} monedas\n"
                f"💰 Balance actual: {self.economy.get_balance(self.user_id)} monedas"
            )
        else:
            result_message += (
                f"😔 Has perdido {self.bet_amount} monedas\n"
                f"💰 Balance actual: {self.economy.get_balance(self.user_id)} monedas"
            )

        # Deshabilitar botones después de jugar
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(content=result_message, view=self)


# Add this command after the carrera command
@client.tree.command(name="tricolor", description="Juega a la ruleta de casino")
@app_commands.describe(apuesta="Cantidad de monedas a apostar")
async def tricolor(interaction: discord.Interaction, apuesta: int):
    try:
        user_id = str(interaction.user.id)

        if apuesta <= 0:
            await interaction.response.send_message("❌ La apuesta debe ser mayor que 0", ephemeral=True)
            return

        if not economy.remove_money(user_id, apuesta):
            await interaction.response.send_message("❌ No tienes suficientes monedas", ephemeral=True)
            return

        view = RouletteView(user_id, apuesta, economy)
        await interaction.response.send_message(
            f"🎰 ¡Bienvenido a la ruleta, {interaction.user.mention}!\n"
            f"Has apostado {apuesta} monedas.\n"
            "Elige tu apuesta:\n"
            "- 🔴 Rojo (x2): Números rojos\n"
            "- ⚫ Negro (x2): Números negros\n"
            "- 🟢 Verde (x14): El número 0\n"
            "- 👥 Par (x2): Números pares\n"
            "- 👤 Impar (x2): Números impares",
            view=view
        )

    except Exception as e:
        print(f"Error en ruleta: {e}")
        economy.add_money(user_id, apuesta)  # Devolver la apuesta en caso de error
        await interaction.response.send_message(
            "❌ Ha ocurrido un error al iniciar la ruleta. Tu apuesta ha sido devuelta.",
            ephemeral=True
        )


TOKEN = ""
client.run(TOKEN)
