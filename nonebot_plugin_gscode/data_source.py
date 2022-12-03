from re import findall
from time import time, strftime, localtime
from traceback import format_exc
from typing import Dict, List

from httpx import AsyncClient
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger


async def getData(type, data: Dict = {}) -> Dict:
    """米哈游接口请求"""

    url = {
        "index": f"https://api-takumi.mihoyo.com/event/bbslive/index?act_id={data.get('actId', '')}",
        "mi18n": f"https://webstatic.mihoyo.com/admin/mi18n/bbs_cn/{data.get('mi18n', '')}/{data.get('mi18n', '')}-zh-cn.json",
        "code": f"https://webstatic.mihoyo.com/bbslive/code/{data.get('actId', '')}.json?version=1&time={int(time())}",
        "actId": "https://bbs-api.mihoyo.com/post/wapi/getPostFullInCollection?collection_id=1280130&gids=2&order_type=2",
    }
    async with AsyncClient() as client:
        try:
            res = await client.get(url[type])
            return res.json()
        except Exception as e:
            logger.error(f"{type} 接口错误 {e.__class__.__name__}\n{format_exc()}")
            return {"error": f"{type} 接口错误 {e.__class__.__name__}"}


async def getActId() -> str:
    """获取 ``act_id``"""

    ret = await getData("actId")
    if ret.get("error") or ret.get("retcode") != 0:
        return ""
    posts = sorted(
        ret.get("data", {}).get("posts", []),
        key=lambda p: p["post"]["created_at"],
        reverse=True,
    )
    return posts[0]["post"]["content"].replace("[链接]", "") if posts else ""


async def getCodes() -> List[MessageSegment]:
    """生成最新前瞻直播兑换码合并转发消息"""

    actId = await getActId()
    if not actId:
        return [
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname="原神前瞻直播",
                content=Message(MessageSegment.text("没有找到 actId！")),
            )
        ]

    indexRes = await getData("index", {"actId": actId})
    if not indexRes.get("data") or not indexRes["data"].get("mi18n", ""):
        return [
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname="原神前瞻直播",
                content=Message(
                    MessageSegment.text(indexRes.get("message") or "没有找到 mi18n！")
                ),
            )
        ]
    mi18n = indexRes["data"].get("mi18n", "")

    mi18nRes = await getData("mi18n", {"mi18n": mi18n})
    codeRes = await getData("code", {"actId": actId})
    nickname = mi18nRes.get("act-title", "").replace("特别节目", "") or "原神前瞻直播"
    if indexRes["data"].get("remain", 0) or not len(codeRes):
        return [
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname=nickname,
                content=Message(MessageSegment.image(mi18nRes["pc-kv"])),
            ),
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname=nickname,
                content=Message(
                    MessageSegment.text(
                        f"预计第一个兑换码发放时间为 "
                        f"{strftime('%H:%M:%S', localtime(int(mi18nRes['time1'])))}"
                        "\n\n* 官方接口数据有 2 分钟左右延迟，请耐心等待下~"
                    )
                ),
            ),
        ]

    nextCode = (
        ""
        if len(codeRes) == 3
        else (
            "，下一个兑换码发放时间为 "
            + strftime("%H:%M:%S", localtime(int(mi18nRes[f"time{len(codeRes) + 1}"])))
        )
    )
    codes = [
        MessageSegment.node_custom(
            user_id=2854196320,
            nickname=nickname,
            content=Message(
                MessageSegment.text(
                    f"当前发放了 {len(codeRes)} 个兑换码{nextCode}\n{mi18nRes['exchange-tips']}"
                )
            ),
        )
    ]
    for codeInfo in codeRes:
        gifts = findall(
            r">\s*([\u4e00-\u9fa5]+|\*[0-9]+)\s*<",
            codeInfo["title"].replace("&nbsp;", " "),
        )
        codes.append(
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname="+".join(g for g in gifts if not g[-1].isdigit()) or nickname,
                content=Message(MessageSegment.text(codeInfo["code"])),
            )
        )

    return codes
