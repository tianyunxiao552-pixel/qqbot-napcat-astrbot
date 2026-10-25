# 模型与恢复

聊天和翻译使用在 AstrBot 中配置的在线提供商，Key 仅留本机。

语音程序来自 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)。通用预训练依赖按上游说明下载。本地运行方案使用 v2ProPlus 和第三方角色分享包的第 8 轮 GPT/SoVITS 权重；这些专用文件及 13 类日语参考音频没有可由本仓库保证长期有效的官方下载地址，因此从源码恢复时需要另行保留自己的合法副本。

本仓库不包含或删除这些文件，也未替你完成模型网盘备份。请将配对的 `.ckpt`、`.pth`、参考音频、对应原文和映射文件一起保存。换机器后更新配置中的路径。通用预训练模型可以重新下载，专用角色权重和参考素材不能视为自动恢复。

将 `runtime/tts-infer.example.yaml` 复制为 `runtime/tts-infer.local.yaml`，填入自己配对权重的路径；然后在 `gpt-sovits-service.json` 的 infer_config 中指向它。
