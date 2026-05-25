#!/usr/bin/env python3
"""
crush.skill — 社交媒体内容解析器
支持微博/小红书/Instagram 导出内容的解析。
"""

import argparse
import re
import json
import sys
from datetime import datetime


def parse_weibo_json(filepath):
    """解析微博 JSON 导出"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"JSON 解析错误: {e}", file=sys.stderr)
        return results

    # 微博导出的 JSON 结构可能不同，尝试常见格式
    posts = data if isinstance(data, list) else data.get('statuses', data.get('posts', []))

    for post in posts:
        if isinstance(post, dict):
            text = post.get('text', post.get('raw_text', post.get('content', '')))
            # 去除 HTML 标签
            text = re.sub(r'<[^>]+>', '', text)

            results.append({
                'time': post.get('created_at', post.get('time', '')),
                'content': text,
                'source': post.get('source', ''),
                'reposts': post.get('reposts_count', 0),
                'comments': post.get('comments_count', 0),
                'likes': post.get('attitudes_count', post.get('likes_count', 0)),
            })

    return results


def parse_xiaohongshu_json(filepath):
    """解析小红书 JSON 导出"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return results

    notes = data if isinstance(data, list) else data.get('notes', data.get('posts', []))

    for note in notes:
        if isinstance(note, dict):
            results.append({
                'time': note.get('time', note.get('created_at', '')),
                'content': note.get('title', '') + '\n' + note.get('desc', note.get('content', '')),
                'likes': note.get('liked_count', note.get('likes', 0)),
                'collected': note.get('collected_count', note.get('collects', 0)),
                'tags': note.get('tags', []),
            })

    return results


def parse_instagram_json(filepath):
    """解析 Instagram JSON 导出"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return results

    media = data if isinstance(data, list) else data.get('media', data.get('posts', []))

    for item in media:
        if isinstance(item, dict):
            caption = ''
            if 'caption' in item:
                if isinstance(item['caption'], dict):
                    caption = item['caption'].get('text', '')
                else:
                    caption = str(item['caption'])

            results.append({
                'time': item.get('timestamp', item.get('created_at', '')),
                'content': caption,
                'likes': item.get('like_count', item.get('likes', 0)),
                'comments': item.get('comment_count', item.get('comments', 0)),
            })

    return results


def parse_text(filepath):
    """解析纯文本/CSV 内容"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='gbk') as f:
            content = f.read()

    # 尝试按行解析，支持简单的 CSV 格式
    lines = content.strip().split('\n')
    for line in lines:
        parts = line.split(',', 2)
        if len(parts) >= 2:
            results.append({
                'time': parts[0].strip(),
                'content': parts[-1].strip(),
            })
        else:
            results.append({
                'time': '',
                'content': line.strip(),
            })

    return results


def format_output(items):
    """格式化输出"""
    if not items:
        return "（未找到社交媒体内容）\n"

    lines = [f"共 {len(items)} 条内容\n", "=" * 50]

    for i, item in enumerate(items):
        time_str = item.get('time', '未知时间')
        lines.append(f"[{i+1}] {time_str}")

        if 'likes' in item:
            engagement = []
            if item.get('likes'):
                engagement.append(f"❤ {item['likes']}")
            if item.get('comments'):
                engagement.append(f"💬 {item['comments']}")
            if item.get('collected'):
                engagement.append(f"⭐ {item['collected']}")
            if engagement:
                lines.append(f"    {' · '.join(engagement)}")

        content = item.get('content', '').strip()
        lines.append(f"    {content[:500]}")
        if len(content) > 500:
            lines.append(f"    ...（省略 {len(content) - 500} 字）")

        if item.get('tags'):
            lines.append(f"    🏷  {', '.join(item['tags'])}")

        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='crush.skill 社交媒体解析器')
    parser.add_argument('--file', required=True, help='社交媒体导出文件路径')
    parser.add_argument('--platform', required=True,
                        choices=['weibo', 'xiaohongshu', 'instagram', 'text'],
                        help='社交媒体平台')
    parser.add_argument('--output', default=None, help='输出文件路径')
    parser.add_argument('--format', default='txt',
                        choices=['txt', 'json'], help='输出格式')

    args = parser.parse_args()

    platform_parsers = {
        'weibo': parse_weibo_json,
        'xiaohongshu': parse_xiaohongshu_json,
        'instagram': parse_instagram_json,
        'text': parse_text,
    }

    parse_fn = platform_parsers.get(args.platform, parse_text)
    items = parse_fn(args.file)

    if args.format == 'json':
        output = json.dumps(items, ensure_ascii=False, indent=2)
    else:
        output = format_output(items)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"已写入 {args.output}（{len(items)} 条内容）")
    else:
        print(output)


if __name__ == '__main__':
    main()
