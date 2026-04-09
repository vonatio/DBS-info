"""
HTML 汇报材料管理 & 发布脚本 v2.0
==================================
基于 registry.json 注册表，自动分流发布：
  - scope=public  → GitHub Pages (公网可访问)
  - scope=internal → D:\\share\\06-市场沟通\\reports (内网共享文件夹)

使用方式：
  方式1：双击 publish.bat
  方式2：命令行 python publish.py
  方式3：python publish.py --public-only  (仅发布公开内容)
  方式4：python publish.py --internal-only (仅发布内网内容)
  方式5：在其他脚本中: from publish import publish_all; publish_all()
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime

# ============================================================
#  CONFIG
# ============================================================

REPO_DIR = r"D:\Claude\DBS-info"
REGISTRY_PATH = r"D:\Claude\html-dashboard\registry.json"
INTERNAL_DIR = r"D:\share\06-市场沟通\reports"
GITHUB_USER = "vonatio"
PAGES_URL = f"https://{GITHUB_USER}.github.io/DBS-info/"

# ============================================================
#  注册表读取
# ============================================================

def load_registry():
    """读取 registry.json"""
    if not os.path.isfile(REGISTRY_PATH):
        print(f"[错误] 注册表不存在: {REGISTRY_PATH}")
        return []
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("reports", [])


def save_registry(reports):
    """保存 registry.json (保留 schema 信息)"""
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data["reports"] = reports
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_timestamp(report_id):
    """更新某个报告的 updated 时间戳"""
    reports = load_registry()
    for r in reports:
        if r["id"] == report_id:
            r["updated"] = datetime.now().strftime("%Y-%m-%d")
            break
    save_registry(reports)

# ============================================================
#  Git 操作
# ============================================================

def run_git(cmd, cwd=REPO_DIR):
    result = subprocess.run(
        cmd, cwd=cwd, shell=True,
        capture_output=True, text=True, encoding='utf-8'
    )
    return result

# ============================================================
#  GitHub Pages 首页生成 (仅 public 内容)
# ============================================================

def generate_index(items):
    """生成 GitHub Pages 首页 index.html"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cards = ""
    for item in items:
        # 根据 category 选择颜色
        color_map = {
            "monitor": "#4a90d9",
            "analysis": "#d9534f",
            "training": "#f0ad4e",
            "education": "#5cb85c",
            "strategy": "#9b59b6",
        }
        color = color_map.get(item.get("category", ""), "#4a90d9")
        badge = item.get("category", "other").upper()

        cards += f'''
        <a href="{item['id']}.html" class="card">
            <div class="card-badge" style="background: {color}15; color: {color}">{badge}</div>
            <div class="card-title">{item['title']}</div>
            <div class="card-desc">{item.get('description', '')[:60]}</div>
            <div class="card-meta">更新: {item.get('updated', 'N/A')}</div>
            <div class="card-action">点击查看 &rarr;</div>
        </a>
'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DBS Info Hub</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, "Microsoft YaHei", sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            display: flex; flex-direction: column; align-items: center;
            padding: 60px 20px;
        }}
        h1 {{ font-size: 28px; color: #1a1a2e; margin-bottom: 8px; }}
        .subtitle {{ color: #666; font-size: 14px; margin-bottom: 40px; }}
        .cards {{
            display: flex; gap: 20px; flex-wrap: wrap;
            justify-content: center; max-width: 900px;
        }}
        .card {{
            background: white; border-radius: 12px; padding: 24px;
            width: 280px; text-decoration: none; color: inherit;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: all 0.2s; border: 1px solid #eee;
        }}
        .card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            border-color: #4a90d9;
        }}
        .card-badge {{
            display: inline-block; font-size: 11px; font-weight: 600;
            padding: 2px 8px; border-radius: 4px; margin-bottom: 12px;
            letter-spacing: 0.5px;
        }}
        .card-title {{ font-size: 17px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }}
        .card-desc {{ font-size: 13px; color: #888; margin-bottom: 12px; line-height: 1.5; }}
        .card-meta {{ font-size: 12px; color: #bbb; margin-bottom: 12px; }}
        .card-action {{ font-size: 14px; color: #4a90d9; font-weight: 500; }}
        .footer {{ margin-top: 60px; font-size: 12px; color: #bbb; }}
        .scope-note {{
            background: #fff3cd; color: #856404; font-size: 12px;
            padding: 8px 16px; border-radius: 6px; margin-bottom: 24px;
        }}
    </style>
</head>
<body>
    <h1>DBS Info Hub</h1>
    <div class="subtitle">最后发布: {now}</div>
    <div class="scope-note">此页面仅展示可公开内容，内部数据请通过共享文件夹访问</div>
    <div class="cards">
{cards}
    </div>
    <div class="footer">Powered by GitHub Pages &middot; Registry v1.0</div>
</body>
</html>'''

    with open(os.path.join(REPO_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)

# ============================================================
#  内网首页生成 (仅 internal 内容)
# ============================================================

def generate_internal_index(items):
    """生成内网共享文件夹的 index.html"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    rows = ""
    for item in items:
        tags_html = " ".join(
            f'<span class="tag">{t}</span>' for t in item.get("tags", [])[:4]
        )
        rows += f'''
        <tr onclick="window.location='{item['id']}.html'" style="cursor:pointer">
            <td><strong>{item['title']}</strong></td>
            <td>{item.get('category', '')}</td>
            <td>{item.get('status', '')}</td>
            <td>{item.get('updated', '')}</td>
            <td>{tags_html}</td>
        </tr>
'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>内部汇报材料</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, "Microsoft YaHei", sans-serif;
            background: #f8f9fa; padding: 40px 24px;
        }}
        h1 {{ font-size: 22px; color: #333; margin-bottom: 4px; }}
        .subtitle {{ color: #888; font-size: 13px; margin-bottom: 24px; }}
        .warn {{
            background: #f8d7da; color: #721c24; font-size: 12px;
            padding: 8px 14px; border-radius: 6px; margin-bottom: 20px;
            display: inline-block;
        }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
        th {{ background: #f1f3f5; font-size: 13px; font-weight: 600; color: #555; text-align: left; padding: 10px 14px; }}
        td {{ padding: 12px 14px; font-size: 13px; border-top: 1px solid #eee; color: #333; }}
        tr:hover td {{ background: #f8f9ff; }}
        .tag {{
            display: inline-block; background: #e9ecef; color: #555;
            font-size: 11px; padding: 1px 6px; border-radius: 3px; margin-right: 4px;
        }}
        #search {{
            padding: 8px 14px; font-size: 14px; border: 1px solid #ddd;
            border-radius: 6px; width: 300px; margin-bottom: 16px;
        }}
    </style>
</head>
<body>
    <h1>内部汇报材料</h1>
    <div class="subtitle">最后更新: {now}</div>
    <div class="warn">仅限内网访问 - 请勿外传</div>
    <br><br>
    <input type="text" id="search" placeholder="搜索标题或标签..." oninput="filterTable(this.value)">
    <table id="report-table">
        <thead>
            <tr><th>标题</th><th>类别</th><th>状态</th><th>更新日期</th><th>标签</th></tr>
        </thead>
        <tbody>
{rows}
        </tbody>
    </table>
    <script>
    function filterTable(q) {{
        q = q.toLowerCase();
        document.querySelectorAll('#report-table tbody tr').forEach(function(row) {{
            var text = row.textContent.toLowerCase();
            row.style.display = text.includes(q) ? '' : 'none';
        }});
    }}
    </script>
</body>
</html>'''

    os.makedirs(INTERNAL_DIR, exist_ok=True)
    with open(os.path.join(INTERNAL_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)

# ============================================================
#  核心发布逻辑
# ============================================================

def publish_all(scope_filter=None):
    """
    发布所有注册表中的报告
    scope_filter: None=全部, 'public'=仅公开, 'internal'=仅内网
    """
    print(f"\n{'='*50}")
    print(f"  HTML 汇报材料发布系统 v2.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if scope_filter:
        print(f"  模式: 仅发布 {scope_filter}")
    print(f"{'='*50}\n")

    reports = load_registry()
    if not reports:
        print("[错误] 注册表为空或读取失败")
        return False

    # 按 scope 分组
    public_items = [r for r in reports if r.get("scope") == "public" and r.get("status") != "archived"]
    internal_items = [r for r in reports if r.get("scope") == "internal" and r.get("status") != "archived"]

    print(f"[注册表] 共 {len(reports)} 个报告: {len(public_items)} 公开, {len(internal_items)} 内网\n")

    # === 发布公开内容到 GitHub Pages ===
    if scope_filter in (None, "public") and public_items:
        print("--- GitHub Pages (公开) ---")
        if not os.path.isdir(os.path.join(REPO_DIR, '.git')):
            print(f"[错误] {REPO_DIR} 不是 git 仓库")
        else:
            copied_public = []
            for r in public_items:
                src = r["source_path"]
                if not os.path.isfile(src):
                    print(f"  [跳过] {r['id']}: 源文件不存在 {src}")
                    continue
                dest = os.path.join(REPO_DIR, f"{r['id']}.html")
                shutil.copy2(src, dest)
                size = os.path.getsize(dest)
                print(f"  [复制] {r['id']}.html ({size:,} bytes)")
                copied_public.append(r)

            if copied_public:
                generate_index(copied_public)
                print(f"  [生成] index.html")

                run_git('git add -A')
                now = datetime.now().strftime('%Y-%m-%d %H:%M')
                result = run_git(f'git commit -m "update {now}"')
                if 'nothing to commit' in result.stdout + result.stderr:
                    print(f"  [无变化] 内容未改变，跳过推送")
                else:
                    result = run_git('git push origin main')
                    if result.returncode != 0:
                        result = run_git('git push origin master')
                    if result.returncode == 0:
                        print(f"  [推送成功] {PAGES_URL}")
                    else:
                        print(f"  [推送失败] {result.stderr.strip()}")
            print()

    # === 发布内网内容到共享文件夹 ===
    if scope_filter in (None, "internal") and internal_items:
        print("--- 共享文件夹 (内网) ---")
        os.makedirs(INTERNAL_DIR, exist_ok=True)
        copied_internal = []
        for r in internal_items:
            src = r["source_path"]
            if not os.path.isfile(src):
                print(f"  [跳过] {r['id']}: 源文件不存在 {src}")
                continue
            dest = os.path.join(INTERNAL_DIR, f"{r['id']}.html")
            shutil.copy2(src, dest)
            size = os.path.getsize(dest)
            print(f"  [复制] {r['id']}.html ({size:,} bytes)")
            copied_internal.append(r)

        if copied_internal:
            generate_internal_index(copied_internal)
            print(f"  [生成] index.html (内网索引页)")
            print(f"  [路径] {INTERNAL_DIR}")
        print()

    # === 汇总 ===
    print(f"{'='*50}")
    print(f"  发布完成!")
    if scope_filter in (None, "public") and public_items:
        print(f"  公开: {PAGES_URL}")
    if scope_filter in (None, "internal"):
        print(f"  内网: {INTERNAL_DIR}\\index.html")
    print(f"{'='*50}")
    return True

# ============================================================
#  CLI 工具函数
# ============================================================

def list_reports():
    """列出所有注册的报告"""
    reports = load_registry()
    print(f"\n{'='*60}")
    print(f"  已注册的 HTML 汇报材料 ({len(reports)} 个)")
    print(f"{'='*60}")
    for r in reports:
        scope_icon = "🌐" if r["scope"] == "public" else "🔒"
        status_map = {"draft": "草稿", "final": "定稿", "archived": "归档"}
        status = status_map.get(r["status"], r["status"])
        print(f"  {scope_icon} [{r['id']}] {r['title']}")
        print(f"     {r['category']} | {status} | 更新: {r.get('updated', 'N/A')}")
        print(f"     源: {r['source_path']}")
        print()


def add_report(report_id, title, source_path, category="analysis", scope="internal", description="", tags=None):
    """添加新报告到注册表"""
    reports = load_registry()

    # 检查 ID 是否重复
    if any(r["id"] == report_id for r in reports):
        print(f"[错误] ID '{report_id}' 已存在")
        return False

    new_report = {
        "id": report_id,
        "title": title,
        "category": category,
        "scope": scope,
        "status": "final",
        "source_path": source_path,
        "description": description,
        "tags": tags or [],
        "created": datetime.now().strftime("%Y-%m-%d"),
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "author": "lee",
        "template": None,
    }

    reports.append(new_report)
    save_registry(reports)
    print(f"[添加成功] {report_id} → {scope}")
    return True


# ============================================================
#  入口
# ============================================================

if __name__ == '__main__':
    args = sys.argv[1:]

    if '--list' in args:
        list_reports()
    elif '--public-only' in args:
        publish_all(scope_filter="public")
    elif '--internal-only' in args:
        publish_all(scope_filter="internal")
    else:
        publish_all()

    input("\n按回车键退出...")
