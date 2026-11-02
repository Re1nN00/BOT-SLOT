import os
import json
import random
import discord
from discord.ext import commands

# Konfigurasi Bot Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# File database lokal untuk menyimpan saldo (json)
DB_FILE = "economy_data.json"

def load_data():
    """Memuat data ekonomi pemain dari file JSON."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(data):
    """Menyimpan data ekonomi pemain ke file JSON."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Simbol Slot Machine
SLOT_SYMBOLS = ["🍒", "🍋", "🔔", "💎", "⭐", "7️⃣"]

@bot.event
async def on_ready():
    print(f"=========================================================")
    print(f"   PROJECT X-PRIME V4 — 24/7 CASINO & ECONOMY (MORGAN)   ")
    print(f"=========================================================")
    print(f" [✓] Logged in as: {bot.user.name}")
    print(f" [✓] Status      : Online & Ready (24/7 Hosting)")
    print(f"=========================================================\n")
    await bot.change_presence(activity=discord.Game(name="!slot | !daily | !balance"))

def get_user_account(data, user_id):
    """Memastikan akun pengguna terdaftar dengan saldo awal."""
    user_id_str = str(user_id)
    if user_id_str not in data:
        data[user_id_str] = {
            "balance": 500,     # Modal awal gratis
            "last_daily": 0     # Timestamp klaim harian terakhir
        }
    return data[user_id_str]

@bot.command(name="balance", aliases=["bal", "cash"], help="Melihat saldo cash kamu.")
async def balance(ctx):
    data = load_data()
    user = get_user_account(data, ctx.author.id)
    
    embed = discord.Embed(
        title="💰 DOMPET KASINO PELER & MORGAN",
        description=f"Pemilik Sesi: **MORGAN**\nPemilik Akun: {ctx.author.mention}",
        color=0xFFD700
    )
    embed.add_field(name="Total Cash", value=f"🪙 **${user['balance']:,}**", inline=False)
    embed.set_footer(text="Gunakan !daily untuk klaim bonus harian!")
    await ctx.send(embed=embed)

@bot.command(name="daily", help="Klaim bonus cash harian (tiap 24 jam).")
async def daily(ctx):
    data = load_data()
    user_id_str = str(ctx.author.id)
    user = get_user_account(data, ctx.author.id)
    
    current_time = time.time()
    cooldown_time = 86400  # 24 jam dalam detik
    last_claim = user.get("last_daily", 0)
    
    if current_time - last_claim < cooldown_time:
        remaining_time = int(cooldown_time - (current_time - last_claim))
        hrs = remaining_time // 3600
        mins = (remaining_time % 3600) // 60
        await ctx.send(f"⏳ {ctx.author.mention}, kamu sudah mengambil klaim harian! Silakan tunggu **{hrs} jam {mins} menit** lagi.")
        return
    
    # Berikan bonus harian sebesar $1,000
    bonus = 1000
    user["balance"] += bonus
    user["last_daily"] = current_time
    save_data(data)
    
    embed = discord.Embed(
        title="🎁 KLAIM HARIAN BERHASIL!",
        description=f"Selamat {ctx.author.mention}, kamu mendapatkan **${bonus:,}** gratis hari ini!",
        color=0x00FF00
    )
    embed.add_field(name="Saldo Baru", value=f"🪙 **${user['balance']:,}**", inline=False)
    embed.set_footer(text="Project X-Prime V4 • Daily Reward Active")
    await ctx.send(embed=embed)

@bot.command(name="slot", help="Bermain mesin slot mempertaruhkan cash.")
async def slot(ctx, amount: int = 50):
    data = load_data()
    user = get_user_account(data, ctx.author.id)
    
    if amount <= 0:
        await ctx.send(f"⚠️ {ctx.author.mention}, jumlah taruhan harus lebih dari 0!")
        return
        
    if user["balance"] < amount:
        await ctx.send(f"❌ {ctx.author.mention}, saldo cash kamu tidak cukup! Sisa saldo kamu: **${user['balance']:,}**. Ketik `!daily` untuk ambil modal.")
        return
        
    # Kurangi saldo untuk taruhan
    user["balance"] -= amount
    
    # Mengacak 3 simbol slot
    result = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    
    # Menentukan hasil kemenangan & multiplier
    if result[0] == result[1] == result[2]:
        payout = amount * 10  # Jackpot 10x lipat
        user["balance"] += payout
        status_text = f"🎉 JACKPOT BESAR! Kamu menang **${payout:,}**!"
        color_embed = 0xFFD700
    elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
        payout = amount * 2   # Menang 2 simbol (2x lipat)
        user["balance"] += payout
        status_text = f"✨ Lumayan! Mendapat 2 simbol sama, menang **${payout:,}**!"
        color_embed = 0x00FFFF
    else:
        status_text = f"❌ Kalah! Kehilangan taruhan sebesar **${amount:,}**."
        color_embed = 0xFF3333

    save_data(data)

    # Tampilan Embed Kasino
    embed = discord.Embed(
        title="🎰 PELER & MORGAN CASINO — SLOT MACHINE",
        description=f"Pemilik Sesi: **MORGAN**\nPlayer: {ctx.author.mention}",
        color=color_embed
    )
    embed.add_field(name="Mesin Putar", value=f"| {result[0]} | {result[1]} | {result[2]} |", inline=False)
    embed.add_field(name="Hasil", value=status_text, inline=False)
    embed.add_field(name="Sisa Saldo Cash", value=f"🪙 **${user['balance']:,}**", inline=False)
    embed.set_footer(text="Project X-Prime V4 • 24/7 Hosting Active")

    await ctx.send(embed=embed)

@bot.command(name="leaderboard", aliases=["lb", "rich"], help="Menampilkan papan peringkat cash terkaya.")
async def leaderboard(ctx):
    data = load_data()
    if not data:
        await ctx.send("📊 Belum ada data pemain di papan peringkat.")
        return
        
    # Urutkan berdasarkan saldo terbanyak
    sorted_users = sorted(data.items(), key=lambda x: x[1]["balance"], reverse=True)
    
    embed = discord.Embed(
        title="🏆 CASH LEADERBOARD — KASINO MORGAN",
        description="Daftar pemain terkaya di server ini:",
        color=0xFFD700
    )
    
    rank_emojis = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (uid, info) in enumerate(sorted_users[:10]):
        member = ctx.guild.get_member(int(uid))
        name = member.name if member else f"User ID: {uid}"
        emoji = rank_emojis[idx] if idx < len(rank_emojis) else "🔸"
        embed.add_field(
            name=f"{emoji} Peringkat #{idx + 1}",
            value=f"👤 **{name}** ➔ 🪙 **${info['balance']:,}**",
            inline=False
        )
        
    embed.set_footer(text="Project X-Prime V4 • Global Economy Rank")
    await ctx.send(embed=embed)

# Token Bot dari Environment Variable (Hosting 24/7)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("[!] ERROR: Token Bot Discord belum disetel di Environment Variables!")
else:
    bot.run(TOKEN)