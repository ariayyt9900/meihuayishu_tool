# -*- coding: utf-8 -*-
"""
梅花易数 · 寻物快速查询（主卦/变卦/互卦/体用/方位与位置提示）
- 三数起卦：上卦=第1数，下卦=第2数，动爻=第3数
- 年月日时起卦（农历）：上=(年支+月+日)%8，下=(年支+月+日+时支)%8，动=(年支+月+日+时支)%6
  取余规则：余0按8或6论

用法：直接运行 main()，按提示输入即可。
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional

# 1..8 对应：乾兑离震巽坎艮坤（与你截图一致）
TRIGRAM_ORDER = [None, "乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]

EARTHLY_BRANCH_NUM = {
    "子": 1, "丑": 2, "寅": 3, "卯": 4, "辰": 5, "巳": 6,
    "午": 7, "未": 8, "申": 9, "酉": 10, "戌": 11, "亥": 12
}

# 八卦三爻（自下而上），阳=1 阴=0；用于推变卦/互卦
TRIGRAM_BITS = {
    1: 0b111,  # 乾 ☰
    2: 0b110,  # 兑 ☱
    3: 0b101,  # 离 ☲
    4: 0b100,  # 震 ☳
    5: 0b011,  # 巽 ☴
    6: 0b010,  # 坎 ☵
    7: 0b001,  # 艮 ☶
    8: 0b000,  # 坤 ☷
}
BITS_TO_TRIGRAM = {v: k for k, v in TRIGRAM_BITS.items()}

@dataclass(frozen=True)
class TrigramInfo:
    name: str
    element: str
    direction: str
    keywords: str
    places: str

# 典型“寻物落点”速查（够用版；你可按师傅资料继续扩充）
TRIGRAM_INFO: Dict[int, TrigramInfo] = {
    1: TrigramInfo("乾", "金", "西北", "高、硬、圆、金属、权证", "高处/柜顶/书架上层/金属盒/证件夹/电脑包"),
    2: TrigramInfo("兑", "金", "正西", "口、开口、缺口、夹具、票据", "开口处/抽屉口/夹层/文件夹口/收纳盒开口"),
    3: TrigramInfo("离", "火", "正南", "明、光、热、电、纸文", "灯下/窗边/桌面明处/充电区/打印区/书本纸张处"),
    4: TrigramInfo("震", "木", "正东", "动、门、出入、震动", "门口动线/玄关/出入处/你走动时放过的位置"),
    5: TrigramInfo("巽", "木", "东南", "入、缝、渗透、绳、细长", "缝隙/夹缝/袋中袋/抽屉边/沙发缝/床缝"),
    6: TrigramInfo("坎", "水", "正北", "陷、隐、液体、深处", "低处/角落深处/桶盆旁/洗手间/厨房水槽附近"),
    7: TrigramInfo("艮", "土", "东北", "止、角、门槛、柜、墙", "墙角/柜子/门背后/台阶边/收纳最里面"),
    8: TrigramInfo("坤", "土", "西南", "地、低、柔、布、收纳", "地面附近/床上被褥/衣物堆/袋底/抽屉最底层"),
}

# 64卦：上卦为行，下卦为列（顺序：乾兑离震巽坎艮坤）
HEXAGRAM_TABLE = [
    #      乾        兑        离        震        巽        坎        艮        坤
    ["乾为天","天泽履","天火同人","天雷无妄","天风姤","天水讼","天山遁","天地否"],      # 乾
    ["泽天夬","兑为泽","泽火革","泽雷随","泽风大过","泽水困","泽山咸","泽地萃"],      # 兑
    ["火天大有","火泽睽","离为火","火雷噬嗑","火风鼎","火水未济","火山旅","火地晋"],  # 离
    ["雷天大壮","雷泽归妹","雷火丰","震为雷","雷风恒","雷水解","雷山小过","雷地豫"],  # 震
    ["风天小畜","风泽中孚","风火家人","风雷益","巽为风","风水涣","风山渐","风地观"],  # 巽
    ["水天需","水泽节","水火既济","水雷屯","水风井","坎为水","水山蹇","水地比"],      # 坎
    ["山天大畜","山泽损","山火贲","山雷颐","山风蛊","山水蒙","艮为山","山地剥"],      # 艮
    ["地天泰","地泽临","地火明夷","地雷复","地风升","地水师","地山谦","坤为地"],      # 坤
]

# 五行生克
GEN = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
KE  = {"木":"土","土":"水","水":"火","火":"金","金":"木"}

def mod_as(n: int, m: int) -> int:
    r = n % m
    return m if r == 0 else r

def hexagram_name(upper: int, lower: int) -> str:
    # upper/lower: 1..8, 顺序：乾兑离震巽坎艮坤
    row = upper - 1
    col = lower - 1
    return HEXAGRAM_TABLE[row][col]

def build_hex_bits(upper: int, lower: int) -> int:
    # 6-bit: lower in bits0-2, upper in bits3-5
    return (TRIGRAM_BITS[upper] << 3) | TRIGRAM_BITS[lower]

def bits_to_trigrams(hex_bits: int) -> Tuple[int, int]:
    lower_bits = hex_bits & 0b111
    upper_bits = (hex_bits >> 3) & 0b111
    return BITS_TO_TRIGRAM[upper_bits], BITS_TO_TRIGRAM[lower_bits]

def flip_line(hex_bits: int, moving_line: int) -> int:
    # moving_line: 1(bottom) .. 6(top)
    bitpos = moving_line - 1
    return hex_bits ^ (1 << bitpos)

def mutual_hexagram(upper: int, lower: int) -> Tuple[int, int, str]:
    """
    互卦：下互=2-3-4爻，上互=3-4-5爻（自下而上计爻）
    """
    hb = build_hex_bits(upper, lower)
    # 取第2~5爻：4位窗口
    # 爻位：1..6 => bit0..bit5
    # 下互：bit1,bit2,bit3
    low_mut = ((hb >> 1) & 0b1) | (((hb >> 2) & 0b1) << 1) | (((hb >> 3) & 0b1) << 2)
    up_mut  = ((hb >> 2) & 0b1) | (((hb >> 3) & 0b1) << 1) | (((hb >> 4) & 0b1) << 2)
    up_tri = BITS_TO_TRIGRAM[up_mut]
    low_tri = BITS_TO_TRIGRAM[low_mut]
    return up_tri, low_tri, hexagram_name(up_tri, low_tri)

def element_relation(body_el: str, use_el: str) -> str:
    if body_el == use_el:
        return "体用同五行（平）"
    if GEN[body_el] == use_el:
        return "体生用（我耗气，偏费力）"
    if GEN[use_el] == body_el:
        return "用生体（外助我，偏有利）"
    if KE[body_el] == use_el:
        return "体克用（我能掌控，偏可得）"
    if KE[use_el] == body_el:
        return "用克体（外压我，偏难得）"
    return "关系未判定"

def level_hint(moving_line: int) -> str:
    if moving_line in (1,2):
        return "低处/地面/袋底/抽屉底层/床沿下/沙发下"
    if moving_line in (3,4):
        return "中层/桌面高度/柜中层/沙发座面/床面附近"
    return "高处/上层/挂起衣物口袋/书架上层/柜顶"

def find_hint(upper: int, lower: int, moving_line: int, changed_upper: int, changed_lower: int) -> str:
    """
    寻物实操提示（简化可用版）：
    - 以内卦为体（你），外卦为用（物/环境）
    - 方位：优先取“用卦方位”，辅以“变卦用卦方位”（如果不同，代表偏移/移动趋势）
    - 高度层级：由动爻给
    """
    body = TRIGRAM_INFO[lower]
    use  = TRIGRAM_INFO[upper]
    use2 = TRIGRAM_INFO[changed_upper]
    rel = element_relation(body.element, use.element)

    dir_primary = use.direction
    dir_secondary = use2.direction if use2.direction != use.direction else None

    parts = []
    parts.append(f"体(你/主体)=下卦{body.name}({body.element} {body.direction})；用(物/环境)=上卦{use.name}({use.element} {use.direction})")
    parts.append(f"体用五行：{rel}")
    parts.append(f"优先方位：{dir_primary}" + (f"；次选方位：{dir_secondary}" if dir_secondary else ""))
    parts.append(f"高度层级（按动爻{moving_line}）：{level_hint(moving_line)}")
    parts.append(f"用卦落点关键词：{use.places}")
    if dir_secondary:
        parts.append(f"变卦用卦落点关键词：{use2.places}（若主方位无果，再按此方位扩展）")
    # 动爻在内外卦
    if moving_line >= 4:
        parts.append("动爻在外卦：更像环境/容器/他人挪动导致，需要按“场景动线”搜。")
    else:
        parts.append("动爻在内卦：更像你自己收纳/夹层/叠放导致，按“个人物品系统”搜。")
    return "\n".join(parts)

def cast_three_numbers(n1: int, n2: int, n3: int) -> Tuple[int,int,int]:
    upper = mod_as(n1, 8)
    lower = mod_as(n2, 8)
    moving = mod_as(n3, 6)
    return upper, lower, moving

def cast_lunar_ymdh(year_branch: int, lunar_month: int, lunar_day: int, hour_branch: int) -> Tuple[int,int,int]:
    s1 = year_branch + lunar_month + lunar_day
    s2 = s1 + hour_branch
    upper = mod_as(s1, 8)
    lower = mod_as(s2, 8)
    moving = mod_as(s2, 6)
    return upper, lower, moving

def report(upper: int, lower: int, moving: int) -> str:
    main = hexagram_name(upper, lower)
    hb = build_hex_bits(upper, lower)
    changed_bits = flip_line(hb, moving)
    ch_upper, ch_lower = bits_to_trigrams(changed_bits)
    changed = hexagram_name(ch_upper, ch_lower)

    mu_upper, mu_lower, mutual = mutual_hexagram(upper, lower)

    out = []
    out.append("=== 起卦结果 ===")
    out.append(f"上卦：{TRIGRAM_ORDER[upper]}（{TRIGRAM_INFO[upper].element} {TRIGRAM_INFO[upper].direction}）")
    out.append(f"下卦：{TRIGRAM_ORDER[lower]}（{TRIGRAM_INFO[lower].element} {TRIGRAM_INFO[lower].direction}）")
    out.append(f"动爻：{moving}爻")
    out.append("")
    out.append("=== 卦名 ===")
    out.append(f"主卦：{main}")
    out.append(f"变卦：{changed}")
    out.append(f"互卦：{mutual}（上互{TRIGRAM_ORDER[mu_upper]} 下互{TRIGRAM_ORDER[mu_lower]}）")
    out.append("")
    out.append("=== 寻物提示（可执行） ===")
    out.append(find_hint(upper, lower, moving, ch_upper, ch_lower))
    return "\n".join(out)

def parse_branch(s: str) -> int:
    s = s.strip()
    if s.isdigit():
        v = int(s)
        if 1 <= v <= 12:
            return v
        raise ValueError("地支数必须在1..12")
    if s in EARTHLY_BRANCH_NUM:
        return EARTHLY_BRANCH_NUM[s]
    raise ValueError("请输入地支：子丑寅卯辰巳午未申酉戌亥 或 1..12")

def main():
    print("梅花易数·寻物快速查询")
    print("模式1：三数起卦（n1 n2 n3）")
    print("模式2：农历年月日时起卦（年支 月 日 时支）")
    mode = input("请选择模式(1/2)：").strip()

    if mode == "1":
        n1 = int(input("输入第1数（上卦）：").strip())
        n2 = int(input("输入第2数（下卦）：").strip())
        n3 = int(input("输入第3数（动爻）：").strip())
        u, l, m = cast_three_numbers(n1, n2, n3)
        print()
        print(report(u, l, m))
        return

    if mode == "2":
        yb = parse_branch(input("输入年支（如‘巳’或数字6）："))
        lm = int(input("输入农历月（1-12）：").strip())
        ld = int(input("输入农历日（1-30）：").strip())
        hb = parse_branch(input("输入时支（如‘未’或数字8）："))
        u, l, m = cast_lunar_ymdh(yb, lm, ld, hb)
        print()
        print(report(u, l, m))
        return

    print("模式输入错误，只能是1或2。")

if __name__ == "__main__":
    main()
