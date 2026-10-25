# NapCat + AstrBot QQ 机器人

Windows 本地部署脚本及四个自写 AstrBot 插件，保存已使用的日语角色聊天方案：先生成日语原句，显示中文译文，再由本地 GPT-SoVITS 直接朗读原句。聊天记忆保留日语，13 类语气按原句识别；当前以统一温柔参考和舒缓节奏配音，优先保持人格。

源码整理自已运行的本地项目。已测试的组件版本为 AstrBot 4.29.1、NapCat 4.18.41、双语插件 1.3.0；语音使用 GPT-SoVITS v2ProPlus。仓库不是包含账号和模型的一键整合包，新电脑需完成下面的本地配置。

## 包含什么

| 目录或文件 | 用途 |
|---|---|
| AstrBot/data/plugins/astrbot_plugin_qq_bilingual_voice | 日语原句、中文显示、13 类标签与温柔原句语音 |
| AstrBot/data/plugins/astrbot_plugin_qq_image_files | 将 QQ 文件形式的图片与引用图片接入原生识图 |
| AstrBot/data/plugins/astrbot_plugin_qq_poke | 将有效戳一戳交给原生模型和人格回应 |
| AstrBot/data/plugins/astrbot_plugin_qq_fallback_phrase | 明确拒答或不知道答案时统一约定措辞 |
| Start.ps1 / Start-Voice.ps1 / Stop.ps1 | 启停本目录内的 AstrBot、NapCat、可选语音服务 |
| config.example / runtime/*.example.json | 无密钥的连接和语音配置样例 |
| docs/persona.example.txt / docs/语气判断标准.md | 当前角色人格示例与语气规则 |

没有上传第三方完整程序、Python 环境、QQ 登录状态、私聊/群聊记录、API Key、Token、模型权重、角色参考音频或训练数据。原有本机安装与数据保持原样。第三方项目和模型遵循各自许可证，本仓库未替它们重新授权。

## 重新部署

1. 将仓库放到普通本地目录，例如 D:/QQBot。按 [AstrBot 官方源码部署说明](https://docs.astrbot.app/deploy/astrbot/cli.html) 在本目录的 AstrBot 子目录安装程序及其 .venv，并取得官方 WebUI；已有插件目录需保留或复制回去。本地已安装版本可直接把这四个插件放进其 data/plugins。
2. 按 [NapCat 官方仓库](https://github.com/NapNeko/NapCatQQ) 安装 Windows Node 版本到 NapCat 子目录，保证其中存在 node.exe 和 index.js。仓库不替你迁移 QQ 客户端或用户数据。
3. 可选：从 [GPT-SoVITS 官方仓库](https://github.com/RVC-Boss/GPT-SoVITS) 准备程序到 GPT-SoVITS 子目录；使用自己有权使用的权重和参考音频。先按上游说明验证 api_v2.py 能完成合成，再填写 runtime 中的服务配置样例。模型和 Python 均放在此项目目录内，停止脚本才会管理这些进程。
4. 双击“启动机器人.cmd”。首次登录 NapCat WebUI 后自行扫码；不设置 QQBOT_ACCOUNT 时使用普通启动。已登录账号需要快捷登录时，可在启动脚本所在 PowerShell 中设置 `$env:QQBOT_ACCOUNT='你的机器人QQ'` 后运行 `./Start.ps1`。配置仍使用默认端口：AstrBot 6185、NapCat 6099、OneBot 6199、TTS 9880。
5. 在 AstrBot WebUI 设置模型 Key、默认聊天模型、允许的好友/群白名单和人格。NapCat 配置反向 WebSocket，与 AstrBot 使用相同 Token。详见 [配置说明](config.example/README.md)。参考人格需复制到 AstrBot 人格设置中；修改示例文本本身不会自动同步。
6. 需要双语语音时，在 AstrBot 添加原生 GPT-SoVITS 自托管 TTS，ID 为 hotaru_gsv_ja，API 地址为 http://127.0.0.1:9880，语言使用日语；翻译模型 ID 为 deepseek_flash。配置好温柔的默认参考，或在参考映射中填写“温柔亲近”的音频与对应日语文本，再开启双语插件。关闭 AstrBot 全局自动文字转语音，避免重复朗读中文。
7. 私聊测试文字、连续上下文、图片和语音；群聊仅在你配置允许时启用。示例人格固定于相应故事时点，可按自己的需求编辑；插件中的日语和翻译规则也包含角色专用内容，换人格时需一起检查。

## 使用与维护

双击“启动机器人.cmd”启动，双击“停止机器人.cmd”停止本目录内由脚本记录的进程。日志和 PID 在 logs。语音服务样例默认 disabled，不使用语音时无需安装 GPT-SoVITS。已提供 runtime/dashboard/dist 时启动脚本使用它，否则使用 AstrBot 默认 WebUI。

“打开手动配音.cmd”调用 GPT-SoVITS/go-webui.bat，适用于 v2ProPlus Windows 整合版。若你的安装方式不同，请直接按上游说明启动 WebUI。

通常每轮有一次聊天与一次翻译/语气 API 请求；本地语音不产生模型 API 用量。翻译失败保留日语原句，语音失败保留已发中文。单个情绪按 [13 类规则](docs/语气判断标准.md) 识别并记录；1.3.0 统一使用映射中的“温柔亲近”参考，不再随标签切换强情绪片段。未配置映射时沿用原生 TTS 默认参考；填写映射路径时，文件必须存在且是有效 JSON。

插件依赖 AstrBot 的内部 provider 接口，升级框架后应重新检查；本次语音调整保留角色、日语原句、中文翻译和上下文记忆，合成使用统一温柔参考、speed_factor=0.9 和 cut1 分句；末尾静音仍沿用原生默认约0.3秒。聊天记录、人格数据库和登录态留在本机。使用 AstrBot 自身功能另行备份它们，不把完整 data 或 NapCat 运行目录提交到仓库。

## 验证

整理时检查四个插件的 Python 语法、PowerShell 语法和 JSON 样例；图片插件保留现有六项回归测试。测试需要已安装的 AstrBot 及依赖；设置 QQBOT_TEST_ASTRBOT 为其目录后运行 `python tests/test_qq_image_files.py`。不会在测试中发送 QQ 消息或调用付费模型。

原运行版本此前已完成 QQ 文字/语音收发验证。干净仓库在填写你自己的账号、密钥和模型后，仍需自行确认实际收发；整理过程未重新登录或向任何联系人发送消息。


## 1.3.0 语音调整

此前按13类标签切换参考片段，且 cut5 会在日语逗号等位置切断句内连贯性。当前统一用“温柔亲近”参考作为声线基础，合成语速0.9，使用原生 cut1 减少碎句切分。其他情绪仍由日语原句表达，标签保留，不改写人格或台词。参数只作用于当前合成的提供商副本，共享默认配置不变。

已用真实萤模型合成同句对比和一条开心语句，三个音频均为32kHz非静音音频，原生QQ语音编码检查通过。同一句关心语句调整前5.82秒、调整后6.62秒；这仅说明本次样例的节奏变化，是否更贴角色需实际试听。音频、参考素材和本机验证记录不上传。
