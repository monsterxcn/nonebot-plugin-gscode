from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot
from nonebot.plugin import PluginMetadata, on_command
from nonebot.adapters.onebot.v11.event import MessageEvent, GroupMessageEvent

from .data_source import getMsg

__plugin_meta__ = PluginMetadata(
    name="GsCode",
    description="查询原神前瞻直播兑换码",
    usage="""查询原神前瞻直播兑换码
注意：经测试，兑换码接口返回与前瞻直播有 2 分钟左右延迟，应为正常现象，请耐心等待。
/gscode
/兑换码""",
)

codeMatcher = on_command("gscode", aliases={"兑换码"}, priority=5)


@codeMatcher.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    if str(state["_prefix"]["command_arg"]):
        await codeMatcher.finish()
    codes = await getMsg()
    if isinstance(event, GroupMessageEvent):
        await bot.send_group_forward_msg(group_id=event.group_id, messages=codes)
    else:
        await bot.send_private_forward_msg(user_id=event.user_id, messages=codes)
