# Project Policy Overrides

只有真实项目约束与默认策略不同时才创建根 `.agent-layout.json`。检查器读取该文件并在内置策略上追加例外，不自动生成它。

```json
{
  "root_markdown_allowlist_add": ["CHANGELOG.md"],
  "ignored_directory_names_add": ["vendor-cache"],
  "runtime_directory_names_add": ["generated-output"]
}
```

- `*_add` 只能追加字符串列表，不能删除默认安全规则。
- 根 Markdown 例外应有工具链或组织规范依据。
- 不要通过忽略规则隐藏密钥、日志、dump 或未知生成产物。
