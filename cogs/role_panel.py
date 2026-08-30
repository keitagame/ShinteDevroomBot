from __future__ import annotations

import logging

import discord
from discord.ext import commands

logger = logging.getLogger("bot.role_panel")

# ------------------------------------------------------------
# 選択可能なロール一覧（ここに追加・削除するだけで反映されます）
# label       : メニューに表示される名前
# role_id     : 付与/剥奪するロールのID
# description : メニュー上の説明（省略可）
# emoji       : メニュー上の絵文字（省略可）
#
# ※ Discordの仕様上、1つのメニューに設定できる選択肢は最大25個までです
# ------------------------------------------------------------
ROLE_OPTIONS = [
    {
        "role_id": 1511613354987225208,
        "label": "VC募集ロール",
        "description": "",
    },
    {
        "role_id": 1466356591451308074,
        "label": "宣伝文チャンネル表示",
        "description": "",
    },
    {
        "role_id": 1466348564585255101,
        "label": "Bumpチャンネル表示",
        "description": "",
    },
]

PANEL_DESCRIPTION = (
    "欲しいロールを下のメニューから選択してください。\n"
    "選択するとロールが付与され、選択を外すと剥奪されます。"
)

SELECT_CUSTOM_ID = "role_panel:select"


# ------------------------------------------------------------
# ロール選択メニュー
# ------------------------------------------------------------
class RolePanelSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=opt["label"],
                value=str(opt["role_id"]),
                description=opt.get("description") or None,
                emoji=opt.get("emoji") or None,
            )
            for opt in ROLE_OPTIONS
        ]
        super().__init__(
            placeholder="欲しいロールを選択...",
            min_values=0,
            max_values=len(options),
            options=options,
            custom_id=SELECT_CUSTOM_ID,
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild

        selected_ids = {int(v) for v in self.values}
        panel_role_ids = {opt["role_id"] for opt in ROLE_OPTIONS}
        current_ids = {r.id for r in member.roles}

        to_add_ids = selected_ids - current_ids
        to_remove_ids = (panel_role_ids - selected_ids) & current_ids

        to_add = [guild.get_role(rid) for rid in to_add_ids if guild.get_role(rid)]
        to_remove = [guild.get_role(rid) for rid in to_remove_ids if guild.get_role(rid)]

        try:
            if to_add:
                await member.add_roles(*to_add, reason="ロールパネル選択")
            if to_remove:
                await member.remove_roles(*to_remove, reason="ロールパネル選択解除")
        except discord.Forbidden:
            await interaction.response.send_message(
                "ロールを付与/削除する権限がありません。Botのロール順位を確認してください。",
                ephemeral=True,
            )
            return
        except discord.HTTPException:
            logger.exception("ロールの付与/削除に失敗しました")
            await interaction.response.send_message(
                "エラーが発生しました。もう一度お試しください。", ephemeral=True
            )
            return

        await interaction.response.edit_message(view=self.view)


# ------------------------------------------------------------
# パネルの View（永続化のため custom_id を固定・timeout=None）
# ------------------------------------------------------------
class RolePanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RolePanelSelect())


# ------------------------------------------------------------
# Cog 本体
# ------------------------------------------------------------
class RolePanel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # 再起動後もメニューを操作できるように View を永続登録
        self.bot.add_view(RolePanelView())

    @commands.command(name="grolepannel")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def grolepannel(self, ctx: commands.Context):
        """ロール選択パネルをこのチャンネルに設置する"""
        await ctx.send(PANEL_DESCRIPTION, view=RolePanelView())

    @grolepannel.error
    async def grolepannel_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("このコマンドを実行するには「サーバー管理」権限が必要です。")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("このコマンドはサーバー内でのみ使用できます。")
        else:
            raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(RolePanel(bot))