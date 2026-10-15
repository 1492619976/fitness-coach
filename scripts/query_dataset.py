# -*- coding: utf-8 -*-
"""exercises-dataset 查询工具（fitness-coach skill 专用）

数据:   D:/projects/exercises-dataset/data/exercises.json （1,324 动作，11 语言分步 + GIF）
权威计划: D:/knowledge/03-健身/训练计划/4分化训练计划.md （--plan 从这里读，不复制内容防漂移）

用法（python = C:/Users/14926/AppData/Local/Programs/Python/Python312/python.exe）:
  python query_dataset.py --plan 周四              # 打印当日分化表（周一/周二/周四/周六/康复）
  python query_dataset.py 侧平举 --safe            # 关键词查询（中英文均可；默认过伤病安全过滤）
  python query_dataset.py row --equipment 器械      # 加器材/部位过滤
  python query_dataset.py --id 1318                # 直查动作 ID（跳过安全过滤，供精确引用）
  python query_dataset.py 深蹲 --unsafe            # 查看被禁的动作（仅用于解释为什么禁）

中文参数映射:
  器材: 自重/哑铃/绳索/器械/史密斯/弹力带/壶铃
  部位: 胸/背/肩/二头/三头/臂/核心/腹/腿/臀/大腿/小腿/有氧

安全过滤的禁令清单与 4分化训练计划.md「伤病逻辑」表同步维护：
杠铃器械全禁 + 名字含硬拉/深蹲跳/跑跳/颈后/仰卧起坐/卷腹/奥林匹克提拉/直立划船/俯身/举腿/俄罗斯转体 等。
"""
import json, re, argparse

DS = "D:/projects/exercises-dataset"
PLAN = "D:/knowledge/03-健身/训练计划/4分化训练计划.md"
BAN = re.compile(
    r"deadlift|jump|burpee|run|sprint|behind.?the.?neck|good morning|sit-?up|crunch"
    r"|clean|snatch|jerk|upright row|bent.?over|toes.?to.?bar|leg raise|russian twist",
    re.I)
EQ_MAP = {"自重": "body weight", "体重": "body weight", "哑铃": "dumbbell", "绳索": "cable",
          "器械": "leverage machine", "史密斯": "smith machine", "弹力带": "band",
          "拉力带": "band", "壶铃": "kettlebell"}
TARGET_MAP = {"胸": ["pectorals"], "背": ["lats", "upper back", "traps"], "肩": ["delts"],
              "二头": ["biceps"], "三头": ["triceps"], "臂": ["biceps", "triceps", "forearms"],
              "核心": ["abs", "waist"], "腹": ["abs", "waist"],
              "腿": ["quads", "hamstrings", "glutes", "calves", "abductors", "adductors",
                     "lower legs", "upper legs"],
              "臀": ["glutes"], "大腿": ["quads", "hamstrings"], "小腿": ["calves", "lower legs"],
              "有氧": ["cardiovascular system"]}
# 健身行话 → 英文动作名片段（数据集中文翻译是描述式的，行话大概率搜不到，需映射）
GYM_MAP = {"侧平举": ["lateral raise"], "前平举": ["front raise"], "俯身": ["bent over"],
           "卧推": ["bench press"], "推举": ["shoulder press"], "划船": ["row"],
           "下拉": ["pulldown"], "引体": ["pull-up", "chin-up"], "弯举": ["curl"],
           "锤式": ["hammer"], "下压": ["pushdown"], "臂屈伸": ["dip"], "飞鸟": ["fly"],
           "夹胸": ["crossover", "cross-over"], "深蹲": ["squat"], "弓步": ["lunge"],
           "台阶": ["step-up"], "臀桥": ["glute bridge", "hip lift", "bridge"],
           "提踵": ["calf raise"], "平板": ["plank"], "侧桥": ["side bridge", "side plank"],
           "死虫": ["dead bug"], "鸟狗": ["bird dog"], "面拉": ["face pull"],
           "后束": ["rear delt", "reverse fly"], "耸肩": ["shrug"], "卷腹": ["crunch"],
           "仰卧起坐": ["sit-up"], "高脚杯": ["goblet"], "腿弯举": ["leg curl"],
           "腿屈伸": ["leg extension"], "腿举": ["leg press"], "帕洛夫": ["pallof"]}


def kw_variants(kw):
    """关键词扩展：原词 + 行话映射出的英文片段（行话本身也要试着搜中文步骤）"""
    v = [kw]
    for k, en in GYM_MAP.items():
        if kw and (k in kw or kw in k):
            v.extend(en)
    return v


def is_safe(x):
    if x["equipment"] == "barbell":
        return False
    return not BAN.search(x["name"])


def show(x):
    steps = (x.get("instruction_steps") or {}).get("zh") or []
    print(f"#{x['id']} {x['name']}  [{x['equipment']}] 目标:{x.get('target','')} 肌群:{x.get('muscle_group','')}")
    print(f"   GIF: file:///{DS}/{x['gif_url']}")
    for i, s in enumerate(steps[:3], 1):
        print(f"   {i}. {s}")
    print()


def do_plan(day):
    text = open(PLAN, encoding="utf-8").read()
    m = re.search(r"^### " + day + r".*?(?=^### |^## |\Z)", text, re.M | re.S)
    print(m.group(0).strip() if m else f"计划里没有「{day}」小节（可用：周一/周二/周四/周六/康复）")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("keyword", nargs="?", default="")
    ap.add_argument("--plan"); ap.add_argument("--id")
    ap.add_argument("--target"); ap.add_argument("--equipment")
    ap.add_argument("--safe", action="store_true", help="伤病安全过滤（默认已开启，可显式传入）")
    ap.add_argument("--unsafe", action="store_true")
    ap.add_argument("--limit", type=int, default=8)
    a = ap.parse_args()
    if a.plan:
        return do_plan(a.plan)
    d = json.load(open(DS + "/data/exercises.json", encoding="utf-8"))
    if a.id:
        x = next((e for e in d if e["id"] == a.id), None)
        return show(x) if x else print("无此 ID")
    eq = EQ_MAP.get(a.equipment, a.equipment)
    tg = TARGET_MAP.get(a.target, [])
    hits = []
    kws = kw_variants(a.keyword) if a.keyword else []
    for x in d:
        if kws:
            zh = " ".join((x.get("instruction_steps") or {}).get("zh") or [])
            nm = x["name"].lower()
            if not any(k.lower() in nm or k in zh for k in kws):
                continue
        if eq and eq not in (x["equipment"] or ""):
            continue
        if tg and x.get("target", "") not in tg:
            continue
        if not a.unsafe and not is_safe(x):
            continue
        hits.append(x)
    if not hits:
        return print("没有命中：试试去掉 --target/--equipment，或 --unsafe 查看被禁动作")
    for x in hits[:a.limit]:
        show(x)
    print(f"-- 共 {len(hits)} 条，显示前 {min(a.limit, len(hits))}（--limit 调整；--unsafe 查禁动作）")


if __name__ == "__main__":
    main()
