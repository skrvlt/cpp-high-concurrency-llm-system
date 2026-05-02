# 论文图表索引

本文核心图表已经随论文终稿化阶段生成，图像文件位于 `output/doc/figures/`，DOCX 由 `tools/generate_thesis_docx.py` 自动插入对应图题位置。

## 已生成图

| 图号 | 名称 | 文件 |
| --- | --- | --- |
| 图3-1 | 系统用例图 | `output/doc/figures/figure-3-1-use-case.png` |
| 图4-1 | 系统总体结构图 | `output/doc/figures/figure-4-1-architecture.png` |
| 图4-2 | 智能问答处理流程图 | `output/doc/figures/figure-4-2-chat-flow.png` |
| 图4-3 | 问答处理时序图 | `output/doc/figures/figure-4-3-sequence.png` |
| 图4-4 | 系统 E-R 图 | `output/doc/figures/figure-4-4-er.png` |

## 已整理表

| 表号 | 名称 | 章节 |
| --- | --- | --- |
| 表3-1 | 管理员核心功能说明 | 第3章 |
| 表4-1 | 用户表结构 | 第4章 |
| 表4-2 | 会话表结构 | 第4章 |
| 表4-3 | 消息表结构 | 第4章 |
| 表4-4 | 日志表结构 | 第4章 |
| 表6-1 | 用户登录测试用例表 | 第6章 |
| 表6-2 | 智能问答测试用例表 | 第6章 |
| 表6-3 | 管理员功能测试用例表 | 第6章 |
| 表6-4 | 并发性能测试结果表 | 第6章 |

## 生成命令

```powershell
& 'C:\Users\kidosto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\generate_thesis_figures.py
& 'C:\Users\kidosto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\generate_thesis_docx.py
```
