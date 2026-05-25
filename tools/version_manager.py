#!/usr/bin/env python3
"""
crush.skill — 版本管理器
支持 Skill 文件的版本存档、回滚和历史查询。
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def get_version_dir(slug, base_dir='./crushes'):
    """获取版本存档目录"""
    return os.path.join(base_dir, slug, 'versions')


def get_next_version(slug, base_dir='./crushes'):
    """获取下一个版本号"""
    version_dir = get_version_dir(slug, base_dir)
    if not os.path.exists(version_dir):
        return 'v1'

    existing = [d for d in os.listdir(version_dir)
                if os.path.isdir(os.path.join(version_dir, d)) and d.startswith('v')]
    if not existing:
        return 'v1'

    # 提取版本号并找到最大值
    versions = []
    for v in existing:
        try:
            versions.append(int(v[1:]))
        except ValueError:
            continue

    return f'v{max(versions) + 1}' if versions else 'v1'


def backup(slug, base_dir='./crushes'):
    """备份当前版本"""
    crush_dir = os.path.join(base_dir, slug)
    if not os.path.exists(crush_dir):
        print(f"错误: crush '{slug}' 不存在", file=sys.stderr)
        return False

    version = get_next_version(slug, base_dir)
    version_dir = os.path.join(get_version_dir(slug, base_dir), version)
    os.makedirs(version_dir, exist_ok=True)

    # 备份所有 markdown 文件和 meta.json
    files_to_backup = ['profile.md', 'signals.md', 'SKILL.md', 'meta.json']
    backed_up = []
    for fname in files_to_backup:
        src = os.path.join(crush_dir, fname)
        if os.path.exists(src):
            dst = os.path.join(version_dir, fname)
            shutil.copy2(src, dst)
            backed_up.append(fname)

    # 写入版本元信息
    version_meta = {
        'version': version,
        'timestamp': datetime.now().isoformat(),
        'files': backed_up
    }
    with open(os.path.join(version_dir, 'version_meta.json'), 'w', encoding='utf-8') as f:
        json.dump(version_meta, f, ensure_ascii=False, indent=2)

    print(f"✅ 已备份到 {version_dir}（{version}）")
    return True


def rollback(slug, target_version, base_dir='./crushes'):
    """回滚到指定版本"""
    crush_dir = os.path.join(base_dir, slug)
    if not os.path.exists(crush_dir):
        print(f"错误: crush '{slug}' 不存在", file=sys.stderr)
        return False

    version_dir = os.path.join(get_version_dir(slug, base_dir), target_version)
    if not os.path.exists(version_dir):
        print(f"错误: 版本 '{target_version}' 不存在", file=sys.stderr)
        return False

    # 先备份当前版本
    backup(slug, base_dir)

    # 恢复目标版本的文件
    files_to_restore = ['profile.md', 'signals.md', 'SKILL.md', 'meta.json']
    restored = []
    for fname in files_to_restore:
        src = os.path.join(version_dir, fname)
        if os.path.exists(src):
            dst = os.path.join(crush_dir, fname)
            shutil.copy2(src, dst)
            restored.append(fname)

    # 更新 meta.json 的版本信息
    meta_path = os.path.join(crush_dir, 'meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta['updated_at'] = datetime.now().isoformat()
        meta['rolled_back_to'] = target_version
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"✅ 已回滚到 {target_version}（恢复文件: {', '.join(restored)}）")
    return True


def list_versions(slug, base_dir='./crushes'):
    """列出版本历史"""
    version_dir = get_version_dir(slug, base_dir)
    if not os.path.exists(version_dir):
        return []

    versions = sorted(
        [d for d in os.listdir(version_dir)
         if os.path.isdir(os.path.join(version_dir, d)) and d.startswith('v')],
        key=lambda x: int(x[1:]) if x[1:].isdigit() else 0,
        reverse=True
    )

    result = []
    for v in versions:
        meta_file = os.path.join(version_dir, v, 'version_meta.json')
        if os.path.exists(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as f:
                vm = json.load(f)
            result.append({
                'version': v,
                'timestamp': vm.get('timestamp', ''),
                'files': vm.get('files', [])
            })
        else:
            result.append({'version': v, 'timestamp': '', 'files': []})

    return result


def main():
    parser = argparse.ArgumentParser(description='crush.skill 版本管理器')
    parser.add_argument('--action', required=True,
                        choices=['backup', 'rollback', 'list'],
                        help='操作类型')
    parser.add_argument('--slug', required=True, help='crush 标识')
    parser.add_argument('--version', default=None, help='目标版本号（rollback 操作需要）')
    parser.add_argument('--base-dir', default='./crushes', help='基础目录')

    args = parser.parse_args()

    if args.action == 'backup':
        backup(args.slug, args.base_dir)
    elif args.action == 'rollback':
        if not args.version:
            print("错误: rollback 操作需要 --version 参数", file=sys.stderr)
            sys.exit(1)
        rollback(args.slug, args.version, args.base_dir)
    elif args.action == 'list':
        versions = list_versions(args.slug, args.base_dir)
        if versions:
            print(f"\n{args.slug} 版本历史：\n")
            for v in versions:
                print(f"  📦 {v['version']} — {v['timestamp']}")
                if v['files']:
                    print(f"     文件: {', '.join(v['files'])}")
        else:
            print(f"{args.slug} 暂无版本历史")


if __name__ == '__main__':
    main()
