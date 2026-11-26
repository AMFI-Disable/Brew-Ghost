# Brew-Ghost

[English](readme.md) · [贡献指南](contributing.zh-cn.md) · [更新日志](changelog.md) · [安全政策](security.md)

[![Website: Live](https://img.shields.io/badge/Website-Live-FBC02D.svg?style=flat-square)](https://amfi-disable.github.io/Brew-Ghost/)
[![Platform: macOS & Linux](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-blue.svg?style=flat-square&logo=apple)](https://apple.com)
[![Shell: Bash / Zsh](https://img.shields.io/badge/Shell-Bash%20%2F%20Zsh-orange.svg?style=flat-square&logo=gnubash)](https://gnu.org)
[![Tap: AMFI-Disable/tap](https://img.shields.io/badge/Tap-AMFI--Disable%2Ftap-blue.svg?style=flat-square&logo=homebrew)](https://brew.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](license)
[![Privacy: Zero Telemetry](https://img.shields.io/badge/Privacy-Zero%20Telemetry%20%2F%20100%25%20Local-purple.svg?style=flat-square)](#判断依据)

## 星标历史

<a href="https://www.star-history.com/?type=date&repos=amfi-disable%2Fbrew-ghost">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=amfi-disable%2Fbrew-ghost&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=amfi-disable%2Fbrew-ghost&type=date&legend=top-left" />
    <img alt="AMFI-Disable/Brew-Ghost Star History Chart" src="https://api.star-history.com/chart?repos=amfi-disable%2Fbrew-ghost&type=date&legend=top-left" />
  </picture>
</a>

## 安装和扫描

先安装 Homebrew，再运行：

```bash
brew tap AMFI-Disable/tap
brew install AMFI-Disable/tap/brew-ghost
brew-ghost
```

直接运行会列出候选软件包、磁盘占用和估算的闲置天数。默认阈值为 90 天。可用 `brew-ghost --json` 获取机器可读的结果，用 `brew-ghost --help` 查看参数。

## 判断依据

工具先用 `brew leaves` 列出顶层软件包，再用 `brew info --json=v2` 读取已安装版本、时间和大小。缺少大小信息时会尝试计算 Cellar 目录占用。程序在本机分析 `~/.zsh_history` 中与包名匹配的命令。通过图形界面启动、在脚本中运行或使用不同命令名的软件，可能没有匹配记录。

没有匹配记录时以安装时间为参考。历史记录缺少时间戳时，程序以历史文件的修改时间估算。要为今后的 Zsh 命令记录时间，可将以下设置加入 `~/.zshrc`：

```zsh
setopt EXTENDED_HISTORY
```

## 清理和历史记录

先查看扫描结果，确认仍在使用的工具没有被列入。运行 `brew-ghost --exorcise` 会显示待卸载列表并询问是否继续，直接回车可取消。确认后，程序会调用 Homebrew 卸载所列软件包。使用 `brew-ghost --history` 可查看记录的清理操作。

## 许可

本项目采用 [MIT 许可证](license)。
