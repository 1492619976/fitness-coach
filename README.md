# fitness-coach · 健身 AI 私教 skill（伤病改造版）

给 ZCode / Claude Code 类 agent 装的健身私教技能：按 4 分化课表给当日训练、做动作安全查询与替换、写训练记录、跑周日检查点评估。核心特色是**伤病安全门**——所有动作查询默认过禁令过滤（杠铃全禁 + 屈脊柱/跑跳/颈后等正则黑名单），被过滤的动作不许绕过。

## 功能

| 你说 | 它做 |
|------|------|
| 今天练什么 | 按星期给当日分化表（动作 + 组次 + 安全要点 + GIF 路径）；"这周只练 3 天"自动切 Push/Pull/腿 |
| 换个 XX 动作 | 先过伤病安全过滤，选定后**追加**进计划文件（不删旧行） |
| 这个动作怎么做 | 报数据集中文分步要点 + 一句安全提醒 |
| 记训练 | 写当日训练记录（只记口述的真实数据） |
| 称重 / 检查点 | 对照掉率规则给"继续 / 顺延"判断 |

## 安装

```bash
# 1. 放进 agent 的技能目录
cp -r fitness-coach ~/.agents/skills/

# 2. 下载动作数据集（1,324 动作 + GIF + 11 语言分步说明）
git clone https://github.com/hasaneyldrm/exercises-dataset ~/projects/exercises-dataset
```

然后改两处本机路径（都在 `scripts/query_dataset.py` 头部）：

- `DS`：数据集目录
- `PLAN`：你的训练计划 MD（本 skill 不复制课表内容，`--plan` 现场解析这份文件，改计划即生效，防漂移）

SKILL.md 顶部的身体约束（禁令清单 / RPE 帽 / 红旗症状）按自己情况改——那是私教的安全门，别删。

## 查询工具

```bash
python scripts/query_dataset.py --plan 周四          # 当日课表（周一/周二/周四/周六/康复）
python scripts/query_dataset.py 侧平举 --safe        # 关键词（中英文 + 健身行话自动映射英文动作名）
python scripts/query_dataset.py row --equipment 器械  # --target 部位 / --equipment 器材 过滤
python scripts/query_dataset.py --id 1318            # 直查动作 ID
python scripts/query_dataset.py 深蹲 --unsafe        # 查看被禁动作（仅用于解释为什么禁）
```

坑位提示：数据集的中文翻译是描述式的（"将手臂向两侧举起"），健身行话（"侧平举"）直搜搜不到，`GYM_MAP` 负责行话→英文映射，遇到新行话往里加。

## 声明

- 本 skill 是教练不是医生：新发疼痛 / 神经症状 → 转诊，不给替代方案
- 数据集动作图片与动画 © Gym visual（180×210 授权原样分发），本仓库**不含**任何媒体文件，仅含路径引用；数据层（名称/肌群/多语言步骤）MIT

## License

MIT（本仓库的 SKILL.md 与脚本）
