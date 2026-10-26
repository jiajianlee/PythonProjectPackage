# -*- coding: utf-8 -*-
"""
install_deps.py
用 sys.exec_prefix 下的 Python 解释器，安装 Requirements.txt 里的依赖。
Requirements.txt 格式：[{ "name": ..., "version": ..., "url": ... }, ...]
"""
import sys
import json
import subprocess
from pathlib import Path
from collections import OrderedDict

DEFAULT_INDEX = "https://pypi.org/simple"


def sh(cmd: list):
    """执行命令：列表传参，天然兼容带空格的路径，也不经过 shell，安全。"""
    print("\n>>>", " ".join(map(str, cmd)))
    return subprocess.run(cmd, check=True)


def get_python_exe() -> Path:
    """跨平台定位解释器。"""
    prefix = Path(sys.exec_prefix)
    if sys.platform.startswith("win"):
        exe = prefix / "python.exe"
    else:
        exe = prefix / "bin" / "python3"
        if not exe.exists():
            exe = prefix / "bin" / "python"
    if not exe.exists():
        raise FileNotFoundError(f"找不到 Python 解释器：{exe}")
    return exe


def ensure_pip(python_exe: Path):
    """优先用自带的 pip；没有再用 get-pip.py 引导安装。"""
    try:
        r = subprocess.run(
            [str(python_exe), "-m", "pip", "--version"],
            capture_output=True, text=True, check=True,
        )
        print(f"✅ pip 已就绪：{r.stdout.strip()}")
        return
    except subprocess.CalledProcessError:
        print("⚠️ 当前解释器没有可用 pip，尝试通过 get-pip.py 安装 …")

    get_pip = Path(sys.exec_prefix) / "get-pip.py"
    if not get_pip.exists():
        raise FileNotFoundError(
            f"找不到 get-pip.py：{get_pip}\n"
            f"请先下载：https://bootstrap.pypa.io/get-pip.py 放到该目录"
        )
    sh([str(python_exe), str(get_pip),"-i https://pypi.tuna.tsinghua.edu.cn/simple"])


def load_requirements(req_path: Path) -> list:
    if not req_path.exists():
        raise FileNotFoundError(f"找不到依赖清单：{req_path}")
    with open(req_path, "r", encoding="utf-8") as f:   # 关键：指定 utf-8
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Requirements.txt 顶层应为 JSON 数组")
    return data


def group_by_index(deps: list):
    """按 index-url 分组：同一源的包合并成一次 pip install，减少启动次数。"""
    groups = OrderedDict()
    for d in deps:
        if "name" not in d:
            raise KeyError(f"依赖项缺少 name 字段：{d}")
        name = d["name"].strip()
        ver = (d.get("version") or "").strip()
        spec = f"{name}=={ver}" if ver else name            # 锁定版本
        url = (d.get("url") or DEFAULT_INDEX).strip()
        groups.setdefault(url, []).append(spec)
    return list(groups.items())


def install_group(python_exe: Path, url: str, specs: list, no_deps: bool):
    cmd = [
        str(python_exe), "-m", "pip", "install",
        "--index-url", url,
        "--disable-pip-version-check",
        "--no-warn-script-location",
    ]
    if no_deps:
        cmd.append("--no-deps")   # 清单本身已是完整闭包，避免依赖被别的源覆盖
    cmd.extend(specs)
    sh(cmd)


def install_all(python_exe: Path, deps: list, no_deps: bool = True, retries: int = 2):
    """按源分组安装；单组失败不中断其余组，最后统一汇报。"""
    failed = []
    for url, specs in group_by_index(deps):
        print(f"\n===== 源：{url}（{len(specs)} 个包）=====")
        attempt = 0
        while True:
            try:
                install_group(python_exe, url, specs, no_deps)
                break
            except subprocess.CalledProcessError:
                attempt += 1
                if attempt > retries:
                    print(f"❌ 源 {url} 安装失败，已重试 {retries} 次")
                    failed.append((url, specs))
                    break
                print(f"⚠️ 安装失败，第 {attempt} 次重试 …")
    return failed


def main():
    print("开始安装依赖，请保持网络畅通")

    python_exe = get_python_exe()
    print(f"使用解释器：{python_exe}")
    print(f"Python 版本：{sys.version.split()[0]}")

    ensure_pip(python_exe)

    deps = load_requirements(Path(sys.exec_prefix) / "Requirements.txt")
    print(f"共读取到 {len(deps)} 个依赖")

    failed = install_all(python_exe, deps, no_deps=True)

    if failed:
        print("\n❌ 以下分组安装失败，请检查网络或手动重试：")
        for url, specs in failed:
            print(f"  [{url}]")
            for s in specs:
                print(f"    - {s}")
        sys.exit(1)

    print("\n🎉 全部依赖安装完成")


if __name__ == "__main__":
    main()