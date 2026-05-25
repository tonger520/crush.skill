#!/usr/bin/env python3
"""
crush.skill — 暧昧温度计算器
基于信号分析结果计算暧昧温度，并输出评估报告。
"""

import argparse
import json
import sys


def calculate_temperature(activity_score, quality_score, signal_score, invite_score):
    """
    计算暧昧温度。

    公式:
    温度 = (activity × 0.25 + quality × 0.25 + signal × 0.30 + invite × 0.20) × 10

    每个维度满分 10 分，加权后乘以 10 得到 0-100 分。
    """
    weighted = (
        activity_score * 0.25 +
        quality_score * 0.25 +
        signal_score * 0.30 +
        invite_score * 0.20
    )
    temperature = round(weighted * 10, 1)
    return temperature


def get_temperature_level(temp):
    """获取温度等级"""
    if temp < 15:
        return {
            'level': '冰冻期',
            'emoji': '❄️',
            'description': '基本无互动，或者纯礼貌性往来',
            'suggestion': '先建立基本互动，不要急于表现喜欢'
        }
    elif temp < 30:
        return {
            'level': '常温期',
            'emoji': '🧊',
            'description': '普通朋友/同事关系，没有特别的暧昧信号',
            'suggestion': '多创造轻松自然的互动机会，不要过早暴露意图'
        }
    elif temp < 45:
        return {
            'level': '微温期',
            'emoji': '🌡️',
            'description': '开始有零星信号，一方或双方在试探阶段',
            'suggestion': '捕捉TA的回应信号，适当增加互动深度'
        }
    elif temp < 60:
        return {
            'level': '暧昧期',
            'emoji': '🔥',
            'description': '双方有明显信号交换，经常聊天，有专属互动方式',
            'suggestion': '可以尝试模糊邀约，观察反应再决定下一步'
        }
    elif temp < 75:
        return {
            'level': '升温期',
            'emoji': '💕',
            'description': '高度暧昧，只差一层窗户纸',
            'suggestion': '主动权在你手里了，选一个合适的时机推进'
        }
    elif temp < 90:
        return {
            'level': '沸腾期',
            'emoji': '❤️‍🔥',
            'description': '就差告白了，或者已经在约会边缘',
            'suggestion': '勇敢一点。TA在等你开口。'
        }
    else:
        return {
            'level': '临界点',
            'emoji': '💍',
            'description': '万事俱备，只差一句"我们在一起吧"',
            'suggestion': '不要再分析了。关掉这个工具，去找TA。'
        }


def analyze_confidence(scores_dict):
    """评估整体置信度"""
    # 计算有多少维度是用户提供的（满分）vs 零分（无数据）
    provided_dims = sum(1 for v in scores_dict.values() if v > 0)
    total_dims = len(scores_dict)

    if provided_dims >= total_dims:
        return '高 — 所有维度均有数据支撑'
    elif provided_dims >= total_dims / 2:
        return '中 — 部分维度数据不足，温度可能存在偏差'
    elif provided_dims >= 1:
        return '低 — 多数维度数据不足，温度仅供参考'
    else:
        return '极低 — 无任何数据，无法计算有效温度'


def generate_report(scores, temperature, level_info, confidence):
    """生成温度评估报告"""
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append(f"  🔥 暧昧温度报告")
    lines.append("=" * 60)
    lines.append("")

    # 各维度分数
    lines.append("📊 各维度评分：")
    lines.append(f"  主动性：  {'█' * int(scores['activity'])}{'░' * (10 - int(scores['activity']))} {scores['activity']}/10")
    lines.append(f"  回复质量：{'█' * int(scores['quality'])}{'░' * (10 - int(scores['quality']))} {scores['quality']}/10")
    lines.append(f"  暧昧信号：{'█' * int(scores['signal'])}{'░' * (10 - int(scores['signal']))} {scores['signal']}/10")
    lines.append(f"  邀约信号：{'█' * int(scores['invite'])}{'░' * (10 - int(scores['invite']))} {scores['invite']}/10")
    lines.append("")

    # 温度
    temp_bar_length = min(int(temperature / 5), 20)
    temp_bar = '█' * temp_bar_length + '░' * (20 - temp_bar_length)
    lines.append(f"🌡️  暧昧温度：{temperature}°C  [{temp_bar}]")
    lines.append(f"   {level_info['emoji']} {level_info['level']} — {level_info['description']}")
    lines.append("")

    # 置信度
    lines.append(f"📋 置信度：{confidence}")
    lines.append("")

    # 建议
    lines.append(f"💡 建议：{level_info['suggestion']}")
    lines.append("=" * 60)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='crush.skill 暧昧温度计算器')
    parser.add_argument('--activity', type=float, default=0,
                        help='主动性评分 (0-10)')
    parser.add_argument('--quality', type=float, default=0,
                        help='回复质量评分 (0-10)')
    parser.add_argument('--signal', type=float, default=0,
                        help='暧昧信号评分 (0-10)')
    parser.add_argument('--invite', type=float, default=0,
                        help='邀约信号评分 (0-10)')
    parser.add_argument('--from-signals', default=None,
                        help='从 signals.md 提取评分（路径）')
    parser.add_argument('--output', default=None, help='输出文件路径')
    parser.add_argument('--format', default='text',
                        choices=['text', 'json'], help='输出格式')

    args = parser.parse_args()

    scores = {
        'activity': args.activity,
        'quality': args.quality,
        'signal': args.signal,
        'invite': args.invite,
    }

    temperature = calculate_temperature(
        scores['activity'], scores['quality'],
        scores['signal'], scores['invite']
    )

    level_info = get_temperature_level(temperature)
    confidence = analyze_confidence(scores)

    output_format = args.format

    if output_format == 'json':
        result = {
            'temperature': temperature,
            'level': level_info['level'],
            'emoji': level_info['emoji'],
            'description': level_info['description'],
            'suggestion': level_info['suggestion'],
            'scores': scores,
            'confidence': confidence
        }
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        output = generate_report(scores, temperature, level_info, confidence)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"已写入 {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
