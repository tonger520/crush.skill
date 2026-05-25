#!/usr/bin/env python3
"""
crush.skill — 聊天记录解析器
支持微信/iMessage/短信/QQ的聊天记录导出文件解析。
"""

import argparse
import re
import json
import csv
import os
import sys
from datetime import datetime
from pathlib import Path


def parse_wechat_txt(filepath, target=None):
    """解析微信聊天记录 TXT 文件（WechatExporter 格式等）"""
    results = []
    # 多种时间格式
    patterns = [
        # 2024-01-15 22:30:45 发送人: 内容
        re.compile(r'^(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)\s+([^:]+?)[:：]\s*(.+)$'),
        # 2024/01/15 22:30 发送人: 内容
        re.compile(r'^(\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2})\s+([^:]+?)[:：]\s*(.+)$'),
        # 1/15 22:30 发送人: 内容
        re.compile(r'^(\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2})\s+([^:]+?)[:：]\s*(.+)$'),
    ]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='gbk') as f:
            lines = f.readlines()

    current_msg = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        matched = False
        for pat in patterns:
            m = pat.match(line)
            if m:
                if current_msg:
                    results.append(current_msg)
                time_str, sender, content = m.groups()
                current_msg = {
                    'time': time_str.strip(),
                    'sender': sender.strip(),
                    'content': content.strip()
                }
                matched = True
                break

        if not matched and current_msg:
            # 多行消息的续行
            current_msg['content'] += '\n' + line

    if current_msg:
        results.append(current_msg)

    # 如果指定了目标对象，筛选TA的消息
    if target:
        results = [m for m in results if target.lower() in m['sender'].lower()
                   or target in m['sender']]

    return results


def parse_wechat_html(filepath, target=None):
    """解析微信聊天记录 HTML 文件"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='gbk') as f:
            html = f.read()

    # 简单的 HTML 解析：提取时间、发送人和内容
    # 匹配常见格式的 HTML 聊天记录
    msg_pattern = re.compile(
        r'<div[^>]*class="[^"]*message[^"]*"[^>]*>.*?'
        r'(?:<[^>]*>)*(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?).*?'
        r'(?:<[^>]*>)*([^<]+?)[:：].*?'
        r'(?:<[^>]*>)*([^<]{1,500}?)'
        r'(?:</div>|</p>)',
        re.DOTALL | re.IGNORECASE
    )

    for m in msg_pattern.finditer(html):
        results.append({
            'time': m.group(1).strip(),
            'sender': m.group(2).strip(),
            'content': re.sub(r'<[^>]+>', '', m.group(3)).strip()
        })

    if target:
        results = [m for m in results if target.lower() in m['sender'].lower()
                   or target in m['sender']]

    return results


def parse_sms_xml(filepath, target=None):
    """解析 Android SMS Backup XML/CSV 导出"""
    results = []
    if filepath.endswith('.xml'):
        import xml.etree.ElementTree as ET
        tree = ET.parse(filepath)
        root = tree.getroot()
        for sms in root.findall('.//sms'):
            results.append({
                'time': sms.get('readable_date', sms.get('date', '')),
                'sender': sms.get('address', ''),
                'content': sms.get('body', '')
            })
    elif filepath.endswith('.csv'):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append({
                    'time': row.get('date', row.get('time', '')),
                    'sender': row.get('address', row.get('sender', '')),
                    'content': row.get('body', row.get('content', row.get('message', '')))
                })

    if target:
        results = [m for m in results if target.lower() in m['sender'].lower()
                   or target.replace('+', '') in m['sender'].replace('+', '')]

    return results


def parse_text(filepath):
    """直接读取任意文本文件"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='gbk') as f:
            content = f.read()

    results.append({
        'time': '',
        'sender': '',
        'content': content
    })
    return results


