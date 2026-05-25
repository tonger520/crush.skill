#!/usr/bin/env python3
"""
crush.skill — 用户沟通模式分析器
基于聊天记录分析用户自身的沟通行为模式。
"""

import argparse
import json
import sys
from collections import Counter


def analyze_user_messages(messages, user_name_hint=None):
    """
    分析用户自身的消息模式。
    messages: list of dicts with 'sender' and 'content'
    返回统计数据字典。
    """
    total = len(messages)
    if total == 0:
        return {'error': '无消息数据'}

    # 1. 基础统计
    msg_lengths = [len(m.get('content', '')) for m in messages]
    avg_length = sum(msg_lengths) / len(msg_lengths) if msg_lengths else 0

    # 长度分布
    short_msgs = sum(1 for l in msg_lengths if l < 10)
    medium_msgs = sum(1 for l in msg_lengths if 10 <= l <= 30)
    long_msgs = sum(1 for l in msg_lengths if l > 30)

    # 2. 高频词统计（简单中文分词前缀匹配）
    all_text = ' '.join(m.get('content', '') for m in messages)
    # 常见中文停用词
    stopwords = set('的了在是我有这和那他个们也到得地说要你去会能就那不一么为可以这个那个什么怎么一个如果但是因为所以已经还是只是没有或者可能不过虽然然后'.split())

    # 提取 2-6 字短语
    phrases = []
    for i in range(len(all_text)):
        for j in range(i+2, min(i+7, len(all_text)+1)):
            phrase = all_text[i:j].strip()
            if len(phrase) >= 2 and phrase not in stopwords and not phrase.isspace():
                phrases.append(phrase)

    phrase_counter = Counter(phrases)
    top_phrases = phrase_counter.most_common(20)

    # 3. emoji 统计
    emoji_count = sum(1 for m in messages for c in m.get('content', '')
                      if ord(c) > 0x1F600 or (0x2600 <= ord(c) <= 0x27BF))
    emoji_per_msg = round(emoji_count / total, 1) if total else 0

    # 4. 句式特征
    question_count = sum(1 for m in messages if ('?' in m.get('content', '') or '？' in m.get('content', '')))
    question_ratio = round(question_count / total * 100, 1) if total else 0

    exclamation_count = sum(1 for m in messages if ('!' in m.get('content', '') or '！' in m.get('content', '')))
    exclamation_ratio = round(exclamation_count / total * 100, 1) if total else 0

    haha_count = sum(1 for m in messages if '哈哈' in m.get('content', ''))
    haha_ratio = round(haha_count / total * 100, 1) if total else 0

    # 5. 消息长度中位数
    sorted_lengths = sorted(msg_lengths)
    median_length = sorted_lengths[len(sorted_lengths) // 2] if sorted_lengths else 0

    return {
        'total_messages': total,
        'avg_length': round(avg_length, 1),
        'median_length': median_length,
        'length_distribution': {
            'short': short_msgs,
            'medium': medium_msgs,
            'long': long_msgs
        },
        'emoji_per_msg': emoji_per_msg,
        'questions': {'count': question_count, 'ratio': question_ratio},
        'exclamations': {'count': exclamation_count, 'ratio': exclamation_ratio},
        'haha': {'count': haha_count, 'ratio': haha_ratio},
        'top_phrases': [{'phrase': p, 'count': c} for p, c in top_phrases[:10]],
    }


def compare_users(user_stats, crush_stats):
    """对比用户和 crush 的沟通风格差异"""
    if 'error' in user_stats or 'error' in crush_stats:
        return {'error': '数据不足，无法对比'}

    return {
        'length_ratio': round(user_stats['avg_length'] / crush_stats['avg_length'], 1) if crush_stats.get('avg_length') else 0,
        'msg_count_ratio': round(user_stats['total_messages'] / crush_stats['total_messages'], 1) if crush_stats.get('total_messages') else 0,
        'emoji_diff': round(user_stats['emoji_per_msg'] - crush_stats.get('emoji_per_msg', 0), 1),
        'verdict': []  # 适配性判断
    }


def main():
    parser = argparse.ArgumentParser(description='crush.skill 用户沟通分析器')
    parser.add_argument('--file', required=True, help='聊天记录 JSON 文件路径（由 chat_parser 生成）')
    parser.add_argument('--user-hint', default=None, help='用户在聊天记录中的昵称提示')
    parser.add_argument('--crush-file', default=None, help='TA 的消息 JSON 文件路径（用于对比）')
    parser.add_argument('--output', default=None, help='输出文件路径')
    parser.add_argument('--format', default='text', choices=['text', 'json'], help='输出格式')

    args = parser.parse_args()

    # 读取消息
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            all_messages = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError) as e:
        print(f"错误: 无法读取 {args.file}: {e}", file=sys.stderr)
        sys.exit(1)

    # 分析用户消息
    user_stats = analyze_user_messages(all_messages, args.user_hint)

    # 对比分析
    comparison = None
    if args.crush_file:
        try:
            with open(args.crush_file, 'r', encoding='utf-8') as f:
                crush_messages = json.load(f)
            crush_stats = analyze_user_messages(crush_messages)
            comparison = compare_users(user_stats, crush_stats)
        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError):
            comparison = {'error': 'TA的数据读取失败'}

    # 输出
    result = {
        'user_stats': user_stats,
        'comparison': comparison
    }

    if args.format == 'json':
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        lines = []
        lines.append("=" * 60)
        lines.append("  个人沟通风格分析")
        lines.append("=" * 60)
        lines.append(f"  消息总数：{user_stats.get('total_messages', 0)} 条")
        lines.append(f"  平均长度：{user_stats.get('avg_length', 0)} 字/条")
        lines.append(f"  中位长度：{user_stats.get('median_length', 0)} 字/条")
        lines.append(f"  短消息 (<10字)：{user_stats.get('length_distribution', {}).get('short', 0)} 条")
        lines.append(f"  中等消息 (10-30字)：{user_stats.get('length_distribution', {}).get('medium', 0)} 条")
        lines.append(f"  长消息 (>30字)：{user_stats.get('length_distribution', {}).get('long', 0)} 条")
        lines.append(f"  emoji密度：{user_stats.get('emoji_per_msg', 0)}/条")
        lines.append(f"  问句比例：{user_stats.get('questions', {}).get('ratio', 0)}%")
        lines.append(f"  感叹句比例：{user_stats.get('exclamations', {}).get('ratio', 0)}%")
        lines.append(f"  '哈哈'出现率：{user_stats.get('haha', {}).get('ratio', 0)}%")
        lines.append("")
        lines.append("  高频短语 TOP10：")
        for p in user_stats.get('top_phrases', [])[:10]:
            lines.append(f"    {p['phrase']} ({p['count']}次)")
        lines.append("")

        if comparison and 'error' not in comparison:
            lines.append("  vs TA 的对比：")
            lines.append(f"    消息长度比： {comparison['length_ratio']}:1")
            lines.append(f"    消息数量比： {comparison['msg_count_ratio']}:1")
        lines.append("=" * 60)

        output = '\n'.join(lines)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"已写入 {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
