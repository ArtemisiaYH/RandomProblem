import random
import aiohttp
import json
from discord.ext import commands

class PorblemCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    PROBLEMS_API = "https://kenkoooo.com/atcoder/resources/problems.json"

    with open("aa.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    aa_list = data["aa"]
    #全体
    @commands.command()
    async def all(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json() #サイトへのアクセスを一回で済ませる
        problem = random.choice(problems)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def abc(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        abc = [p for p in problems if p["contest_id"].startswith("abc")]
        problem = random.choice(abc)
        contest_id = problem["contest_id"]   
        problem_id = problem["id"]       
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def arc(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        arc = [p for p in problems if p["contest_id"].startswith("arc")]
        problem = random.choice(arc)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]       
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def agc(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        agc = [p for p in problems if p["contest_id"].startswith("agc")]
        problem = random.choice(agc)
        contest_id = problem["contest_id"]
        problem_id = problem["id"]          
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    #abcのa問題とか個別
    @commands.command()
    async def abc_a(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        abca = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "A"]
        pre = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "1"]
        abca.extend(pre)
        problem = random.choice(abca)
        contest_id = problem["contest_id"] 
        problem_id = problem["id"]         
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def abc_b(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        abcb = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "B"]
        pre = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "2"]
        abcb.extend(pre)
        problem = random.choice(abcb)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]      
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def abc_c(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        abcc = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "C"]
        pre = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "3"]
        abcc.extend(pre)
        problem = random.choice(abcc)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]          
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def abc_d(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        abcd = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "D"]
        pre = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "4"]
        abcd.extend(pre)
        problem = random.choice(abcd)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]         
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def abc_e(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        abce = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "E"]
        problem = random.choice(abce)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]         
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def abc_f(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        abcf = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "F"]
        problem = random.choice(abcf)
        contest_id = problem["contest_id"] 
        problem_id = problem["id"]       
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def abc_g(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        abcg = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "G"]
        problem = random.choice(abcg)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]         
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def abc_h(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        abch = [p for p in problems if p["contest_id"].startswith("abc") and p["problem_index"] == "H"]
        problem = random.choice(abch)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]         
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    #arcのa問題とか個別
    @commands.command()
    async def arc_a(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        arca = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "A"]
        pre = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "1"]
        arca.extend(pre)
        problem = random.choice(arca)
        contest_id = problem["contest_id"]   
        problem_id = problem["id"]  
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def arc_b(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        arcb = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "B"]
        pre = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "2"]
        arcb.extend(pre)
        problem = random.choice(arcb)
        contest_id = problem["contest_id"]   
        problem_id = problem["id"]           
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def arc_c(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        arcc = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "C"]
        pre = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "3"]
        arcc.extend(pre)
        problem = random.choice(arcc)
        contest_id = problem["contest_id"] 
        problem_id = problem["id"]       
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def arc_d(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        arcd = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "D"]
        pre = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "4"]
        arcd.extend(pre)
        problem = random.choice(arcd)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]       
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def arc_e(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        arce = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "E"]
        problem = random.choice(arce)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]        
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def arc_f(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        arcf = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "F"]
        problem = random.choice(arcf)
        contest_id = problem["contest_id"]   
        problem_id = problem["id"]          
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def arc_f2(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        arcf2 = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "F2"]
        problem = random.choice(arcf2)
        contest_id = problem["contest_id"]   
        problem_id = problem["id"]           
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def arc_g(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        arcg = [p for p in problems if p["contest_id"].startswith("arc") and p["problem_index"] == "G"]
        problem = random.choice(arcg)
        contest_id = problem["contest_id"]   
        problem_id = problem["id"]           
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    #agcのa問題とか個別
    @commands.command()
    async def agc_a(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        agca = [p for p in problems if p["contest_id"].startswith("agc") and p["problem_index"] == "A"]
        problem = random.choice(agca)
        contest_id = problem["contest_id"]   
        problem_id = problem["id"]  
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def agc_b(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        agcb = [p for p in problems if p["contest_id"].startswith("agc") and p["problem_index"] == "B"]
        problem = random.choice(agcb)
        contest_id = problem["contest_id"]   
        problem_id = problem["id"]           
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def agc_c(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        agcc = [p for p in problems if p["contest_id"].startswith("agc") and p["problem_index"] == "C"]
        problem = random.choice(agcc)
        contest_id = problem["contest_id"] 
        problem_id = problem["id"]       
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def agc_d(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        agcd = [p for p in problems if p["contest_id"].startswith("agc") and p["problem_index"] == "D"]
        problem = random.choice(agcd)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]       
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def agc_e(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        agce = [p for p in problems if p["contest_id"].startswith("agc") and p["problem_index"] == "E"]
        problem = random.choice(agce)
        contest_id = problem["contest_id"]  
        problem_id = problem["id"]        
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def agc_f(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        agcf = [p for p in problems if p["contest_id"].startswith("agc") and p["problem_index"] == "F"]
        problem = random.choice(agcf)
        contest_id = problem["contest_id"]   
        problem_id = problem["id"]          
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

    @commands.command()
    async def agc_f2(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.PROBLEMS_API) as resp:
                problems = await resp.json()
        agcf2 = [p for p in problems if p["contest_id"].startswith("agc") and p["problem_index"] == "F2"]
        problem = random.choice(agcf2)
        contest_id = problem["contest_id"]   
        problem_id = problem["id"]           
        url = f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}"
        await ctx.send(f"解けるかな {random.choice(self.aa_list)}: **{problem['title']}**\n{url}")

async def setup(bot):
    await bot.add_cog(PorblemCog(bot))