import sqlite3
import asyncio
import requests
from datetime import datetime, timezone, timedelta

import discord
from discord.ext import commands
from discord import app_commands
from . import user

JST = timezone(timedelta(hours=9))

# ===========================
# API判定ロジック
# ===========================
def check_today_ac(atcoder_id: str) -> bool:
    """今日の0:00(JST)以降の提出を取得し、ACがあるか判定する"""
    base_url = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions"
    now = datetime.now(JST)
    
    # 今日の0:00のタイムスタンプを計算
    start_of_today = datetime(now.year, now.month, now.day, tzinfo=JST)
    from_second = int(start_of_today.timestamp())

    try:
        resp = requests.get(
            base_url,
            params={"user": atcoder_id, "from_second": from_second},
            timeout=10
        )
        if resp.status_code != 200:
            return False
            
        data = resp.json()
        for sub in data:
            if sub.get("result") == "AC":
                return True
        return False
    except Exception as e:
        print(f"APIエラー: {e}")
        return False


# ===========================
# Streak管理 Cog
# ===========================
class StreakCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("streaks.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS streaks (
            user_id INTEGER PRIMARY KEY,
            streak INTEGER NOT NULL,
            last_solved TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def process_streak(self, user_id: int, atcoder_id: str):
        """APIを確認し、現在のstreak情報を計算・更新して返す"""
        today = datetime.now(JST).date()

        self.cursor.execute(
            "SELECT streak, last_solved FROM streaks WHERE user_id = ?",
            (user_id,)
        )
        result = self.cursor.fetchone()

        # 今日のAC状況をAPIで確認
        has_ac_today = check_today_ac(atcoder_id)

        # 初回記録
        if result is None:
            if has_ac_today:
                streak = 1
                self.cursor.execute(
                    "INSERT INTO streaks VALUES (?, ?, ?)",
                    (user_id, streak, str(today))
                )
                self.conn.commit()
                return streak, True, str(today)
            else:
                return 0, False, "記録なし"

        streak, last_solved_str = result
        last_solved = datetime.strptime(last_solved_str, "%Y-%m-%d").date()
        difference = (today - last_solved).days

        # 既にDB上で今日解決済みとなっている場合
        if difference == 0:
            return streak, True, last_solved_str

        # 今日のACが確認できた場合、DBを更新
        if has_ac_today:
            if difference == 1:
                streak += 1
            else:
                streak = 1
                
            self.cursor.execute("""
                UPDATE streaks
                SET streak = ?, last_solved = ?
                WHERE user_id = ?
            """, (streak, str(today), user_id))
            self.conn.commit()
            return streak, True, str(today)
            
        # 今日まだACしていない場合
        else:
            if difference > 1:
                streak = 0 # 昨日解いていないのでストリークは0として扱う
            return streak, False, last_solved_str

    @app_commands.command(name="streak", description="現在の連続学習記録（自動判定）を表示します")
    async def streak(self, interaction: discord.Interaction):
        discord_id = str(interaction.user.id)
        
        # ユーザー登録の確認 (※get_atcoder_idは既存の関数を呼び出します)
        atcoder_id = user.get_atcoder_id(discord_id)
        if not atcoder_id:
            await interaction.response.send_message(
                "先に `/user register` でAtCoder IDを登録してくれ。", 
                ephemeral=True
            )
            return

        # API通信で時間がかかるため、インタラクションを待機状態にする
        await interaction.response.defer()

        loop = asyncio.get_event_loop()
        # API通信を含む処理を非同期で実行し、ブロックを防ぐ
        streak, is_solved_today, last_solved = await loop.run_in_executor(
            None, self.process_streak, interaction.user.id, atcoder_id
        )

        if streak >= 30:
            icon = "👑"
        elif streak >= 7:
            icon = "🔥🔥"
        elif streak > 0:
            icon = "🔥"
        else:
            icon = "💤"

        embed = discord.Embed(
            title=f"{icon} {interaction.user.display_name}'s Streak",
            color=discord.Color.green() if is_solved_today else discord.Color.orange()
        )

        embed.add_field(name="連続記録", value=f"**{streak}** 日", inline=False)
        embed.add_field(name="最終学習日", value=str(last_solved), inline=False)

        if is_solved_today:
            embed.set_footer(text="今日はすでにAC済みだ！素晴らしい！")
        else:
            embed.set_footer(text="今日はまだACしていないようだ。頑張ろう！")

        # defer() を使用したため、followup.send で送信
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StreakCog(bot))
