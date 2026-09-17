import discord
from discord import app_commands
from discord.ext import commands

# Указываем ID вашего сервера для мгновенной регистрации слэш-команд
GUILD_ID =   # Замените на ID вашего сервера
VERIFIED_ROLE_ID =   # Замените на ID роли верифицированного пользователя
REJECTED_ROLE_ID =   # ID роли «Недопуск»

class VerificationView(discord.ui.View):
    def __init__(self, target_member: discord.Member):
        super().__init__(timeout=60)
        self.target_member = target_member

    def disable_buttons(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="Верифицировать", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        
        if not role:
            await interaction.response.send_message("Ошибка: Роль верификации не найдена.", ephemeral=True)
            return

        # Выдаем роль верификации
        await self.target_member.add_roles(role)
        
        self.disable_buttons()
        await interaction.response.edit_message(
            content=f"Пользователь {self.target_member.mention} успешно верифицирован (выдана роль **{role.name}**).", 
            view=self
        )

    @discord.ui.button(label="Недопуск", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        reject_role = interaction.guild.get_role(REJECTED_ROLE_ID)
        
        if not reject_role:
            await interaction.response.send_message("Ошибка: Роль «Недопуск» не найдена.", ephemeral=True)
            return

        # Выдаем роль недопуска
        await self.target_member.add_roles(reject_role)
        
        self.disable_buttons()
        await interaction.response.edit_message(
            content=f"Пользователю {self.target_member.mention} отказано в верификации (выдана роль **{reject_role.name}**).", 
            view=self
        )

class VerificationBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

bot = VerificationBot()

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

@bot.tree.command(name="verify", description="Запросить верификацию для пользователя")
@app_commands.describe(member="Пользователь, которого нужно проверить")
async def verify(interaction: discord.Interaction, member: discord.Member):
    v_role = interaction.guild.get_role(VERIFIED_ROLE_ID)
    r_role = interaction.guild.get_role(REJECTED_ROLE_ID)

    # Проверка: есть ли у пользователя уже одна из ролей
    if (v_role and v_role in member.roles) or (r_role and r_role in member.roles):
        await interaction.response.send_message(
            f"У пользователя {member.mention} уже есть роль верификации или недопуска.", 
            ephemeral=True
        )
        return

    view = VerificationView(target_member=member)
    await interaction.response.send_message(
        f"Выберите действие для пользователя {member.mention}:", 
        view=view, 
        ephemeral=True
    )

bot.run("YOUR_TOKEN")