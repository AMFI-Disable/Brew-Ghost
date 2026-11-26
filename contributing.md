# Contributing

[中文文档](contributing.zh-cn.md) · [Project Guide](readme.md)

Before working on Brew-Ghost, check open issues and coordinate overlapping changes. Issues and pull requests accept English or Simplified Chinese.

Use the [bug report outline](.github/issue_template/bug_report.md) to [open a bug report](https://github.com/AMFI-Disable/Brew-Ghost/issues/new?title=%5BBUG%5D%20).

## Verification

Run the CLI tests with a disposable home directory. Check help and JSON output. Use mocked Homebrew commands for uninstall tests.

```sh
python3 -m unittest discover
```

## Preparing A Pull Request

Describe the observable change, link related issues and include test results. Keep commit messages in the form `type: three lowercase words`. Record changes under Unreleased. Release tags use `vMAJOR.MINOR.PATCH` after verification.
