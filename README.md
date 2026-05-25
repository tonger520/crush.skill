# crush.skill 💕

> *"TA 回消息了吗？没有。那如果我发这条呢？"*
>
> **不只分析 TA，也帮你认识自己。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

把暗恋对象的说话方式、性格特点、那些让你心跳加速的细节蒸馏成 AI Skill。同时也帮你看清自己的沟通模式——你在 TA 面前的优点、弱点和成长空间。

- 🧠 **语义理解引擎** — 7维度深度语义分析，读懂 TA 没说出口的话
- 📊 **信号分析** — 从聊天记录中提取暧昧信号，量化真相
- 🔮 **消息预测** — 发送前先看 TA 会怎么回
- 🌡️ **暧昧温度计** — 用数据告诉你进展到哪一步
- 💬 **模拟对话** — 像 TA 一样回复你，练习没说出口的话
- 📚 **仓库学习** — 从你的历史档案中学习，越用越懂你
- 🪞 **自我画像** — 不只分析 TA，也分析你自己

---

## 与前任.skill 的区别

| | 前任.skill | crush.skill |
|------|:---:|:---:|
| 关系状态 | 已结束 | 进行中/未开始 |
| 核心诉求 | 回忆、告别、疗愈 | 理解、预测、行动指导 |
| 语义理解 | 基础 | ✅ 7维度深度引擎 |
| 信号分析 | ❌ | ✅ 4维度评分 |
| 温度计 | ❌ | ✅ 0-100°C |
| 消息预测 | ❌ | ✅ 3概率预测 |
| 仓库学习 | ❌ | ✅ 跨档案模式挖掘 |
| 用户自画像 | ❌ | ✅ 沟通弱点诊断 |
| 告白/约会模拟 | ❌ | ✅ |
| 防沉迷 | 无 | ✅ |

---

## 安装

### Claude Code

```bash
# 安装到当前项目
mkdir -p .claude/skills
git clone https://github.com/tonger520/crush-skill .claude/skills/create-crush

# 或安装到全局
git clone https://github.com/tonger520/crush-skill ~/.claude/skills/create-crush
```

> **重要**：Claude Code 从 git 仓库根目录的 `.claude/skills/` 查找 skill。

### 依赖（可选）

```bash
pip3 install -r requirements.txt
```

---

## 使用

在 Claude Code 中输入：

```
/crush
```

### 管理命令

| 命令 | 说明 |
|------|------|
| `/crush` | 创建新 crush 档案 |
| `/list-crushes` | 列出所有 crush |
| `/{slug}` | 模拟对话 |
| `/{slug}-predict` | 消息预测引擎 |
| `/{slug}-signals` | 信号解读 |
| `/{slug}-temp` | 暧昧温度计 |
| `/{slug}-strategy` | 策略建议 |
| `/{slug}-persona` | 查看画像 |
| `/{slug}-progress` | 进展追踪 |
| `/me {slug}` | 自我反思（分析你的沟通模式） |
| `/crush-rollback {slug} {v}` | 回滚版本 |
| `/delete-crush {slug}` | 删除档案 |
| `/move-on {slug}` | 释然 |
| `/crush-learn` | 触发仓库学习 |
| `/warehouse-reset` | 清除仓库数据 |

### 支持的数据来源

| 来源 | 聊天 | 照片 | 社交 | 备注 |
|------|:---:|:---:|:---:|------|
| 微信 | ✅ | — | — | WechatExporter 导出 |
| iMessage | ✅ | — | — | macOS chat.db |
| 短信 | ✅ | — | — | XML/CSV |
| 微博 | — | — | ✅ | JSON |
| 小红书 | — | — | ✅ | JSON |
| Instagram | — | — | ✅ | JSON |
| 截屏/照片 | ✅ | ✅ | ✅ | 直接读取 |
| 粘贴文字 | ✅ | — | — | 手动输入 |
| 纯口述 | ✅ | — | — | 无需文件 |

---

## 效果示例

### 信号分析

```
📊 互动信号：
  主动性：6/10 — 每周主动 2-3 次
  回复质量：7/10 — 中快，30字/条
  暧昧信号：5/10 — 有深夜聊天

🌡️ 温度：52°C 🔥 暧昧期
```

### 消息预测

```
📨 你：周末有空吗？想约你喝杯咖啡

🔮 预测：
🟢 高概率 (55%)：「周末啊...我看看」
🟡 中概率 (30%)：「好啊！去哪？」
🔴 低概率 (15%)：「最近有点忙」

💡 建议：可以发，如果犹豫换更轻松的理由
```

### 自我反思

```
🪞 你的沟通画像：

💪 优势：你善于制造笑点，TA因为你笑得很多
⚠️ 注意：你的消息平均是TA的 3.2 倍长
📈 建议：缩减至 1.5 倍以内
```

---

## 生成的 Skill 结构

每个 crush Skill 由 4 部分组成：

| 部分 | 内容 |
|------|------|
| **Part A — 语义分析** | 7维语义引擎 |
| **Part B — 信号档案** | 4维度评分 + 温度 + 时间线 |
| **Part C — TA画像** | 5层：规则→身份→风格→节律→边界 |
| **Part D — 你** | 沟通画像 + 优势 + 弱点 + 建议 |

---

## 项目结构

```
crush-skill/
├── SKILL.md
├── prompts/
│   ├── intake.md               # 信息录入
│   ├── semantic_engine.md      # 语义理解引擎（7维）
│   ├── profile_analyzer.md     # TA 画像分析
│   ├── profile_builder.md      # TA 画像生成（5层）
│   ├── signal_analyzer.md      # 信号解读（4维+温度）
│   ├── predictor.md            # 消息预测引擎
│   ├── merger.md               # 增量合并
│   ├── correction_handler.md   # 对话纠正
│   ├── warehouse_learner.md    # 仓库知识学习
│   └── user_learner.md         # 用户自我学习
├── tools/
│   ├── chat_parser.py          # 聊天记录解析
│   ├── social_parser.py        # 社交媒体解析
│   ├── version_manager.py      # 版本管理
│   ├── skill_writer.py         # 文件管理+仓库导出
│   ├── temperature_calculator.py # 温度计算
│   └── user_analyzer.py        # 用户模式分析
├── crushes/                    # 生成档案（gitignored）
├── README.md
├── CHANGELOG.md
├── requirements.txt
└── LICENSE
```

---

## ⚠️ 安全边界

1. **仅用于个人情感分析** — 不用于骚扰、跟踪或侵犯他人隐私
2. **TA 是真实的人** — 不是攻略对象，有自己的选择
3. **标注不确定性** — 所有推断都标注置信度
4. **鼓励真实行动** — Skill 是军师，不是替身
5. **禁止操纵** — 不提供套路、PUA话术或操纵技巧
6. **防沉迷机制** — 反复纠结同一条消息时提醒你放下手机
7. **隐私保护** — 所有数据仅在本地处理，不上传任何外部服务

---

## 哲学

> **前任.skill 的终极目的是让你放下。**
> **crush.skill 的终极目的是给你勇气——看清局势后，做真实的自己。**
> **而认识你自己，是获得勇气的前提。**

---

## 作者

**GitHub**：[tonger520](https://github.com/tonger520)

## 开源声明

本项目为开源项目，仅供学习参考使用。请尊重每个人的知识产权。

如有侵权，请联系我，我将立即删除相关内容。

Copyright © 2025 tonger520. Released under the MIT License.
