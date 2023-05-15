import json
from time import time
from re import findall
from typing import Dict, List, Union
from datetime import datetime, timezone, timedelta

from httpx import AsyncClient

from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment

TZ = timezone(timedelta(hours=8))


async def getData(type, data: Dict = {}) -> Dict:
    """米哈游接口请求"""

    url = {
        "actId": "https://bbs-api.mihoyo.com/painter/api/user_instant/list?offset=0&size=20&uid=75276550",
        "index": "https://api-takumi.mihoyo.com/event/miyolive/index",
        "code": "https://api-takumi-static.mihoyo.com/event/miyolive/refreshCode",
    }
    async with AsyncClient() as client:
        try:
            if type == "index":
                res = await client.get(
                    url[type], headers={"x-rpc-act_id": data.get("actId", "")}
                )
            elif type == "code":
                res = await client.get(
                    url[type],
                    params={
                        "version": data.get("version", ""),
                        "time": f"{int(time())}",
                    },
                    headers={"x-rpc-act_id": data.get("actId", "")},
                )
            else:
                res = await client.get(url[type])
            return res.json()
        except Exception as e:
            logger.opt(exception=e).error(f"{type} 接口请求错误")
            return {"error": f"[{e.__class__.__name__}] {type} 接口请求错误"}


async def getActId() -> str:
    """获取 ``act_id``"""

    ret = await getData("actId")
    if ret.get("error") or ret.get("retcode") != 0:
        return ""

    actId = ""
    keywords = ["来看《原神》", "版本前瞻特别节目"]
    for p in ret["data"]["list"]:
        post = p.get("post", {}).get("post", {})
        if not post:
            continue
        if not all(word in post["subject"] for word in keywords):
            continue
        shit = json.loads(post["structured_content"])
        for segment in shit:
            link = segment.get("attributes", {}).get("link", "")
            if "观看直播" in segment.get("insert", "") and link:
                matched = findall(r"act_id=(.*?)\&", link)
                if matched:
                    actId = matched[0]
        if actId:
            break

    return actId


async def getLiveData(actId: str) -> Dict:
    """获取直播数据，尤其是 ``code_ver``"""

    ret = await getData("index", {"actId": actId})
    if ret.get("error") or ret.get("retcode") != 0:
        return {"error": ret.get("error") or "前瞻直播数据异常"}

    liveDataRaw = ret["data"]["live"]
    liveTemplate = json.loads(ret["data"]["template"])
    liveData = {
        "code_ver": liveDataRaw["code_ver"],
        "title": liveDataRaw["title"].replace("特别节目", ""),
        "header": liveTemplate["kvDesktop"],
        "room": liveTemplate["liveConfig"][0]["desktop"],
    }
    if liveDataRaw["is_end"]:
        liveData["review"] = liveTemplate["reviewUrl"]["args"]["post_id"]
    else:
        now = datetime.fromtimestamp(time(), TZ)
        start = datetime.strptime(liveDataRaw["start"], "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=TZ
        )
        if now < start:
            liveData["start"] = liveDataRaw["start"]

    return liveData


async def getCodes(version: str, actId: str) -> Union[Dict, List[Dict]]:
    """获取兑换码"""

    ret = await getData("code", {"version": version, "actId": actId})
    if ret.get("error") or ret.get("retcode") != 0:
        return {"error": ret.get("error") or "兑换码数据异常"}

    codesData = []
    for codeInfo in ret["data"]["code_list"]:
        gifts = findall(
            r">\s*([\u4e00-\u9fa5]+|\*[0-9]+)\s*\*<",
            codeInfo["title"].replace("&nbsp;", " "),
        )
        codesData.append(
            {
                "items": "+".join(g for g in gifts if not g[-1].isdigit()),
                "code": codeInfo["code"],
            }
        )

    return codesData


async def getMsg() -> List[MessageSegment]:
    """生成最新前瞻直播兑换码合并转发消息"""

    actId = await getActId()
    if not actId:
        return [
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname="原神前瞻直播",
                content=Message(MessageSegment.text("暂无前瞻直播资讯！")),
            )
        ]

    liveData = await getLiveData(actId)
    if liveData.get("error"):
        return [
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname="原神前瞻直播",
                content=Message(MessageSegment.text(liveData["error"])),
            )
        ]
    elif liveData.get("start"):
        return [
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname=liveData["title"],
                content=Message(MessageSegment.image(liveData["header"])),
            ),
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname=liveData["title"],
                content=Message(MessageSegment.text(liveData["room"])),
            ),
        ]

    codesData = await getCodes(liveData["code_ver"], actId)
    if isinstance(codesData, Dict):
        return [
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname=liveData["title"],
                content=Message(MessageSegment.text(codesData["error"])),
            )
        ]
    codesMsg = [
        MessageSegment.node_custom(
            user_id=2854196320,
            nickname=liveData["title"],
            content=Message(
                MessageSegment.text(
                    f"当前发布了 {len(codesData)} 个兑换码，请在有效期内及时兑换哦~"
                    + "\n\n* 官方接口数据有 2 分钟左右延迟，请耐心等待下~"
                )
            ),
        ),
        *[
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname=code["items"] or liveData["title"],
                content=Message(MessageSegment.text(code["code"])),
            )
            for code in codesData
        ],
    ]
    if liveData.get("review"):
        codesMsg.append(
            MessageSegment.node_custom(
                user_id=2854196320,
                nickname=liveData["title"],
                content=Message(
                    MessageSegment.text(
                        "直播已经结束，查看回放：\n\n"
                        + f"https://www.miyoushe.com/ys/article/{liveData['review']}"
                    )
                ),
            )
        )
    return codesMsg
