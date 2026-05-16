import random
import aiohttp
import json
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

class ProblemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    PROBLEMS_API = "https://kenkoooo.com/atcoder/resources/problems.json"

    with open("aa.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    aa_list = data["aa"]

    async def fetch_problem(self, contest_prefix=None, problem_index=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()

        if contest_prefix:
            problems = [p for p in problems if p["contest_id"].startswith(contest_prefix)]
        if problem_index:
            old_index = str(ord(problem_index[0]) - ord("A") + 1) + problem_index[1:] if problem_index[0].isalpha() else problem_index
            problems = [p for p in problems if p["problem_index"] in (problem_index, old_index)]

        if not problems:
            return None

        return random.choice(problems)

    def build_message(self, problem):
        contest_id = problem["contest_id"]
        problem_id = problem["id"]
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        return f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}"

    # コンテストと問題インデックスを選択肢で受け取る1つのコマンドに集約
    @app_commands.command(description="AtCoderの問題をランダムに出題")
    @app_commands.describe(
        contest="コンテスト種別 (省略で全体)",
        index="問題インデックス (省略でランダム)",
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
    async def problem(
        self,
        interaction: discord.Interaction,
        contest: Optional[app_commands.Choice[str]] = None,
        index: Optional[app_commands.Choice[str]] = None,
    ):
        contest_prefix = None if (contest is None or contest.value == "all") else contest.value
        problem_index = index.value if index else None

        problem = await self.fetch_problem(contest_prefix, problem_index)

        if problem is None:
            await interaction.response.send_message("該当する問題が見つからなかった", ephemeral=True)
            return

        await interaction.response.send_message(self.build_message(problem))

async def setup(bot):
    await bot.add_cog(ProblemCog(bot))