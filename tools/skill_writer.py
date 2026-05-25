#!/usr/bin/env python3
"""
crush.skill — Skill 文件管理器
支持列出、删除 crush Skill 以及生成 meta 信息。
"""

import argparse
import json
import os
import sys
from datetime import datetime


def list_crushes(base_dir='./crushes'):
    """列出所有 crush Skill"""
    if not os.path.exists(base_dir):
        print("还没有创建过任何 crush。")
        return []

    results = []
    for slug in os.listdir(base_dir):
        crush_dir = os.path.join(base_dir, slug)
        if not os.path.isdir(crush_dir):
            continue

        meta_path = os.path.join(crush_dir, 'meta.json')
        if not os.path.exists(meta_path):
            continue

        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except (json.JSONDecodeError, IOError):
            meta = {}

        results.append({
            'slug': slug,
            'name': meta.get('name', slug),
            'created_at': meta.get('created_at', ''),
            'version': meta.get('version', 'v1'),
            'temperature': meta.get('temperature', None),
            'impression': meta.get('impression', ''),
        })

    # 按创建时间倒序
    results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return results


def format_list(crushes):
    """格式化列表输出"""
    if not crushes:
        print("📭 还没有任何 crush。输入 /crush 来创建第一个吧。")
        return

    print(f"\n💕 你的 crush 档案（{len(crushes)} 个）：\n")

    for i, c in enumerate(crushes):
        temp_str = f" — 🔥 {c['temperature']}°C" if c.get('temperature') is not None else ""
        print(f"  [{i+1}] /{c['slug']}{temp_str}")
        print(f"       {c['name']} · {c.get('created_at', '')[:10]}{' · ' + c.get('version', '') if c.get('version') else ''}")
        if c.get('impression'):
            print(f"       「{c['impression'][:60]}」")
        print()


def delete_crush(slug, base_dir='./crushes'):
    """删除指定 crush Skill"""
    crush_dir = os.path.join(base_dir, slug)
    if not os.path.exists(crush_dir):
        print(f"错误: crush '{slug}' 不存在", file=sys.stderr)
        return False

    import shutil
    shutil.rmtree(crush_dir)
    print(f"✅ 已删除 {slug}")
    return True


def get_crush_info(slug, base_dir='./crushes'):
    """获取 crush 详细信息"""
    crush_dir = os.path.join(base_dir, slug)
    if not os.path.exists(crush_dir):
        return None

    meta_path = os.path.join(crush_dir, 'meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def export_warehouse_knowledge(base_dir='./crushes'):
    """导出匿名化的仓库知识，供语义学习和模式匹配使用"""
    warehouse_dir = os.path.join(base_dir, '.warehouse')
    os.makedirs(warehouse_dir, exist_ok=True)

    crushes = list_crushes(base_dir)
    knowledge = {
        'total_archives': len(crushes),
        'export_timestamp': datetime.now().isoformat(),
        'tag_patterns': {},
        'temperature_progressions': [],
        'signal_sequences': []
    }

    for c in crushes:
        slug = c['slug']
        crush_dir = os.path.join(base_dir, slug)

        # 读取 meta
        meta = get_crush_info(slug, base_dir)
        if not meta:
            continue

        # 匿名化：只提取模式，不保留身份
        tags_list = meta.get('tags', {})
        interaction_style = tags_list.get('interaction_style', [])
        signal_type = tags_list.get('signal_type', '')
        attachment = tags_list.get('attachment', '')

        # 记录标签共现
        for tag in interaction_style:
            knowledge['tag_patterns'].setdefault(tag, {
                'count': 0,
                'co_occurring_signals': [],
                'co_occurring_attachments': []
            })
            knowledge['tag_patterns'][tag]['count'] += 1
            if signal_type:
                knowledge['tag_patterns'][tag]['co_occurring_signals'].append(signal_type)
            if attachment:
                knowledge['tag_patterns'][tag]['co_occurring_attachments'].append(attachment)

        # 记录温度变化（如果有多个版本）
        temperature = meta.get('temperature')
        if temperature is not None:
            knowledge['temperature_progressions'].append({
                'final_temp': temperature,
                'interaction_style': interaction_style,
                'signal_type': signal_type
            })

    # 写入仓库文件
    warehouse_file = os.path.join(warehouse_dir, 'knowledge.json')
    with open(warehouse_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)

    return knowledge


def main():
    parser = argparse.ArgumentParser(description='crush.skill 文件管理器')
    parser.add_argument('--action', default='list',
                        choices=['list', 'delete', 'info', 'knowledge'],
                        help='操作类型')
    parser.add_argument('--slug', default=None, help='crush 标识')
    parser.add_argument('--base-dir', default='./crushes', help='基础目录')

    args = parser.parse_args()

    if args.action == 'list':
        crushes = list_crushes(args.base_dir)
        format_list(crushes)

    elif args.action == 'delete':
        if not args.slug:
            print("错误: delete 操作需要 --slug 参数", file=sys.stderr)
            sys.exit(1)
        delete_crush(args.slug, args.base_dir)

    elif args.action == 'info':
        if not args.slug:
            print("错误: info 操作需要 --slug 参数", file=sys.stderr)
            sys.exit(1)
        info = get_crush_info(args.slug, args.base_dir)
        if info:
            print(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            print(f"crush '{args.slug}' 不存在")

    elif args.action == 'knowledge':
        knowledge = export_warehouse_knowledge(args.base_dir)
        print(json.dumps(knowledge, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
