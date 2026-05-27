import random
import aiohttp
import json
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import sqlite3
import asyncio
from datetime import datetime
import requests
import os

DB_PATH = "users.db"

# 色とレーティング範囲の対応
COLOR_RANGE = {
    "grey":   (0,    800),
    "brown":  (800,  1200),
    "green":  (1200, 1600),
    "cyan":   (1600, 2000),
    "blue":   (2000, 2400),
    "yellow": (2400, 2800),
    "orange": (2800, 3200),
    "red":    (3200, 10000),
}

# 色コードの対応
COLOR_HEX = {
    "grey":   0x808080,
    "brown":  0x804000,
    "green":  0x008000,
    "cyan":   0x00c0c0,
    "blue":   0x0000ff,
    "yellow": 0xc0c000,
    "orange": 0xff8000,
    "red":    0xff0000,
}

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
class ProblemGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="problem", description="問題関連コマンド")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(BASE_DIR, "..", "aa.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        self.aa_list = data["aa"]

    PROBLEMS_API = "https://kenkoooo.com/atcoder/resources/problems.json"
    DIFFICULTY_API = "https://kenkoooo.com/atcoder/resources/problem-models.json"

    async def get_saved_id(self, interaction: discord.Interaction) -> str | None:
        """紐づけ済みIDを取得、未登録なら通知してNoneを返す"""
        saved_id = get_atcoder_id(str(interaction.user.id))
        if not saved_id:
            await interaction.response.send_message(
                "先に `/user register お前のAtCoderユーザー名` で登録してくれ。"
            )
        return saved_id

    async def fetch_problems(self) -> list:
        """全問題リストを取得する"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                return await resp.json()

    async def fetch_difficulty(self) -> dict:
        """難易度データを取得する（problem_id -> difficulty）"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.DIFFICULTY_API) as resp:
                return await resp.json()

    def build_problem_url(self, problem: dict) -> str:
        """問題のURLを組み立てる"""
        return f"https://atcoder.jp/contests/{problem['contest_id']}/tasks/{problem['id']}"

    async def get_ac_ids(self, discord_id: str) -> set:
        """AC済み問題IDのセットを返す"""
        saved_id = get_atcoder_id(discord_id)
        if not saved_id:
            return set()
        loop = asyncio.get_event_loop()
        submissions = await loop.run_in_executor(None, fetch_all_submissions, saved_id)
        return {s["problem_id"] for s in submissions if s["result"] == "AC"}

    # ===========================
    # /problem random
    # ===========================
    @app_commands.command(name="random", description="AtCoderの問題をランダムに出題")
    @app_commands.describe(
        contest="コンテスト種別 (省略で全体)",
        index="問題インデックス (省略でランダム)",
        exclude_ac="ACした問題を除外するか"
    )
    @app_commands.choices(
        contest=[
            app_commands.Choice(name="全体", value="all"),
            app_commands.Choice(name="ABC", value="abc"),
            app_commands.Choice(name="ARC", value="arc"),
            app_commands.Choice(name="AGC", value="agc"),
        ],
        index=[
            app_commands.Choice(name="A", value="A"),
            app_commands.Choice(name="B", value="B"),
            app_commands.Choice(name="C", value="C"),
            app_commands.Choice(name="D", value="D"),
            app_commands.Choice(name="E", value="E"),
            app_commands.Choice(name="F", value="F"),
            app_commands.Choice(name="F2", value="F2"),
            app_commands.Choice(name="G", value="G"),
            app_commands.Choice(name="H", value="H"),
        ],
    )
    async def random_command(
        self,
        interaction: discord.Interaction,
        contest: Optional[app_commands.Choice[str]] = None,
        index: Optional[app_commands.Choice[str]] = None,
        exclude_ac: bool = False,
    ):
        await interaction.response.defer()

        problems = await self.fetch_problems()

        # コンテスト種別で絞り込む
        contest_prefix = None if (contest is None or contest.value == "all") else contest.value
        if contest_prefix:
            problems = [p for p in problems if p["contest_id"].startswith(contest_prefix)]

        # 問題インデックスで絞り込む
        if index:
            old_index = str(ord(index.value[0]) - ord("A") + 1) + index.value[1:] if index.value[0].isalpha() else index.value
            problems = [p for p in problems if p["problem_index"] in (index.value, old_index)]

        # AC済み問題を除外する
        ac_ids = set()
        if exclude_ac:
            ac_ids = await self.get_ac_ids(str(interaction.user.id))
            problems = [p for p in problems if p["id"] not in ac_ids]

        if not problems:
            await interaction.followup.send("該当する問題が見つからなかった")
            return

        problem = random.choice(problems)
        url = self.build_problem_url(problem)

        # AC済みかチェックして表示する
        ac_status = ""
        if not exclude_ac:
            if not ac_ids:
                ac_ids = await self.get_ac_ids(str(interaction.user.id))
            if problem["id"] in ac_ids:
                ac_status = " ✅ AC済み"

        embed = discord.Embed(
            title=problem["title"],
            url=url,
            color=0x00cc66 if ac_status else 0x888888,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="コンテスト", value=problem["contest_id"].upper(), inline=True)
        embed.add_field(name="問題", value=problem["problem_index"], inline=True)
        if ac_status:
            embed.add_field(name="状態", value="✅ AC済み", inline=True)
        embed.set_footer(text="AtCoder Problems API (kenkoooo)")

        await interaction.followup.send(
            f"解けるかな {random.choice(self.aa_list)}",
            embed=embed
        )

    # ===========================
    # /problem color
    # ===========================
    @app_commands.command(name="color", description="色難易度でランダム出題")
    @app_commands.describe(
        color="難易度の色",
        contest="コンテスト種別 (省略で全体)",
        exclude_ac="ACした問題を除外するか"
    )
    @app_commands.choices(
        color=[
            app_commands.Choice(name="Grey",   value="grey"),
            app_commands.Choice(name="Brown",  value="brown"),
            app_commands.Choice(name="Green",  value="green"),
            app_commands.Choice(name="Cyan",   value="cyan"),
            app_commands.Choice(name="Blue",   value="blue"),
            app_commands.Choice(name="Yellow", value="yellow"),
            app_commands.Choice(name="Orange", value="orange"),
            app_commands.Choice(name="Red",    value="red"),
        ],
        contest=[
            app_commands.Choice(name="全体", value="all"),
            app_commands.Choice(name="ABC", value="abc"),
            app_commands.Choice(name="ARC", value="arc"),
            app_commands.Choice(name="AGC", value="agc"),
        ],
    )
    async def color_command(
        self,
        interaction: discord.Interaction,
        color: str,
        contest: Optional[app_commands.Choice[str]] = None,
        exclude_ac: bool = False,
    ):
        await interaction.response.defer()

        problems, difficulty = await asyncio.gather(
            self.fetch_problems(),
            self.fetch_difficulty()
        )

        # コンテスト種別で絞り込む
        contest_prefix = None if (contest is None or contest.value == "all") else contest.value
        if contest_prefix:
            problems = [p for p in problems if p["contest_id"].startswith(contest_prefix)]

        # 色に対応するレーティング範囲で絞り込む
        low, high = COLOR_RANGE[color]
        problems = [
            p for p in problems
            if p["id"] in difficulty
            and difficulty[p["id"]].get("difficulty") is not None
            and low <= difficulty[p["id"]]["difficulty"] < high
        ]

        # AC済み問題を除外する
        ac_ids = set()
        if exclude_ac:
            ac_ids = await self.get_ac_ids(str(interaction.user.id))
            problems = [p for p in problems if p["id"] not in ac_ids]

        if not problems:
            await interaction.followup.send("該当する問題が見つからなかった")
            return

        problem = random.choice(problems)
        url = self.build_problem_url(problem)

        # AC済みかチェックして表示する
        ac_status = ""
        if not exclude_ac:
            if not ac_ids:
                ac_ids = await self.get_ac_ids(str(interaction.user.id))
            if problem["id"] in ac_ids:
                ac_status = " ✅ AC済み"

        diff = int(difficulty[problem["id"]]["difficulty"])
        embed = discord.Embed(
            title=problem["title"],
            url=url,
            color=COLOR_HEX[color] if ac_status else COLOR_HEX[color],
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="コンテスト", value=problem["contest_id"].upper(), inline=True)
        embed.add_field(name="問題", value=problem["problem_index"], inline=True)
        embed.add_field(name="Difficulty", value=str(diff), inline=True)
        if ac_status:
            embed.add_field(name="状態", value="✅ AC済み", inline=True)
        embed.set_footer(text="AtCoder Problems API (kenkoooo)")

        await interaction.followup.send(
            f"解けるかな {random.choice(self.aa_list)}",
            embed=embed
        )


    # ===========================
    # /problem select
    # ===========================
    @app_commands.command(name="select", description="特定の問題のURLと提出結果を表示")
    @app_commands.describe(problem_id="問題ID（例: abc333_a）")
    async def select_command(self, interaction: discord.Interaction, problem_id: str):
        await interaction.response.defer()

        # URLは登録なしでも表示する
        problem_url = f"https://atcoder.jp/contests/{problem_id.rsplit('_', 1)[0]}/tasks/{problem_id}"

        saved_id = get_atcoder_id(str(interaction.user.id))

        # 未登録なら提出結果なしでURLだけ返す
        if not saved_id:
            await interaction.followup.send(
                f"**{problem_id}**\n{problem_url}\n提出結果を見たいなら `/user register` で登録してくれ。"
            )
            return

        loop = asyncio.get_event_loop()
        submissions = await loop.run_in_executor(None, fetch_all_submissions, saved_id)

        # 指定した問題の提出だけ絞り込む
        target = [s for s in submissions if s["problem_id"] == problem_id]

        embed = discord.Embed(
            title=f"{problem_id}",
            color=0x00cc66 if any(s["result"] == "AC" for s in target) else 0xff4444 if target else 0x888888,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="URL", value=problem_url, inline=False)

        if not target:
            embed.add_field(name="提出結果", value="まだ提出してない", inline=False)
        else:
            results = [s["result"] for s in target]
            ac = results.count("AC")
            wa = results.count("WA")
            total = len(results)
            latest = target[-1]["result"]

            embed.add_field(name="提出回数", value=f"**{total}** 回", inline=True)
            embed.add_field(name="AC", value=f"**{ac}** 回", inline=True)
            embed.add_field(name="WA", value=f"**{wa}** 回", inline=True)
            embed.add_field(name="最新結果", value=f"**{latest}**", inline=False)

        embed.set_footer(text="AtCoder Problems API (kenkoooo)")

        await interaction.followup.send(embed=embed)

# ===========================
# Cog本体
# ===========================
class ProblemCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.problem_group = ProblemGroup()
        bot.tree.add_command(self.problem_group)
        init_db()

# ===========================
# メインから呼ぶやつ
# ===========================
async def setup(bot: commands.Bot):
    await bot.add_cog(ProblemCog(bot))