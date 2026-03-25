"""
GitHub Pages 自动发布脚本
========================
将 NMPA 和挂网价监控的 HTML 结果自动推送到 GitHub Pages

使用方式：
  方式1：双击 publish.bat（自动发布两个工具的最新结果）
  方式2：命令行 python publish.py
  方式3：在爬虫脚本末尾加两行：
         from publish import publish_all
         publish_all()
"""

import os
import shutil
import subprocess
from datetime import datetime

# ============================================================
#  CONFIG - 你的配置
# ============================================================

# 仓库本地路径
REPO_DIR = r"D:\Claude\DBS-info"

# 你的 GitHub 用户名
GITHUB_USER = "vonatio"

# 两个监控工具的 HTML 结果路径
HTML_SOURCES = {
    "nmpa": r"D:\Claude\NMPA\3.0\result_latest.html",
    "guawangjia": r"D:\Claude\dbs_windows-guawangjia\result.html",
    "xiaohongshu-dashboard": r"D:\Claude\html-dashboard\xiaohongshu-dashboard.html",
}

# GitHub Pages 地址
PAGES_URL = f"https://{GITHUB_USER}.github.io/DBS-info/"

# ============================================================
#  核心逻辑
# ============================================================

def run_git(cmd, cwd=REPO_DIR):
    """执行 git 命令"""
    result = subprocess.run(
        cmd, cwd=cwd, shell=True,
        capture_output=True, text=True, encoding='utf-8'
    )
    return result


def publish_all():
    """发布所有监控结果到 GitHub Pages"""
    print(f"\n{'='*50}")
    print(f"  GitHub Pages 自动发布")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    # 检查仓库
    if not os.path.isdir(os.path.join(REPO_DIR, '.git')):
        print(f"[错误] {REPO_DIR} 不是 git 仓库")
        return False

    copied = []

    # 复制各个 HTML 到仓库
    for name, src in HTML_SOURCES.items():
        if not os.path.isfile(src):
            print(f"[跳过] {name}: 文件不存在 {src}")
            continue

        dest_name = f"{name}.html"
        dest = os.path.join(REPO_DIR, dest_name)
        shutil.copy2(src, dest)
        size = os.path.getsize(dest)
        mtime = datetime.fromtimestamp(os.path.getmtime(src)).strftime('%Y-%m-%d %H:%M')
        print(f"[复制] {name}.html ({size:,} bytes, 生成于 {mtime})")
        copied.append({"name": name, "file": dest_name, "time": mtime})

    if not copied:
        print("\n[错误] 没有找到任何 HTML 文件")
        return False

    # 生成首页 index.html
    generate_index(copied)
    print(f"[生成] index.html (首页导航)")

    # Git 推送
    print(f"\n[推送] git add + commit + push ...")
    run_git('git add -A')

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    result = run_git(f'git commit -m "update {now}"')
    if 'nothing to commit' in result.stdout + result.stderr:
        print(f"  内容没有变化，无需推送")
        return True

    result = run_git('git push origin main')
    if result.returncode != 0:
        # 尝试 master 分支
        result = run_git('git push origin master')
        if result.returncode != 0:
            print(f"[错误] 推送失败:")
            print(f"  {result.stderr.strip()}")
            print(f"\n  如果是权限问题，请确认 token 有 repo 权限")
            return False

    print(f"\n{'='*50}")
    print(f"  发布成功!")
    print(f"  首页: {PAGES_URL}")
    for item in copied:
        print(f"  {item['name']}: {PAGES_URL}{item['file']}")
    print(f"  (页面更新可能有 1-2 分钟延迟)")
    print(f"{'='*50}")
    return True


def generate_index(items):
    """生成首页 index.html"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cards = ""
    for item in items:
        LABELS = {
            "nmpa": "NMPA 医疗器械审批监控",
            "guawangjia": "DBS 挂网价监控",
            "xiaohongshu-dashboard": "「强迫之家」小红书运营Dashboard",
        }
        label = LABELS.get(item["name"], item["name"])
        cards += f'''
        <a href="{item['file']}" class="card">
            <div class="card-title">{label}</div>
            <div class="card-meta">数据更新: {item['time']}</div>
            <div class="card-action">点击查看 &rarr;</div>
        </a>
'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DBS Info Monitor</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, "Microsoft YaHei", sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 60px 20px;
        }}
        h1 {{
            font-size: 28px;
            color: #1a1a2e;
            margin-bottom: 8px;
        }}
        .subtitle {{
            color: #666;
            font-size: 14px;
            margin-bottom: 40px;
        }}
        .cards {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            justify-content: center;
            max-width: 700px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            width: 320px;
            text-decoration: none;
            color: inherit;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: all 0.2s;
            border: 1px solid #eee;
        }}
        .card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            border-color: #4a90d9;
        }}
        .card-title {{
            font-size: 18px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 12px;
        }}
        .card-meta {{
            font-size: 13px;
            color: #999;
            margin-bottom: 16px;
        }}
        .card-action {{
            font-size: 14px;
            color: #4a90d9;
            font-weight: 500;
        }}
        .footer {{
            margin-top: 60px;
            font-size: 12px;
            color: #bbb;
        }}
    </style>
</head>
<body>
    <h1>DBS Info Monitor</h1>
    <div class="subtitle">最后发布: {now}</div>
    <div class="cards">
{cards}
    </div>
    <div class="footer">Powered by GitHub Pages</div>
</body>
</html>'''

    with open(os.path.join(REPO_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == '__main__':
    success = publish_all()
    input("\n按回车键退出...")