def parse_imessage_direct(target=None):
    """直接读取本机 iMessage chat.db（仅 macOS）"""
    import sqlite3
    import platform

    if platform.system() != 'Darwin':
        print("错误: --direct 仅支持 macOS", file=sys.stderr)
        return []

    db_path = os.path.expanduser('~/Library/Messages/chat.db')
    if not os.path.exists(db_path):
        print(f"错误: chat.db 不存在 ({db_path})", file=sys.stderr)
        print("请确保给终端/Claude Code 授予了 Full Disk Access 权限", file=sys.stderr)
        return []

    results = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
            SELECT
                datetime(message.date/1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime') as msg_time,
                handle.id as sender,
                message.text as content
            FROM message
            JOIN handle ON message.handle_id = handle.ROWID
            WHERE message.text IS NOT NULL
            ORDER BY message.date ASC
        """

        if target:
            query = """
                SELECT
                    datetime(message.date/1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime') as msg_time,
                    handle.id as sender,
                    message.text as content
                FROM message
                JOIN handle ON message.handle_id = handle.ROWID
                WHERE message.text IS NOT NULL
                AND (handle.id LIKE ? OR handle.id LIKE ?)
                ORDER BY message.date ASC
            """
            cursor.execute(query, (f'%{target}%', f'%{target.replace("+", "")}%'))
        else:
            cursor.execute(query)

        for row in cursor.fetchall():
            results.append({
                'time': row[0],
                'sender': row[1],
                'content': row[2] if row[2] else ''
            })

        conn.close()
    except sqlite3.Error as e:
        print(f"数据库读取错误: {e}", file=sys.stderr)
        print("可能需要授予终端 Full Disk Access 权限", file=sys.stderr)
        return []

    return results


def format_output(messages):
    """格式化输出为可读文本"""
    if not messages:
        return "（未找到消息记录）\n"

    lines = []
    lines.append(f"共 {len(messages)} 条消息\n")
    lines.append("=" * 50)

    for i, msg in enumerate(messages):
        lines.append(f"[{i+1}] {msg['time']} | {msg['sender']}")
        lines.append(f"    {msg['content']}")
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='crush.skill 聊天记录解析器')
    parser.add_argument('--platform', required=True,
                        choices=['wechat', 'imessage', 'sms', 'qq', 'auto'],
                        help='聊天平台')
    parser.add_argument('--file', help='聊天记录文件路径')
    parser.add_argument('--direct', action='store_true',
                        help='直接读取本机 iMessage chat.db（仅 macOS）')
    parser.add_argument('--target', default=None, help='目标对象名称/昵称')
    parser.add_argument('--output', default=None, help='输出文件路径')
    parser.add_argument('--format', default='txt',
                        choices=['txt', 'json'], help='输出格式')

    args = parser.parse_args()

    if not args.file and not args.direct:
        print("错误: 需要 --file 或 --direct 参数", file=sys.stderr)
        sys.exit(1)

    if args.file and not os.path.exists(args.file):
        print(f"错误: 文件不存在: {args.file}", file=sys.stderr)
        sys.exit(1)

    # 解析聊天记录
    messages = []
    file_ext = os.path.splitext(args.file)[1].lower() if args.file else ''

    if args.platform == 'imessage' and args.direct:
        messages = parse_imessage_direct(args.target)
    elif args.platform in ('wechat', 'auto'):
        if file_ext == '.html' or file_ext == '.htm':
            messages = parse_wechat_html(args.file, args.target)
        else:
            messages = parse_wechat_txt(args.file, args.target)
    elif args.platform in ('imessage',):
        messages = parse_wechat_txt(args.file, args.target)
    elif args.platform == 'sms':
        messages = parse_sms_xml(args.file, args.target)
    elif args.platform == 'qq':
        messages = parse_wechat_txt(args.file, args.target)

    # 输出
    if args.format == 'json':
        output = json.dumps(messages, ensure_ascii=False, indent=2)
    else:
        output = format_output(messages)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"已写入 {args.output}（{len(messages)} 条消息）")
    else:
        print(output)


if __name__ == '__main__':
    main()
