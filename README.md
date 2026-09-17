# battery-cycle-life-prediction
用**前 100 圈循环数据**预测锂电池的**循环寿命**（早期寿命筛选）。

- 需求来源：[Issue #1](../../issues/1)
- 数据：Severson et al. 2019（Nature Energy）公开数据集，124 颗电芯
- 方法：先做线性外推基线，再上模型；对比两者
- 验收标准：见 Issue #1（MAPE 目标 + 基线对比 + 诚实边界）

> 本仓库是 HA7CH AI Native School 共修节点的实操项目，用来走通
> **issue → branch → PR → diff → 验收 → merge** 全流程。

## 怎么跑

```bash
python scripts/fetch_data.py --check
```
零依赖，clone 下来就能跑。输出应能对照 docs/data-sources.md 第二节的表格。
