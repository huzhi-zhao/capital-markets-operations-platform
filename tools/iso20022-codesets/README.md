# ISO 20022 Code Sets Extraction

从 ISO 20022 注册机构发布的 External Code Sets 与银行交易码组合表抽取计数，产出
`data/reference/iso20022/manifest.json`。它是文档里码值数字的凭证，不是 Bronze 事实。
引用这些数字的地方见[验证与对账规范](../../docs/dev/requirements/validation-and-reconciliation-specification.md)。

## 源文件

需要手工从 iso20022.org 下载，放在同一目录下：

| 文件 | 内容 |
|---|---|
| `ExternalCodeSets_XLSX.zip` | 全部码值，含 Registered 与 Obsolete 状态 |
| `ExternalCodeSets_JSON.zip` | JSON Schema，只含 Registered 码值 |
| `BTC_Codification_30Nov2025.xlsx` | 银行交易码 Domain/Family/SubFamily 组合表 |

manifest 里记录了三者的 sha256，换版本时哈希会变，测试会失败，这是预期行为。

## 运行

```bash
python3 tools/iso20022-codesets/extract.py --src ~/Downloads
```

`--out DIR` 另外写两份 TSV 词表（码值与组合），供本地判定使用，**不提交**，理由见下。

```bash
python3 -m pytest tools/iso20022-codesets/tests
```

源文件目录用 `CMOP_ISO20022_SRC` 指定，默认 `~/Downloads`。源文件不在场时只检查已提交的
manifest，重跑比对会被跳过。

## 两个读表要点

- **按单元格坐标取列。** 空单元格在 xlsx 里直接缺席，按出现顺序读会让整行左移。
- **XLSX 有 141 个码集，JSON 只有 140 个。** 差的那个是 `ExternalUndertakingDocumentType2Code`，
  它的 3 个码值全部是 Obsolete，JSON 只收 Registered，于是整个码集消失。这不是抽取错误。

## 许可

**再分发条款尚未确认。** 仓库里没有记录 ISO 20022 External Code Sets 的使用条款，
[监管数据契约](../../docs/dev/requirements/regulatory-data-contracts.md) §7 又规定第三方
规范文本不入库。因此本工具只提交脚本、manifest 与派生计数，不提交原始文件与完整词表。
条款确认允许再分发之后，才考虑把 TSV 钉进 `data/reference/iso20022/`。
