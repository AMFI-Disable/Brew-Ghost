# 贡献指南

[English](contributing.md) · [项目说明](readme.zh-cn.md)

参与 Brew-Ghost 前，请查看现有议题，避免与其他贡献者重复开发。议题和拉取请求都可以使用英文或简体中文。

请参照[缺陷报告模板](.github/issue_template/bug_report.md)填写[新缺陷报告](https://github.com/AMFI-Disable/Brew-Ghost/issues/new?title=%5BBUG%5D%20)。

## 验证方法

在临时用户目录运行命令行测试，检查帮助与 JSON 输出。测试卸载时使用模拟的 Homebrew 命令。

```sh
python3 -m unittest discover
```

## 提交拉取请求

说明改动对用户的影响，关联相关议题，并附上验证结果。提交说明的格式为 `type: three lowercase words`。在更新日志的 Unreleased 部分记录改动。发布验证通过后，版本标签使用 `vMAJOR.MINOR.PATCH` 格式。
