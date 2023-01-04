<h1 align="center">NoneBot Plugin GsCode</h1></br>


<p align="center">🤖 用于查询原神前瞻直播兑换码的 NoneBot2 插件</p></br>


<p align="center">
  <a href="https://github.com/monsterxcn/nonebot-plugin-gscode/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/monsterxcn/nonebot-plugin-gscode/publish.yml?branch=main&style=flat-square" alt="actions">
  </a>
  <a href="https://raw.githubusercontent.com/monsterxcn/nonebot-plugin-gscode/master/LICENSE">
    <img src="https://img.shields.io/github/license/monsterxcn/nonebot-plugin-gscode?style=flat-square" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-gscode">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-gscode?style=flat-square" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=flat-square" alt="python"><br />
</p></br>


| ![image](https://user-images.githubusercontent.com/22407052/204017447-84f300f4-0df2-44df-ac3e-4bc72a47d816.png) | ![image](https://user-images.githubusercontent.com/22407052/204016397-2c2063cb-9e0d-4060-808d-32b2bb84bc69.png) |
|:--:|:--:|


## 安装方法


如果你正在使用 2.0.0.beta1 以上版本 NoneBot，推荐使用以下命令安装：


```bash
# 从 nb_cli 安装
python -m nb_cli plugin install nonebot-plugin-gscode

# 或从 PyPI 安装
python -m pip install nonebot-plugin-gscode
```


## 使用说明


插件响应 `gscode` / `兑换码` 开头的消息，返回一组包含兑换码信息的合并转发消息。


经测试，兑换码接口返回与前瞻直播有 2 分钟左右延迟，应为正常现象，请耐心等待。


插件依赖 [@Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 的合并转发接口，如需启用私聊响应请务必安装 [v1.0.0-rc2](https://github.com/Mrs4s/go-cqhttp/releases/tag/v1.0.0-rc2) 以上版本的 go-cqhttp。


## 特别鸣谢


[@nonebot/nonebot2](https://github.com/nonebot/nonebot2/) | [@Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp) | [@Le-niao/Yunzai-Bot](https://github.com/Le-niao/Yunzai-Bot)
