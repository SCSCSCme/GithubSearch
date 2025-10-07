#!/usr/bin/env python3
"""
GitHub 仓库搜索命令行工具 (带分页)
用法：python github_search.py <关键词> [--page <页码>]
示例：
  python github_search.py python machine learning
  python github_search.py python --page 2
"""

import requests
import sys
import argparse

# GitHub API 基础 URL
GITHUB_API_URL = "https://api.github.com/search/repositories"

def truncate_text(text, max_length=100):
    """
    如果文本长度超过 max_length，则截断并在末尾添加 '...'
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def search_github_repos(query, page=1, per_page=10):
    """
    使用 GitHub API 搜索仓库，支持分页
    """
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'page': page,
        'per_page': per_page
    }

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'GitHub-Search-CLI'
    }

    try:
        response = requests.get(GITHUB_API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)

    data = response.json()
    repos = data.get('items', [])
    total_count = data.get('total_count', 0)
    total_pages = (total_count + per_page - 1) // per_page  # 向上取整

    if not repos:
        print(f"🔍 没有找到相关仓库。")
        return

    # 计算当前页的起始和结束索引
    start_index = (page - 1) * per_page + 1
    end_index = min(page * per_page, total_count)

    print(f"\n🎉 找到 {total_count} 个仓库，显示第 {start_index}-{end_index} 个 (共 {total_pages} 页，当前第 {page} 页)：\n")
    print("-" * 80)

    for repo in repos:
        name = repo.get('full_name', 'N/A')
        description = repo.get('description', '无描述')
        # 👇 使用我们之前加的截断功能
        description = truncate_text(description, 100)
        stars = repo.get('stargazers_count', 0)
        html_url = repo.get('html_url', 'N/A')
        owner = repo.get('owner', {}).get('login', 'N/A')

        print(f"🌟 {name}")
        print(f"   👤 作者: {owner}")
        print(f"   ⭐ 星标: {stars}")
        print(f"   📝 描述: {description}")
        print(f"   🔗 链接: {html_url}")
        print("-" * 80)

    # 如果当前页不是最后一页，提示用户可以翻页
    if page < total_pages:
        print(f"\n💡 提示：使用 --page {page + 1} 查看下一页")

def main():
    parser = argparse.ArgumentParser(description="在 GitHub 上搜索仓库 (支持分页)")
    parser.add_argument('query', nargs='+', help='搜索关键词（如：python machine learning）')
    parser.add_argument('--page', type=int, default=1, help='要显示的页码 (默认为1)')
    args = parser.parse_args()

    # 将多个参数拼接成一个搜索字符串
    query = ' '.join(args.query)
    page = args.page

    # 简单的页码验证
    if page < 1:
        print("❌ 页码必须大于0")
        sys.exit(1)

    print(f"🔎 正在搜索: '{query}'...")
    search_github_repos(query, page=page)

if __name__ == "__main__":
    main()
