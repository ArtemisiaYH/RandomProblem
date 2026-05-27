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
    ken_base_url = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions"
    from_second = 0
    all_submissions = []

    while True:
        try:
            resp = requests.get(
                ken_base_url,
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

def get_all_users() -> list[tuple[str, str]]:
    """全登録ユーザーを取得する"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT discord_id, atcoder_id FROM users").fetchall()
    conn.close()
    return rows

def fetch_atcoder_rating(atcoder_id: str) -> int:
    try:
        resp = requests.get(
            f"https://atcoder.jp/users/{atcoder_id}/history.json",
            timeout=10
        )
        if resp.status_code != 200:
            return 0  # 取得失敗も0扱い
        data = resp.json()
        return data[-1]["NewRating"] if data else 0
    except Exception:
        return 0
    
def fetch_atcoder_ac(atcoder_id: str) -> int:
    try:
        resp = requests.get(
        "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions",
        params={"user": atcoder_id, "from_second": 0},
        timeout=10
        )
        if resp.status_code != 200:
            return 0  # 取得失敗も0扱い
        data = resp.json()
        if not data:
            return 0
        else:
            ac_problems = {
                s["problem_id"]
                for s in data
                if s["result"] == "AC"
            }
            num_ac = len(ac_problems)
            return num_ac
    except Exception:
        return 0
    
def fetch_atcoder_wa(atcoder_id: str) -> int:
    try:
        resp = requests.get(
        "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions",
        params={"user": atcoder_id, "from_second": 0},
        timeout=10
        )
        if resp.status_code != 200:
            return 0  # 取得失敗も0扱い
        data = resp.json()
        if not data:
            return 0
        else:
            wa_problems = {
                s["problem_id"]
                for s in data
                if s["result"] == "WA"
            }
            num_wa = len(wa_problems)
            return num_wa
    except Exception:
        return 0
    
def fetch_atcoder_total_point(atcoder_id: str) -> int:
    # fetch_all_submissions で全提出を取得（ページネーション込み）
    submissions = fetch_all_submissions(atcoder_id)
    if not submissions:
        return 0

    # 同じ問題を複数回ACしてる場合は最高点だけ使う
    best_points = {}
    for s in submissions:
        if s["result"] == "AC":
            pid = s["problem_id"]
            best_points[pid] = max(best_points.get(pid, 0), s["point"])

    return int(sum(best_points.values()))

def fetch_atcoder_contest_points(atcoder_id: str) -> dict[str, int]:
    # コンテストIDをキー、得点の合計を値にしたdictを返す
    submissions = fetch_all_submissions(atcoder_id)
    if not submissions:
        return {}

    # コンテストごとに問題の最高点を集める
    contest_best: dict[str, dict[str, float]] = {}
    for s in submissions:
        if s["result"] == "AC":
            cid = s["contest_id"]
            pid = s["problem_id"]
            if cid not in contest_best:
                contest_best[cid] = {}
            contest_best[cid][pid] = max(
                contest_best[cid].get(pid, 0), s["point"]
            )

    # コンテストごとに合計する
    return {
        cid: int(sum(problems.values()))
        for cid, problems in contest_best.items()
    }
    
def get_rate_color(rating: int) -> tuple[str, int]:
    """レートに対応する色名とDiscord埋め込みカラーを返す"""
    thresholds = [
        (2800, "赤",  0xFF0000),
        (2400, "橙",  0xFF8000),
        (2000, "黄",  0xC0C000),
        (1600, "青",  0x0000FF),
        (1200, "水",  0x00C0C0),
        ( 800, "緑",  0x008000),
        ( 400, "茶",  0x804000),
    ]
    for threshold, name, color in thresholds:
        if rating >= threshold:
            return name, color
    return "灰", 0x808080

# ===========================
# サブコマンドグループ
# ===========================
class RankGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="ranking", description="ランキング関連コマンド")
        self.add_command(PointGroup())  # ← これを追加

    async def get_saved_id(self, interaction: discord.Interaction) -> str | None:
        """紐づけ済みIDを取得、未登録なら通知してNoneを返す"""
        saved_id = get_atcoder_id(str(interaction.user.id))
        if not saved_id:
            await interaction.response.send_message(
                "先に `/user register お前のAtCoderユーザー名` で登録してくれ。"
            )
        return saved_id
    
    @app_commands.command(name="rate", description="サーバーのAtCoderレートランキングを表示")
    async def rate_command(self, interaction: discord.Interaction):
        # レート取得は重いのでdeferは必須
        await interaction.response.defer()

        all_users = get_all_users()
        if not all_users:
            await interaction.followup.send("誰も登録してないぞ。`/user register` から始めろ。")
            return

        # このサーバーのメンバーだけに絞る
        guild_member_ids = {str(m.id) for m in interaction.guild.members}
        target_users = [
            (discord_id, ac_id)
            for discord_id, ac_id in all_users
            if discord_id in guild_member_ids
        ]

        if not target_users:
            await interaction.followup.send("このサーバーに登録済みユーザーがいないぞ。")
            return

        # 複数ユーザーのレートを並列で取得する
        async def fetch_rating_async(discord_id: str, ac_id: str):
            loop = asyncio.get_event_loop()
            rating = await loop.run_in_executor(None, fetch_atcoder_rating, ac_id)
            return discord_id, ac_id, rating

        results = await asyncio.gather(
            *[fetch_rating_async(d_id, ac_id) for d_id, ac_id in target_users]
        )

        valid = valid = list(results)
        valid.sort(key=lambda x: x[2], reverse=True)

        if not valid:
            await interaction.followup.send("レートの取得に全部失敗した。AtCoderのIDを確認しろ。")
            return

        # Embedを組み立てる
        lines = []
        for rank, (discord_id, ac_id, rating) in enumerate(valid, 1):
            member = interaction.guild.get_member(int(discord_id))
            display_name = member.display_name if member else f"<@{discord_id}>"
            color_name, _ = get_rate_color(rating)

            medal = {1: "1st", 2: "2nd", 3: "3rd"}.get(rank, f"`{rank:2}.`")
            lines.append(
                f"{medal} **{rating}** ({color_name})"
                f"{display_name}"
                f"[{ac_id}](https://atcoder.jp/users/{ac_id})"
            )

        # 25行超えるとEmbedの文字数制限に引っかかるので分割
        CHUNK = 25
        embeds = []
        for i in range(0, len(lines), CHUNK):
            chunk = lines[i:i + CHUNK]
            embed = discord.Embed(
                title="⚔️ AtCoder レートランキング" if i == 0 else "",
                description="\n".join(chunk),
                color=0x00BFFF,
            )
            if i == 0:
                embed.set_footer(
                    text=f"登録: {len(valid)}人更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
            embeds.append(embed)

        await interaction.followup.send(embeds=embeds)

    @app_commands.command(name="ac", description="サーバーのAtCoderのAC数ランキングを表示")
    async def ac_command(self, interaction: discord.Interaction):
        # レート取得は重いのでdeferは必須
        await interaction.response.defer()

        all_users = get_all_users()
        if not all_users:
            await interaction.followup.send("誰も登録してないぞ。`/user register` から始めろ。")
            return

        # このサーバーのメンバーだけに絞る
        guild_member_ids = {str(m.id) for m in interaction.guild.members}
        target_users = [
            (discord_id, ac_id)
            for discord_id, ac_id in all_users
            if discord_id in guild_member_ids
        ]

        if not target_users:
            await interaction.followup.send("このサーバーに登録済みユーザーがいないぞ。")
            return

        # 複数ユーザーのレートを並列で取得する
        async def fetch_ac_async(discord_id: str, ac_id: str):
            loop = asyncio.get_event_loop()
            acing = await loop.run_in_executor(None, fetch_atcoder_ac, ac_id)
            return discord_id, ac_id, acing

        results = await asyncio.gather(
            *[fetch_ac_async(d_id, ac_id) for d_id, ac_id in target_users]
        )

        valid = valid = list(results)
        valid.sort(key=lambda x: x[2], reverse=True)

        if not valid:
            await interaction.followup.send("レートの取得に全部失敗した。AtCoderのIDを確認しろ。")
            return

        # Embedを組み立てる
        lines = []
        for rank, (discord_id, ac_id, acing) in enumerate(valid, 1):
            member = interaction.guild.get_member(int(discord_id))
            display_name = member.display_name if member else f"<@{discord_id}>"

            medal = {1: "1st", 2: "2nd", 3: "3rd"}.get(rank, f"`{rank:2}.`")
            lines.append(
                f"{medal} **{acing}**"
                f"{display_name}"
                f"[{ac_id}](https://atcoder.jp/users/{ac_id})"
            )

        # 25行超えるとEmbedの文字数制限に引っかかるので分割
        CHUNK = 25
        embeds = []
        for i in range(0, len(lines), CHUNK):
            chunk = lines[i:i + CHUNK]
            embed = discord.Embed(
                title="⚔️ AtCoder ACランキング" if i == 0 else "",
                description="\n".join(chunk),
                color=0x00BFFF,
            )
            if i == 0:
                embed.set_footer(
                    text=f"登録: {len(valid)}人更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
            embeds.append(embed)

        await interaction.followup.send(embeds=embeds)

    @app_commands.command(name="wa", description="サーバーのAtCoderのWA数ランキングを表示")
    async def wa_command(self, interaction: discord.Interaction):
        # レート取得は重いのでdeferは必須
        await interaction.response.defer()

        all_users = get_all_users()
        if not all_users:
            await interaction.followup.send("誰も登録してないぞ。`/user register` から始めろ。")
            return

        # このサーバーのメンバーだけに絞る
        guild_member_ids = {str(m.id) for m in interaction.guild.members}
        target_users = [
            (discord_id, ac_id)
            for discord_id, ac_id in all_users
            if discord_id in guild_member_ids
        ]

        if not target_users:
            await interaction.followup.send("このサーバーに登録済みユーザーがいないぞ。")
            return

        # 複数ユーザーのレートを並列で取得する
        async def fetch_ac_async(discord_id: str, ac_id: str):
            loop = asyncio.get_event_loop()
            waing = await loop.run_in_executor(None, fetch_atcoder_wa, ac_id)
            return discord_id, ac_id, waing

        results = await asyncio.gather(
            *[fetch_ac_async(d_id, ac_id) for d_id, ac_id in target_users]
        )

        valid = valid = list(results)
        valid.sort(key=lambda x: x[2], reverse=True)

        if not valid:
            await interaction.followup.send("レートの取得に全部失敗した。AtCoderのIDを確認しろ。")
            return

        # Embedを組み立てる
        lines = []
        for rank, (discord_id, ac_id, waing) in enumerate(valid, 1):
            member = interaction.guild.get_member(int(discord_id))
            display_name = member.display_name if member else f"<@{discord_id}>"

            medal = {1: "1st", 2: "2nd", 3: "3rd"}.get(rank, f"`{rank:2}.`")
            lines.append(
                f"{medal} **{waing}**"
                f"{display_name}"
                f"[{ac_id}](https://atcoder.jp/users/{ac_id})"
            )

        # 25行超えるとEmbedの文字数制限に引っかかるので分割
        CHUNK = 25
        embeds = []
        for i in range(0, len(lines), CHUNK):
            chunk = lines[i:i + CHUNK]
            embed = discord.Embed(
                title="⚔️ AtCoder WAランキング" if i == 0 else "",
                description="\n".join(chunk),
                color=0x00BFFF,
            )
            if i == 0:
                embed.set_footer(
                    text=f"登録: {len(valid)}人更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
            embeds.append(embed)

        await interaction.followup.send(embeds=embeds)

class PointGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="point", description="得点ランキング")

    @app_commands.command(name="total", description="総合得点ランキング")
    async def total_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self._point_total(interaction)

    @app_commands.command(name="contest", description="コンテスト別得点ランキング")
    @app_commands.describe(contest_id="コンテストID（例: abc001）")
    async def contest_command(self, interaction: discord.Interaction, contest_id: str):
        await interaction.response.defer()
        await self._point_contest(interaction, contest_id)
    async def _point_total(self, interaction: discord.Interaction):
        all_users = get_all_users()
        if not all_users:
            await interaction.followup.send("誰も登録してないぞ。")
            return

        guild_member_ids = {str(m.id) for m in interaction.guild.members}
        target_users = [
            (discord_id, ac_id)
            for discord_id, ac_id in all_users
            if discord_id in guild_member_ids
        ]
        if not target_users:
            await interaction.followup.send("このサーバーに登録済みユーザーがいないぞ。")
            return

        async def fetch_async(discord_id: str, ac_id: str):
            loop = asyncio.get_event_loop()
            point = await loop.run_in_executor(None, fetch_atcoder_total_point, ac_id)
            return discord_id, ac_id, point

        results = list(await asyncio.gather(
            *[fetch_async(d_id, ac_id) for d_id, ac_id in target_users]
        ))
        results.sort(key=lambda x: x[2], reverse=True)

        lines = []
        for rank, (discord_id, ac_id, point) in enumerate(results, 1):
            member = interaction.guild.get_member(int(discord_id))
            display_name = member.display_name if member else f"<@{discord_id}>"
            medal = {1: "1st", 2: "2nd", 3: "3rd"}.get(rank, f"`{rank:2}.`")
            lines.append(
                f"{medal} **{point}pt**{display_name}"
                f"[{ac_id}](https://atcoder.jp/users/{ac_id})"
            )

        CHUNK = 25
        embeds = []
        for i in range(0, len(lines), CHUNK):
            embed = discord.Embed(
                title="🏆 AtCoder 総合得点ランキング" if i == 0 else "",
                description="\n".join(lines[i:i + CHUNK]),
                color=0x00BFFF,
            )
            if i == 0:
                embed.set_footer(
                    text=f"登録: {len(results)}人更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
            embeds.append(embed)

        await interaction.followup.send(embeds=embeds)

    async def _point_contest(self, interaction: discord.Interaction, contest_id: str):
                # コンテストが存在するか確認する
        resp = requests.get(
            f"https://atcoder.jp/contests/{contest_id}",
            timeout=10
        )
        if resp.status_code == 404:
            await interaction.followup.send(f"`{contest_id}` というコンテストは存在しないぞ。")
            return
        all_users = get_all_users()
        if not all_users:
            await interaction.followup.send("誰も登録してないぞ。")
            return

        guild_member_ids = {str(m.id) for m in interaction.guild.members}
        target_users = [
            (discord_id, ac_id)
            for discord_id, ac_id in all_users
            if discord_id in guild_member_ids
        ]
        if not target_users:
            await interaction.followup.send("このサーバーに登録済みユーザーがいないぞ。")
            return

        async def fetch_async(discord_id: str, ac_id: str):
            loop = asyncio.get_event_loop()
            # コンテストごとの得点dictを取得して指定コンテストだけ取り出す
            contest_points = await loop.run_in_executor(
                None, fetch_atcoder_contest_points, ac_id
            )
            point = contest_points.get(contest_id, 0)
            return discord_id, ac_id, point

        results = list(await asyncio.gather(
            *[fetch_async(d_id, ac_id) for d_id, ac_id in target_users]
        ))
        results.sort(key=lambda x: x[2], reverse=True)

        lines = []
        for rank, (discord_id, ac_id, point) in enumerate(results, 1):
            member = interaction.guild.get_member(int(discord_id))
            display_name = member.display_name if member else f"<@{discord_id}>"
            medal = {1: "1st", 2: "2nd", 3: "3rd"}.get(rank, f"`{rank:2}.`")
            lines.append(
                f"{medal} **{point}pt**{display_name}"
                f"[{ac_id}](https://atcoder.jp/users/{ac_id})"
            )

        CHUNK = 25
        embeds = []
        for i in range(0, len(lines), CHUNK):
            embed = discord.Embed(
                title=f"🏆 {contest_id} 得点ランキング" if i == 0 else "",
                description="\n".join(lines[i:i + CHUNK]),
                color=0x00BFFF,
            )
            if i == 0:
                embed.set_footer(
                    text=f"登録: {len(results)}人更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
            embeds.append(embed)

        await interaction.followup.send(embeds=embeds)


# ===========================
# Cog本体
# ===========================
class RankCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rank_group = RankGroup()
        bot.tree.add_command(self.rank_group)
        init_db()

# ===========================
# メインから呼ぶやつ
# ===========================
async def setup(bot: commands.Bot):
    await bot.add_cog(RankCog(bot))