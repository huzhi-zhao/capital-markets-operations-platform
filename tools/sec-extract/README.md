# SEC Extraction

从美国证监会的结构化接口抽取公司行为事件。产出是**参考数据**，用于给合成数据生成器的
事件分布提供真实锚点，不是 Bronze 事实。决策依据见
[原始数据源清单](../../docs/dev/requirements/raw-data-source-inventory.md) §5.3 到 §5.7。

## 两个脚本

| 脚本 | 抽取内容 | 调用量 |
|---|---|---|
| `extract-events.py` | 拆股与合股、分红、退市、代码与交易所全集 | 约 121 次 |
| `extract-former-names.py` | 更名历史，按 CIK 逐个调用 `submissions` | 每个 CIK 一次 |

第二个脚本依赖第一个的产出 `universe-ciks.txt`，必须先跑第一个。

## 运行

```bash
python3 tools/sec-extract/extract-events.py
python3 tools/sec-extract/extract-former-names.py
```

两个环境变量：

- `CMOP_SEC_UA` 覆盖 User-Agent。**证监会的公平访问政策要求请求头声明联系邮箱**，默认值
  里的地址是本项目作者的，换人使用时必须改。
- `CMOP_SEC_RAW` 覆盖输出目录，默认写入 `data/reference/sec/raw/`。

速率固定在每秒约 8 次，低于证监会每秒 10 次的上限。不要调高。

## 许可

证监会明确说明站上信息属于公开信息，无需其许可即可复制或进一步分发；不得使用其徽标与
商标，并应注明来源。抽取到的内容本身是事实而非受保护的表达。

## 为什么原始响应要提交进仓库

证监会的数据会随补充申报与更正而变化，**今天重跑不会得到文档里引用的同一批数字**。原始
响应因此被钉住并提交，使文档中每一个实测数字可以事后复核。重新抽取时不要覆盖，另起一个
带日期的 manifest。
