# 本地配置

这些文件仅为对照样例，真实账号、Key、Token 均由使用者在本地配置。

- AstrBot：新建模型提供商 `deepseek_flash`，地址 `https://api.deepseek.com/v1`，选择实际可用的模型并填自己的 API Key。主聊天和翻译使用同一提供商 ID。
- OneBot v11：AstrBot 监听 `127.0.0.1:6199`；NapCat 反向 WebSocket 连 `ws://127.0.0.1:6199/ws`。两端设置相同的自选 Token，参考 `onebot11.json`。
- 白名单：在 AstrBot 中分别设置允许的好友 QQ 和群号，不要把机器人账号、好友账号与群号混为一项。主模型、人格和触发规则都在本地 WebUI 设置。
- `bilingual-voice.json` 对应插件设置页面，默认不启用；完成日语 TTS 配置后再启用。
- 语音服务配置：复制 `runtime/gpt-sovits-service.example.json` 为同目录 `gpt-sovits-service.json`，改成自己机器上的 Python、程序和推理配置路径，确认后将 enabled 设为 true。
- 情绪参考：复制 `hotaru-reference-map.example.json` 为同目录 `hotaru-reference-map.json`，填每类音频的真实路径与对应日文原文，再把绝对路径填入插件的 emotion_references_path。没有情绪参考时保留空路径，使用 TTS 模型默认参考。
