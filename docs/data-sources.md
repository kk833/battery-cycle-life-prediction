# 数据源调研

> 结论先行：**Severson 2019 的原始数据能拿到，但体积 3.24 GB，且国内网络下下载不稳。**
> 第一版流水线必须能在**不下这 3 GB** 的前提下跑通，否则这个项目在真实环境里根本没法迭代。

## 一、数据是什么

| | |
|---|---|
| **来源** | Severson et al., *Data-driven prediction of battery cycle life before capacity degradation*, Nature Energy 4, 383–391 (2019) |
| **内容** | 124 颗 LFP/石墨电芯的完整循环数据（电压、电流、温度、容量，逐圈记录） |
| **关键性质** | 论文的核心结论就是「**用前 100 圈就能预测总循环寿命**」——和本项目的 Issue #1 完全对口 |
| **官方入口** | https://data.matr.io/1/ （项目 `5c48dd2bc625d700019f3204`） |

## 二、候选数据源实测（2026-09）

**复现方式**：`python scripts/fetch_data.py --check`
（下表 = 该脚本的实际输出，两边必须一致；不一致就是有一方错了）

| 数据源 | 预期体积 | 实测 | 结论 |
|---|---|---|---|
| data.matr.io 原始 Batch 1 | 3.24 GB | HTTP 200，**5 KB，`text/html`** | ⚠️ **这不是直链**，返回的是网页 |
| HuggingFace 镜像 | 3.24 GB | **不可达** | ❌ 当前网络环境下被阻断 |
| dsr-18/long-live-the-battery-dataset | ~453 MB | HTTP 200（API 元数据） | 🟡 仓库可达，已转 tfrecords，需 TensorFlow |
| GitHub API | - | HTTP 200 | ✅ 可作网络基线对照 |

### ⚠️ 本节记录了一个踩过的坑

第一版调研里，那条 `data.matr.io/.../fileDownload/...` 是**猜的直链**——
实测返回 `HTTP 200` 但**只有 5 KB 的 HTML 页面**，说明这个 fileId 不对。

> **教训**：`HTTP 200` ≠ 拿到了文件。
> **必须同时看体积和 Content-Type**——这条检查现在写进脚本里了。

真正的直链需要去 https://data.matr.io/1/ 页面里取真实的 fileId。
**这一步留给下一个 PR。**

## 三、一个重要的观察

GitHub 上已经存在**多个**同类复现仓库（`sami-ennedoui/battery-cycle-life`、`AmirrezaRoodsaz/battery-rul-prediction`、`ibtisamkhan96/battery-lifetime-prediction` 等）。

**但它们的 `data/` 目录全都是空的。**

> 说明：**这一关大家都卡过** —— 原始数据太大，没人把它提交进仓库。
> 这是这类项目公认的第一个门槛，不是我们做错了什么。

## 四、下一步（本 PR 之后）

1. **数据获取做成可续传的脚本**，并把下载校验（文件大小 + 哈希）写进去
2. **先只下载一颗电芯**，跑通「读 → 特征 → 基线」的最小闭环，再决定要不要拉全量
3. 基线（线性外推）先落地——**在拿到完整数据之前，它就能先写好并单测**

## 五、诚实边界（对应 Issue #1 第 4 条）

- Severson 是**实验室循环老化数据**（124 颗、特定充放电协议），**不是真实产线数据**
- 本项目能得出的结论是「**方法在这份数据上可行、比基线好**」
- **不能**说「真实产线上误差 X%」
