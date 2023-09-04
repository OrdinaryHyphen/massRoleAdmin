# インストールした discord.py を読み込む
import json
import os
import discord
from discord.ext import tasks
from datetime import datetime
import time
import pytz

# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.environ['DISCORD_TOKEN']

# 接続に必要なオブジェクトを生成
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# ぷらなろサーバーのオブジェクトを取得
GUILD_ID = 957833149289742346

# 新規参加者用のチャンネルをIDから取得
CHANNEL_FRESHMAN_ID = 959807916918050856

# 新規参加者のロールをIDから取得
ROLE_FRESHMAN_ID = 1148186727584911390

# ようこそ！！のロールをIDから取得
ROLE_WELCOME_ID = 1148260144862478376

# 初等部のロールをIDから取得
ROLE_BEGINNER_STUDENT_ID = 1148134929906016267

# 中等部のロールをIDから取得
ROLE_ADVANCED_STUDENT_ID = 1148186444091887636

# 高等部のロールをIDから取得
ROLE_EXPERT_STUDENT_ID = 1148186616289054721

# ロール付与候補のユーザーのIDリスト
with open('json/welcome.json') as f:
    welcome_dict = json.load(f)

with open('json/beginner.json') as f:
    beginner_students = json.load(f)

with open('json/advanced.json') as f:
    advanced_students = json.load(f)

with open('json/expert.json') as f:
    expert_students = json.load(f)


@client.event
async def on_ready():
	print('on_ready')
	elapse_time.start()


@tasks.loop(seconds=60)
async def elapse_time():
	now = datetime.now(pytz.timezone('Asia/Tokyo'))
	if now.hour == 0 and now.minute == 0:
		for user_id in welcome_dict:
			welcome_dict[user_id] -= 1
			if welcome_dict[user_id] <= 0:
				welcome_dict.pop(user_id)
				guild = client.get_guild(GUILD_ID)
				freshman_role = guild.get_role(ROLE_FRESHMAN_ID)
				guild.get_member(user_id).remove_roles(freshman_role)
		
		with open('json/welcome.json', 'w') as f:
			json.dump(welcome_dict, f, indent=2)


# メンバー参加時に動作する処理
@client.event
async def on_member_join(member):
# サーバー参加者がBotだった場合は無視する
	if member.bot:
		return

	freshman_channel = client.get_channel(CHANNEL_FRESHMAN_ID)
	await freshman_channel.send('A、B、C、選ぶのだ')


# ＠新規参加者ロールが外れた場合、追加でようこそロールと学園ロールを付与する
@client.event
async def on_member_update(before, after):
	# 用意した役職IDから Role オブジェクトを取得
	guild = client.get_guild(GUILD_ID)
	freshman_role = guild.get_role(ROLE_FRESHMAN_ID)
	welcome_role = guild.get_role(ROLE_WELCOME_ID)
	beginner_students_role = guild.get_role(ROLE_BEGINNER_STUDENT_ID)
	advanced_students_role = guild.get_role(ROLE_ADVANCED_STUDENT_ID)
	expert_students_role = guild.get_role(ROLE_ADVANCED_STUDENT_ID)

	if freshman_role in before.roles and freshman_role not in after.roles:
		await after.add_roles(welcome_role)
		welcome_dict[after.id] = 66
		with open('json/welcome.json', 'w') as f:
			json.dump(welcome_dict, f, indent=2)

	if after.id in beginner_students:
		await after.add_roles(beginner_students_role)
	if after.id in advanced_students:
		await after.add_roles(advanced_students_role)
	if after.id in expert_students:
		await after.add_roles(expert_students_role)


# あるメッセージにリアクションがついた場合、リアクションごとに異なる状態を付与する
@client.event
async def on_reaction_add(reaction, user):
	print('reaction')
	print(reaction.emoji)

	# 新規参加者用チャンネル以外はスルー
	freshman_channel = client.get_channel(CHANNEL_FRESHMAN_ID)
	if reaction.message.channel != freshman_channel:
		return

	# user_id（リアクションしたユーザーのid）を初等部・中等部・高等部リストに入れる
	if reaction.emoji == '🇦':
		beginner_students[user.id] = 0
		with open('json/beginner.json', 'w') as f:
			json.dump(beginner_students, f, indent=2)
	if reaction.emoji == '🇧':
		advanced_students[user.id] = 0
		with open('json/advanced.json', 'w') as f:
			json.dump(advanced_students, f, indent=2)
	if reaction.emoji == '🇨':
		expert_students[user.id] = 0
		with open('json/expert.json', 'w') as f:
			json.dump(expert_students, f, indent=2)

	print(beginner_students)
	print(advanced_students)
	print(expert_students)

	# 分かりやすいように歓迎のメッセージを送る
	await reaction.message.channel.send('リアクションを確認しました！\nご回答ありがとうございます！')


# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
