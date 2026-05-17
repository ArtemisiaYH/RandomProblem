# RandomProblem
random atcoder problem
# My Discord Bot

## 機能
- /problem関数はselectとrandomの二つの引数がある。selectはproblem_idの引数でabc999_aなどを打つとそのurlが表示される。またすでに解いた問題は、ACとWAの回数が表示される。randomはcontest,index,exclude_acの引数でそれぞれ、コンテスト、インデックス、すでに解いた問題を含むかが選べる.
- /user関数はregister,problem,ac,waの四つの引数があり、registerは最初の一回もしくは変更したいときに自分のAtCoderのidを打つとdiscordとAtCoderのアカウントが紐づく.peoblem,acはそれぞれ解いた問題の全問題、acを取った全問題が表示され、waはall,xacの二つの引数があり、それぞれwaを取った問題、waを取りのちにacを取った問題が表示される.

## セットアップ
1. `.env` に `DISCORD_TOKEN=トークン` を記入
2. `pip install -r requirements.txt`
3. `python rp.py` で起動