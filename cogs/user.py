import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import asyncio
from datetime import datetime
import requests

DB_PATH = "users.db"

# ===========================
# DB
# ===========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            atcoder_id TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_atcoder_id(discord_id: str) -> str | None:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT atcoder_id FROM users WHERE discord_id = ?", (discord_id,)
    ).fetchone()
    conn.close()
    return row[0] if row else None

def save_atcoder_id(discord_id: str, atcoder_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO users (discord_id, atcoder_id) VALUES (?, ?)",
        (discord_id, atcoder_id)
    )
    conn.commit()
    conn.close()

# ===========================
# AtCoder Problems API
# ===========================
def fetch_all_submissions(atcoder_id: str) -> list:
    """全提出を取得する"""
    base_url = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions"
    from_second = 0
    all_submissions = []

    while True:
        try:
            resp = requests.get(
                base_url,
                params={"user": atcoder_id, "from_second": from_second},
                timeout=10
            )
            data = resp.json()
        except Exception as e:
            print(f"エラー: {e}")
            break

        if not data:
            break

        all_submissions.extend(data)

        if len(data) < 500:
            break

        from_second = data[-1]["epoch_second"] + 1

    return all_submissions

# ===========================
# サブコマンドグループ
# ===========================
class UserGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="user", description="アカウント関連コマンド")
        self.add_command(WAGroup())

    async def get_saved_id(self, interaction: discord.Interaction) -> str | None:
        """紐づけ済みIDを取得、未登録なら通知してNoneを返す"""
        saved_id = get_atcoder_id(str(interaction.user.id))
        if not saved_id:
            await interaction.response.send_message(
                "先に `/user register お前のAtCoderユーザー名` で登録してくれ。"
            )
        return saved_id

    @app_commands.command(name="register", description="AtCoderアカウントを紐づける")
    @app_commands.describe(atcoder_id="AtCoderのユーザー名（初回or変更時のみ）")
    async def reg_command(self, interaction: discord.Interaction, atcoder_id: str = None):
        discord_id = str(interaction.user.id)
        saved_id = get_atcoder_id(discord_id)

        if atcoder_id:
            # ユーザー名が渡されたら登録or上書き
            save_atcoder_id(discord_id, atcoder_id)
            await interaction.response.send_message(
                f"AtCoderアカウント `{atcoder_id}` を紐づけた。"
            )
        elif saved_id:
            await interaction.response.send_message(
                f"現在 `{saved_id}` が紐づいてる。変更するなら `/user ac 新しいID` で。"
            )
        else:
            await interaction.response.send_message(
                "初回は `/user ac キミのAtCoderユーザー名` で登録してくれ。"
            )

#提出した問題全て
    @app_commands.command(name="problem", description="全問題を表示")
    async def problem_command(self, interaction: discord.Interaction):
        saved_id = await self.get_saved_id(interaction)
        if not saved_id:
            return

        await interaction.response.send_message(f"`{saved_id}` の全問題を取得中...")

        loop = asyncio.get_event_loop()
        submissions = await loop.run_in_executor(None, fetch_all_submissions, saved_id)

        if not submissions:
            await interaction.edit_original_response(
                content=f"`{saved_id}` の提出が見つからなかった。キミのユーザー名を確認してくれ。"
            )
            return

        problems = sorted({s["problem_id"] for s in submissions})
        total = len(problems)
        preview_text = "\n".join(f"- {p}" for p in problems)

        embed = discord.Embed(
            title=f"{saved_id} の提出した問題",
            color=0x00cc66,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="提出済み問題の総数", value=f"**{total}** 問", inline=False)
        embed.add_field(
            name="問題一覧",
            value=f"```\n{preview_text}\n```",
            inline=False
        )
        embed.set_footer(text="AtCoder Problems API (kenkoooo)")

        await interaction.edit_original_response(content=None, embed=embed)

    @app_commands.command(name="ac", description="AC数を表示")
    async def ac_command(self, interaction: discord.Interaction):
        saved_id = await self.get_saved_id(interaction)
        if not saved_id:
            return

        await interaction.response.send_message(f"`{saved_id}` のAC済み問題を取得中...")

        loop = asyncio.get_event_loop()
        submissions = await loop.run_in_executor(None, fetch_all_submissions, saved_id)

        if not submissions:
            await interaction.edit_original_response(
                content=f"`{saved_id}` の提出が見つからなかった。キミのユーザー名を確認してくれ。"
            )
            return

        ac_problems = sorted({s["problem_id"] for s in submissions if s["result"] == "AC"})
        total = len(ac_problems)
        preview_text = "\n".join(f"- {p}" for p in ac_problems)

        embed = discord.Embed(
            title=f"{saved_id} のAC済み問題",
            color=0x00cc66,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="AC済み総数", value=f"**{total}** 問", inline=False)
        embed.add_field(
            name="問題一覧",
            value=f"```\n{preview_text}\n```",
            inline=False
        )
        embed.set_footer(text="AtCoder Problems API (kenkoooo)")

        await interaction.edit_original_response(content=None, embed=embed)

class WAGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="wa", description="WAを表示する")

class WAGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="wa", description="WAを表示する")

    async def get_saved_id(self, interaction: discord.Interaction) -> str | None:
        saved_id = get_atcoder_id(str(interaction.user.id))
        if not saved_id:
            await interaction.response.send_message(
                "先に `/user register キミのAtCoderユーザー名` で登録してくれ。"
            )
        return saved_id

    @app_commands.command(name="all", description="今までWAを取った問題を表示する")
    async def wa_all_command(self, interaction: discord.Interaction):
        saved_id = await self.get_saved_id(interaction)
        if not saved_id:
            return

        await interaction.response.send_message(f"`{saved_id}` のWAを取った問題を取得中...")

        loop = asyncio.get_event_loop()
        submissions = await loop.run_in_executor(None, fetch_all_submissions, saved_id)

        if not submissions:
            await interaction.edit_original_response(
                content=f"`{saved_id}` の提出が見つからなかった。キミのユーザー名を確認してくれ。"
            )
            return

        wa_problems = sorted({s["problem_id"] for s in submissions if s["result"] == "WA"})
        total = len(wa_problems)
        preview_text = "\n".join(f"- {p}" for p in wa_problems)

        embed = discord.Embed(
            title=f"{saved_id} のWAを取った問題",
            color=0x00cc66,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="WAを取った問題数", value=f"**{total}** 問", inline=False)
        embed.add_field(
            name="問題一覧",
            value=f"```\n{preview_text}\n```",
            inline=False
        )
        embed.set_footer(text="AtCoder Problems API (kenkoooo)")

        await interaction.edit_original_response(content=None, embed=embed)

    @app_commands.command(name="xac", description="WAを取ってまだACを取っていない問題を表示")
    async def wa_xac_command(self, interaction: discord.Interaction):
        saved_id = await self.get_saved_id(interaction)
        if not saved_id:
            return

        await interaction.response.send_message(f"`{saved_id}` のWAを取った問題を取得中...")

        loop = asyncio.get_event_loop()
        submissions = await loop.run_in_executor(None, fetch_all_submissions, saved_id)

        if not submissions:
            await interaction.edit_original_response(
                content=f"`{saved_id}` の提出が見つからなかった。キミのユーザー名を確認してくれ。"
            )
            return

        ac_problems = {s["problem_id"] for s in submissions if s["result"] == "AC"}
        wa_problems = sorted({s["problem_id"] for s in submissions if s["result"] == "WA"} - ac_problems)
        total = len(wa_problems)
        preview_text = "\n".join(f"- {p}" for p in wa_problems)

        embed = discord.Embed(
            title=f"{saved_id} のWAを取った問題",
            color=0x00cc66,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="WAを取った問題数", value=f"**{total}** 問", inline=False)
        embed.add_field(
            name="問題一覧",
            value=f"```\n{preview_text}\n```",
            inline=False
        )
        embed.set_footer(text="AtCoder Problems API (kenkoooo)")

        await interaction.edit_original_response(content=None, embed=embed)


# ===========================
# Cog本体
# ===========================
class UserCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_group = UserGroup()
        bot.tree.add_command(self.user_group)
        init_db()

# ===========================
# メインから呼ぶやつ
# ===========================
async def setup(bot: commands.Bot):
    await bot.add_cog(UserCog(bot))