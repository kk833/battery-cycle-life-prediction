#!/usr/bin/env python3
"""数据源可达性自检。

真实数据项目的第一个难关不是建模，是搞清楚：数据在哪、多大、拿不拿得到。
这个脚本不下载数据，只**探测**每个候选数据源，把结论打成一张表。

用法：
    python scripts/fetch_data.py --check

输出：一行一个数据源，含可达性、体积、内容类型、结论。
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request

# 候选数据源
# size_hint 来自上游页面说明 / 公开资料，可能与实际略有出入
SOURCES = [
    {
        "name": "Severson 2019 原始批次数据（Batch 1）",
        "url": "https://data.matr.io/1/api/v1/fileDownload/5c48dd2bc625d700019f3205",
        "size_hint": "3.24 GB",
        "expect": "file",
        "note": "论文原始 .mat，需 scipy.io.loadmat；体积大、国内下载不稳",
    },
    {
        "name": "HuggingFace 镜像（bsebench-org/severson-2019-raw）",
        "url": "https://huggingface.co/datasets/bsebench-org/severson-2019-raw/resolve/main/2018-04-12_batchdata_updated_struct_errorcorrect.mat",
        "size_hint": "3.24 GB",
        "expect": "file",
        "note": "原始文件的镜像，同样体积",
    },
    {
        "name": "dsr-18/long-live-the-battery-dataset（已处理）",
        "url": "https://api.github.com/repos/dsr-18/long-live-the-battery-dataset",
        "size_hint": "约 453 MB",
        "expect": "api",
        "note": "已转成 tfrecords，需要 TensorFlow 读取",
    },
    {
        "name": "GitHub API（连通性基线）",
        "url": "https://api.github.com/rate_limit",
        "size_hint": "-",
        "expect": "api",
        "note": "用来对照：API 通不代表网页 / 大文件下载通",
    },
]

TIMEOUT = 30
UA = {"User-Agent": "battery-life-prediction/0.1 (+https://github.com/kk833)"}


def probe(url: str, expect: str) -> dict:
    """只读响应头，不下载 body。返回探测结论。"""
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            h = resp.headers
            raw_len = h.get("Content-Length")
            ctype = (h.get("Content-Type") or "").split(";")[0].strip()
            size = _human(int(raw_len)) if raw_len and raw_len.isdigit() else "未提供"
            verdict = _verdict(resp.status, ctype, expect)
            return {"status": f"HTTP {resp.status}", "size": size, "ctype": ctype, "verdict": verdict}
    except urllib.error.HTTPError as e:
        return {"status": f"HTTP {e.code}", "size": "未知", "ctype": "-", "verdict": f"❌ 请求被拒（{e.reason}）"}
    except Exception as e:
        return {"status": "不可达", "size": "未知", "ctype": "-", "verdict": f"❌ {type(e).__name__}"}


def _verdict(status: int, ctype: str, expect: str) -> str:
    if status != 200:
        return f"❌ 非 200"
    if expect == "file":
        if "html" in ctype:
            return "⚠️ 返回的是网页，不是文件 —— 这个地址不是直链"
        if "octet-stream" in ctype or "mat" in ctype or "zip" in ctype:
            return "✅ 像直链文件"
        return f"🟡 内容类型存疑（{ctype}）"
    return "✅ 可达"


def _human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def main() -> int:
    ap = argparse.ArgumentParser(description="探测电池寿命预测项目的候选数据源")
    ap.add_argument("--check", action="store_true", help="探测所有候选数据源并打印报告")
    args = ap.parse_args()

    if not args.check:
        ap.print_help()
        return 0

    print("候选数据源可达性报告")
    print("=" * 96)
    for s in SOURCES:
        r = probe(s["url"], s["expect"])
        print(f"\n· {s['name']}")
        print(f"    URL      : {s['url']}")
        print(f"    预期体积  : {s['size_hint']}")
        print(f"    实测      : {r['status']}   体积 {r['size']}   类型 {r['ctype']}")
        print(f"    结论      : {r['verdict']}")
        print(f"    备注      : {s['note']}")
    print("\n" + "=" * 96)
    print("结论与下一步见 docs/data-sources.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
