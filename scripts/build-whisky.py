from html import escape
from html.parser import HTMLParser
from pathlib import Path
import json
import math
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "whisky"
DIST = ROOT / "dist"
ORIGIN = "https://www.rockbarfxxkup.com"

LANGUAGES = [
    {"code": "en", "folder": "", "file": "whisky-inventory.md", "title_prefix": "Page title: ", "description_prefix": "Page description: "},
    {"code": "ja", "folder": "ja", "file": "whisky-inventory-ja.md", "title_prefix": "ページタイトル案：", "description_prefix": "ページ紹介文案："},
    {"code": "ko", "folder": "ko", "file": "whisky-inventory-ko.md", "title_prefix": "페이지 제목 제안: ", "description_prefix": "페이지 소개 문구 제안: "},
    {"code": "th", "folder": "th", "file": "whisky-inventory-th.md", "title_prefix": "ชื่อหน้าแนะนำ: ", "description_prefix": "ข้อความแนะนำหน้า: "},
    {"code": "zh-Hans", "folder": "zh-hans", "file": "whisky-inventory-zh-hans.md", "title_prefix": "页面标题建议：", "description_prefix": "页面简介建议："},
]
ACTIVE_LANGUAGES = LANGUAGES

# Owner-approved category copy; every active language must be complete.
CATEGORY_GUIDE = json.loads((SOURCE / "category-guide.json").read_text(encoding="utf-8"))

LABELS = {
    "en": {"home": "Home", "drinks": "Drinks", "find": "Find us", "language": "Language", "languages": "Website language", "search": "Search whiskies", "placeholder": "Search bottle names or styles", "category": "Category", "all": "All categories", "all_count": "All categories", "clear": "Clear", "count": "results", "no_results": "No whiskies match that search.", "notes": "Menu notes", "area": "WHISKY / MENU", "privacy": "Privacy policy", "directions": "Get directions", "instagram": "Instagram", "full_menu": "Full drinks menu", "availability": "Selection and availability can change."},
    "ja": {"home": "ホーム", "drinks": "ドリンク", "find": "アクセス", "language": "言語", "languages": "ウェブサイトの言語", "search": "ウイスキーを検索", "placeholder": "銘柄やタイプで検索", "category": "カテゴリー", "all": "すべてのカテゴリー", "all_count": "すべてのカテゴリー（{count}銘柄）", "clear": "クリア", "count": "件", "no_results": "該当するウイスキーがありません。", "notes": "メニュー情報の確認事項", "area": "ウイスキー / メニュー", "privacy": "プライバシーポリシー", "directions": "アクセス", "instagram": "Instagram", "full_menu": "ドリンク全メニュー", "availability": "銘柄と在庫状況は変更されることがあります。"},
    "ko": {"home": "홈", "drinks": "음료", "find": "오시는 길", "language": "언어", "languages": "웹사이트 언어", "search": "위스키 검색", "placeholder": "이름이나 종류로 검색", "category": "분류", "all": "전체 분류", "all_count": "전체 분류 ({count}종)", "clear": "지우기", "count": "개", "no_results": "검색 결과가 없습니다.", "notes": "메뉴 데이터 확인 사항", "area": "위스키 / 메뉴", "privacy": "개인정보 처리방침", "directions": "오시는 길", "instagram": "Instagram", "full_menu": "전체 음료 메뉴", "availability": "메뉴 구성과 재고는 변경될 수 있습니다."},
    "th": {"home": "หน้าแรก", "drinks": "เครื่องดื่ม", "find": "เส้นทาง", "language": "ภาษา", "languages": "ภาษาเว็บไซต์", "search": "ค้นหาวิสกี้", "placeholder": "ค้นหาตามชื่อหรือประเภท", "category": "หมวดหมู่", "all": "ทุกหมวดหมู่", "all_count": "ทุกหมวดหมู่ ({count} รายการ)", "clear": "ล้าง", "count": "รายการ", "no_results": "ไม่พบวิสกี้ที่ตรงกับการค้นหา", "notes": "หมายเหตุเกี่ยวกับข้อมูลเมนู", "area": "วิสกี้ / เมนู", "privacy": "นโยบายความเป็นส่วนตัว", "directions": "เส้นทาง", "instagram": "Instagram", "full_menu": "เมนูเครื่องดื่มทั้งหมด", "availability": "รายการและสินค้าที่มีจำหน่ายอาจเปลี่ยนแปลงได้"},
    "zh-Hans": {"home": "首页", "drinks": "饮品", "find": "到店路线", "language": "语言", "languages": "网站语言", "search": "搜索威士忌", "placeholder": "按酒款或类型搜索", "category": "分类", "all": "所有分类", "all_count": "所有分类（{count}款）", "clear": "清除", "count": "项", "no_results": "没有找到匹配的威士忌。", "notes": "菜单数据备注", "area": "威士忌 / 酒单", "privacy": "隐私政策", "directions": "到店路线", "instagram": "Instagram", "full_menu": "完整饮品菜单", "availability": "酒款与库存情况可能会有变化。"},
}

# Localized copy is grounded in the current inventory and the site's visit section.
WHISKY_GUIDE = {
    "en": {"intro": "Try Yoichi and Akkeshi from Hokkaido alongside a pour of Yamazaki, then tell us what rock song you want to hear. We’re a four-minute walk from Susukino Station. Browse all {count} whiskies and their prices below.", "explore": "Explore the whisky menu", "peat": "The Islay section includes peated whiskies such as Laphroaig and Ardbeg.", "groups": ["Japanese Whisky — Nikka", "Japanese Whisky — Suntory", "Japanese Whisky — Akkeshi", "Scotch — Islay", "Bourbon"]},
    "ja": {"intro": "ウイスキーメニューには{count}件の掲載があります。ジャパニーズ、スコッチ、バーボン、アイリッシュなどの価格をご覧いただけます。おすすめはスタッフにお尋ねください。", "explore": "カテゴリーから探す", "peat": "アイラのカテゴリーには、ラフロイグやアードベッグなどのピート系ウイスキーも掲載しています。", "groups": ["ジャパニーズウイスキー — ニッカ", "ジャパニーズウイスキー — サントリー", "ジャパニーズウイスキー — 厚岸", "スコッチ — アイラ", "バーボン"]},
    "ko": {"intro": "메뉴에는 일본 위스키, 스카치, 버번, 아이리시 등 위스키 항목 {count}개가 올라와 있습니다. 가격을 확인하고 추천이 필요하면 직원에게 문의해 주세요.", "explore": "위스키 메뉴 둘러보기", "peat": "아일라 항목에는 라프로익과 아드벡 등 피트 위스키도 있습니다.", "groups": ["일본 위스키 — 니카", "일본 위스키 — 산토리", "일본 위스키 — 앗케시", "스카치 — 아일라", "버번"]},
    "th": {"intro": "เมนูมีวิสกี้ {count} รายการ ทั้งวิสกี้ญี่ปุ่น สก็อตช์ เบอร์เบิน และไอริช ดูราคาและสอบถามพนักงานเพื่อขอคำแนะนำได้", "explore": "สำรวจเมนูวิสกี้", "peat": "หมวดไอเลย์มีวิสกี้พีต เช่น Laphroaig และ Ardbeg", "groups": ["วิสกี้ญี่ปุ่น — นิกกะ", "วิสกี้ญี่ปุ่น — ซันโทรี", "วิสกี้ญี่ปุ่น — อักเคชิ", "สก็อตช์ — ไอเลย์", "เบอร์เบิน"]},
    "zh-Hans": {"intro": "菜单列有{count}条威士忌酒款，包括日本威士忌、苏格兰威士忌、波本和爱尔兰威士忌。欢迎查看价格并向店员咨询推荐。", "explore": "浏览威士忌菜单", "peat": "艾雷岛分类中有拉弗格和阿贝等泥煤风味威士忌。", "groups": ["日本威士忌 — 日果", "日本威士忌 — 三得利", "日本威士忌 — 厚岸", "苏格兰威士忌 — 艾雷岛", "波本威士忌"]},
}

LOTTERY_COPY = {
    "en": {"title": "Whisky lottery", "intro": "Try our in-bar roulette-style whisky lottery for a chance to get a higher-priced whisky for less. A lucky result might, for example, be a pour of Yamazaki 12 for {price}. Ask the staff about current prizes and details.", "names": ["Japanese Lottery", "Islay whisky lottery"]},
    "ja": {"title": "ウイスキーくじ", "intro": "店内で楽しめるルーレット式のウイスキーくじ。通常よりお得にウイスキーを楽しめるチャンスです。例えば、運が良ければ山崎12年を{price}で楽しめることも。現在の景品や詳細はスタッフにお尋ねください。", "names": ["ジャパニーズウイスキーくじ", "アイラウイスキーくじ"]},
    "ko": {"title": "위스키 복권", "intro": "바에서 즐기는 룰렛 방식의 위스키 복권으로 더 비싼 위스키를 저렴하게 즐길 기회가 있습니다. 예를 들어 운이 좋으면 야마자키 12년을 {price}에 맛볼 수도 있습니다. 현재 경품과 자세한 내용은 직원에게 문의해 주세요.", "names": ["일본 위스키 복권", "아일라 위스키 복권"]},
    "th": {"title": "ลอตเตอรี่วิสกี้", "intro": "ลองลอตเตอรี่วิสกี้แบบรูเล็ตที่บาร์ เพื่อลุ้นวิสกี้ราคาสูงกว่าในราคาที่ถูกลง ตัวอย่างเช่น หากโชคดีอาจได้ชิม Yamazaki 12 ในราคา {price} สอบถามพนักงานเกี่ยวกับรางวัลและรายละเอียดปัจจุบัน", "names": ["ลอตเตอรี่วิสกี้ญี่ปุ่น", "ลอตเตอรี่วิสกี้ไอเลย์"]},
    "zh-Hans": {"title": "威士忌抽选", "intro": "在店内参加轮盘式威士忌抽选，有机会以较低价格喝到价格更高的威士忌。例如，幸运的话可能以{price}喝到一杯山崎12年。当前奖品和详情请咨询店员。", "names": ["日本威士忌抽选", "艾雷威士忌抽选"]},
}

# These weights are for a demonstration only; the bar's actual odds are unknown.
WHEEL_WEIGHTS = [11, 9, 6, 10, 7, 9, 11, 6, 9, 10, 12]
WHEEL_COPY = {
 "en": {"summary":"Try the wheel demo", "notice":"Demo only. No prize is awarded and this does not enter the bar’s lottery. Slice sizes and probabilities are illustrative, not the real odds. Current prizes and prices may change.", "title":"Spin the demo", "prompt":"Tap the button for an example result. Current prizes and real odds are not confirmed.", "initial":"Ready when you are.", "status":"Example result", "spin":"Spin the wheel", "spinning":"Spinning…", "example":"Example only · not a real prize", "again":"Spin again", "examples":"Example names in this demo", "names":["Fuji Single Malt","Tsunuki","Hakushu 12 Year","Yoichi","Hibiki Blender’s Choice","Yamazaki","Miyagikyo","Yamazaki 12 Year","Hakushu","Taketsuru","Nikka From The Barrel"], "short":["Fuji Single Malt","Tsunuki","Hakushu 12y","Yoichi","Hibiki BC","Yamazaki","Miyagikyo","Yamazaki 12y","Hakushu","Taketsuru","Nikka From Barrel"]},
 "ja": {"summary":"ホイールのデモを試す", "notice":"デモ専用です。実際のくじへの参加や景品の獲得にはなりません。区画の大きさと確率は例示であり、実際の当選確率ではありません。現在の景品や価格は変更されることがあります。", "title":"デモを回す", "prompt":"ボタンを押すと結果の例が表示されます。現在の景品と実際の確率は未確認です。", "initial":"ボタンを押してスタート", "status":"結果の例", "spin":"ホイールを回す", "spinning":"回転中…", "example":"結果の例 · 実際の景品ではありません", "again":"もう一度回す", "examples":"デモに登場する銘柄例", "names":["富士 シングルモルト","津貫","白州 12年","余市","響 ブレンダーズチョイス","山崎","宮城峡","山崎 12年","白州","竹鶴","ニッカ フロム・ザ・バレル"], "short":["富士 シングルモルト","津貫","白州 12年","余市","響 BC","山崎","宮城峡","山崎 12年","白州","竹鶴","フロム・ザ・バレル"]},
 "ko": {"summary":"휠 데모 해보기", "notice":"데모 전용입니다. 실제 복권에 참여하거나 경품을 받는 것이 아닙니다. 칸 크기와 확률은 예시이며 실제 확률이 아닙니다. 현재 경품과 가격은 변경될 수 있습니다.", "title":"데모 돌리기", "prompt":"버튼을 눌러 예시 결과를 확인하세요. 현재 경품과 실제 확률은 확인되지 않았습니다.", "initial":"버튼을 눌러 시작하세요.", "status":"예시 결과", "spin":"휠 돌리기", "spinning":"돌리는 중…", "example":"예시일 뿐 실제 경품이 아닙니다", "again":"다시 돌리기", "examples":"데모에 나오는 예시 이름", "names":["후지 싱글 몰트","쓰누키","하쿠슈 12년","요이치","히비키 블렌더스 초이스","야마자키","미야기쿄","야마자키 12년","하쿠슈","다케쓰루","닛카 프롬 더 배럴"], "short":["후지 싱글 몰트","쓰누키","하쿠슈 12년","요이치","히비키 BC","야마자키","미야기쿄","야마자키 12년","하쿠슈","다케쓰루","닛카 프롬 더 배럴"]},
 "th": {"summary":"ลองวงล้อสาธิต", "notice":"เป็นเพียงการสาธิต ไม่ได้เข้าร่วมลอตเตอรี่จริงหรือรับรางวัล ขนาดช่องและความน่าจะเป็นเป็นเพียงตัวอย่าง ไม่ใช่อัตราจริง รางวัลและราคาในปัจจุบันอาจเปลี่ยนแปลงได้", "title":"หมุนวงล้อสาธิต", "prompt":"กดปุ่มเพื่อดูผลตัวอย่าง ยังไม่ได้ยืนยันรางวัลปัจจุบันและอัตราจริง", "initial":"กดปุ่มเพื่อเริ่ม", "status":"ผลตัวอย่าง", "spin":"หมุนวงล้อ", "spinning":"กำลังหมุน…", "example":"ตัวอย่างเท่านั้น ไม่ใช่รางวัลจริง", "again":"หมุนอีกครั้ง", "examples":"ชื่อตัวอย่างในเดโม", "names":["ฟูจิ ซิงเกิลมอลต์","สึนุกิ","ฮาคุชู 12 ปี","โยอิจิ","ฮิบิกิ เบลนเดอร์สชอยส์","ยามาซากิ","มิยางิเคียว","ยามาซากิ 12 ปี","ฮาคุชู","ทาเค็ตสึรุ","นิกกะ ฟรอมเดอะบาร์เรล"], "short":["ฟูจิ ซิงเกิลมอลต์","สึนุกิ","ฮาคุชู 12 ปี","โยอิจิ","ฮิบิกิ BC","ยามาซากิ","มิยางิเคียว","ยามาซากิ 12 ปี","ฮาคุชู","ทาเค็ตสึรุ","นิกกะ ฟรอมเดอะบาร์เรล"]},
 "zh-Hans": {"summary":"试试转盘演示", "notice":"仅供演示，不会参加酒吧的实际抽选，也不会获得奖品。扇区大小与概率仅为示意，并非实际中奖概率。当前奖品与价格可能会有变化。", "title":"转动演示转盘", "prompt":"点击按钮查看示例结果。当前奖品和实际概率尚未确认。", "initial":"点击按钮开始", "status":"示例结果", "spin":"转动转盘", "spinning":"转动中…", "example":"仅为示例，不是真实奖品", "again":"再转一次", "examples":"演示中的示例名称", "names":["富士 单一麦芽","津贯","白州 12年","余市","响 调酒师之选","山崎","宫城峡","山崎 12年","白州","竹鹤","日果 原桶强度"], "short":["富士 单一麦芽","津贯","白州 12年","余市","响 BC","山崎","宫城峡","山崎 12年","白州","竹鹤","日果 原桶强度"]},
}

# Menu IDs, expected names and fixed analytics labels; the lottery pour size is not known.
WHEEL_MENU_ITEMS = [
 (192, "Fuji Single Malt", "fuji_single_malt"), (193, "Tsunuki Single Malt", "tsunuki"),
 (172, "Hakushu 12 Year", "hakushu_12"), (148, "Yoichi", "yoichi"),
 (162, "Hibiki Blender's Choice", "hibiki_blenders_choice"), (174, "Yamazaki", "yamazaki"),
 (142, "Miyagikyo", "miyagikyo"), (177, "Yamazaki 12 Year", "yamazaki_12"),
 (168, "Hakushu", "hakushu"), (143, "Taketsturu", "taketsuru"),
 (136, "Nikka From The Barrel", "nikka_from_the_barrel"),
]
WHEEL_RESULT_COPY = {
 "en": {"nice":"Nice! That’s a good example spin.", "menu":"Menu price", "lottery":"Lottery (30 ml)", "unspecified":"serving size not listed", "caveat":"A comparable 30 ml menu price is unavailable, so a saving cannot be calculated.", "saving":"Example saving", "savingBasis":"compared with the normal 30 ml menu price", "noSaving":"No example saving at the listed 30 ml menu price."},
 "ja": {"nice":"いいですね！デモでの結果です。", "menu":"メニュー価格", "lottery":"くじ（30 ml）", "unspecified":"提供量の記載なし", "caveat":"比較できる30 mlのメニュー価格がないため、差額は計算できません。", "saving":"差額の例", "savingBasis":"通常メニューの30 ml価格との比較", "noSaving":"掲載された30 ml価格との差額はありません。"},
 "ko": {"nice":"좋아요! 데모에서 나온 예시 결과입니다.", "menu":"메뉴 가격", "lottery":"복권 (30 ml)", "unspecified":"제공량 미기재", "caveat":"비교할 수 있는 30 ml 메뉴 가격이 없어 절약 금액을 계산할 수 없습니다.", "saving":"예시 절약 금액", "savingBasis":"일반 메뉴의 30 ml 가격과 비교", "noSaving":"표시된 30 ml 메뉴 가격과의 절약 금액이 없습니다."},
 "th": {"nice":"เยี่ยม! นี่คือผลตัวอย่างจากการสาธิต", "menu":"ราคาในเมนู", "lottery":"ลอตเตอรี่ (30 มล.)", "unspecified":"ไม่ได้ระบุปริมาณเสิร์ฟ", "caveat":"ไม่มีราคา 30 มล. ในเมนูสำหรับเปรียบเทียบ จึงคำนวณส่วนต่างไม่ได้", "saving":"ส่วนต่างตัวอย่าง", "savingBasis":"เทียบกับราคา 30 มล. ปกติในเมนู", "noSaving":"ไม่มีส่วนต่างจากราคา 30 มล. ที่ระบุในเมนู"},
 "zh-Hans": {"nice":"不错！这是演示转盘的示例结果。", "menu":"菜单价格", "lottery":"抽选（30 毫升）", "unspecified":"未注明份量", "caveat":"没有可比较的30毫升菜单价格，因此无法计算节省金额。", "saving":"示例节省", "savingBasis":"与菜单中正常 30 毫升价格相比", "noSaving":"与所列 30 毫升菜单价格相比没有节省金额。"},
}

def example_saving(normal_30, lottery_price):
    difference = normal_30 - lottery_price
    return f"¥{difference:,}" if difference > 0 else None


def render_wheel(code):
    copy = WHEEL_COPY[code]
    if len(copy["names"]) != len(WHEEL_WEIGHTS) or len(copy["short"]) != len(WHEEL_WEIGHTS):
        raise ValueError("Whisky wheel labels and weights do not match")
    total = sum(WHEEL_WEIGHTS)
    logo = (DIST / "assets/logo.svg").read_text(encoding="utf-8")
    logo_inner = re.search(r"<svg\b[^>]*>([\s\S]*)</svg>", logo).group(1)
    colors = ["#302321", "#251f1f", "#5c2f2b", "#332524", "#57302c", "#2c2221", "#392824", "#5c2f2b", "#2e2322", "#382925", "#2a2020"]
    svg = ['<svg id="whisky-wheel-svg" viewBox="0 0 400 400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><circle cx="200" cy="200" r="196" fill="#ff5954"/><circle cx="200" cy="200" r="189" fill="#161414"/>']
    current = 0
    for name, weight, color in zip(copy["short"], WHEEL_WEIGHTS, colors):
        start = -90 + current / total * 360
        end = -90 + (current + weight) / total * 360
        mid = (start + end) / 2
        current += weight
        x1, y1 = 200 + 182*math.cos(math.radians(start)), 200 + 182*math.sin(math.radians(start))
        x2, y2 = 200 + 182*math.cos(math.radians(end)), 200 + 182*math.sin(math.radians(end))
        x, y = 200 + 132*math.cos(math.radians(mid)), 200 + 132*math.sin(math.radians(mid))
        angle = mid + 180 if 90 < mid % 360 < 270 else mid
        fontsize = 9.5 if len(name) > 15 or (code != "en" and len(name) > 8) else 11.5
        svg.append(f'<path d="M200 200 L{x1:.4f} {y1:.4f} A182 182 0 0 1 {x2:.4f} {y2:.4f} Z" fill="{color}" stroke="#b65851" stroke-width="1.2"/>')
        svg.append(f'<text x="{x:.3f}" y="{y:.3f}" transform="rotate({angle:.3f} {x:.3f} {y:.3f})" fill="#f0efe7" font-family="Barlow Condensed,Noto Sans JP,sans-serif" font-weight="700" font-size="{fontsize}" text-anchor="middle" dominant-baseline="middle">{escape(name)}</text>')
    svg.append('<circle cx="200" cy="200" r="57" fill="#161414" stroke="#ff5954" stroke-width="3"/>')
    svg.append(f'<svg x="151" y="177.3" width="98" height="45.4" viewBox="0 0 151 70">{logo_inner}</svg></svg>')
    menu = {item["id"]: item for item in json.loads((ROOT / "source/menu/menu-data.json").read_text(encoding="utf-8"))}
    result_copy = WHEEL_RESULT_COPY[code]
    lottery = menu.get(297)
    if not lottery or lottery.get("name") != "Japanese Lottery" or not isinstance(lottery.get("prices", {}).get("standard"), int):
        raise ValueError("Japanese whisky lottery price is unavailable")
    configured_items = []
    for name, weight, (item_id, expected_name, event_id) in zip(copy["names"], WHEEL_WEIGHTS, WHEEL_MENU_ITEMS):
        item = menu.get(item_id)
        if not item or item.get("name") != expected_name:
            raise ValueError(f"Wheel menu item {item_id} is missing or changed")
        prices = item.get("prices", {})
        # The owner confirmed standard whisky servings are 30 ml; 15 ml is optional.
        explicit_30 = prices.get("30ml")
        standard = prices.get("standard")
        normal_30 = explicit_30 if isinstance(explicit_30, int) else standard if isinstance(standard, int) else None
        comparable = normal_30 is not None
        if comparable:
            price = (f"15 ml ¥{prices['15ml']:,} / " if isinstance(prices.get("15ml"), int) else "") + f"30 ml ¥{normal_30:,}"
        else:
            raise ValueError(f"Wheel menu item {item_id} has no comparable 30 ml price")
        saving = example_saving(normal_30, lottery["prices"]["standard"])
        configured_items.append({"id": event_id, "name": name, "weight": weight, "price": price, "comparable": comparable, "saving": saving})
    config = {"items": configured_items, "locale": code, "spinning": copy["spinning"], "example": copy["example"], "again": copy["again"],
        "nice": result_copy["nice"], "menuLabel": result_copy["menu"], "lotteryLabel": result_copy["lottery"],
        "lotteryPrice": f"¥{lottery['prices']['standard']:,}", "caveat": result_copy["caveat"], "savingLabel": result_copy["saving"],
        "savingBasis": result_copy["savingBasis"], "noSaving": result_copy["noSaving"]}
    data = json.dumps(config, ensure_ascii=False).replace("</", r"<\/")
    examples = "".join("<li>" + escape(name) + "</li>" for name in copy["names"])
    return ('<details class="whisky-wheel-demo"><summary>' + escape(copy["summary"]) + '</summary>'
      + '<p class="whisky-wheel-notice">' + escape(copy["notice"]) + '</p><div class="whisky-wheel-game">'
      + '<div class="whisky-wheel-holder"><span class="whisky-wheel-pointer" aria-hidden="true"></span>' + "".join(svg) + '</div>'
      + '<div class="whisky-wheel-panel"><h3>' + escape(copy["title"]) + '</h3><p class="whisky-wheel-fine">' + escape(copy["prompt"]) + '</p>'
      + '<div class="whisky-wheel-result" role="status" aria-live="polite"><div class="whisky-wheel-status" id="whisky-wheel-status">' + escape(copy["status"]) + '</div><div class="whisky-wheel-result-name" id="whisky-wheel-result">' + escape(copy["initial"]) + '</div><p class="whisky-wheel-message" id="whisky-wheel-message"></p><p class="whisky-wheel-prices" id="whisky-wheel-prices"></p></div>'
      + '<button type="button" class="whisky-wheel-spin" id="whisky-wheel-spin" disabled>' + escape(copy["spin"]) + '</button></div></div>'
      + '<details class="whisky-wheel-examples"><summary>' + escape(copy["examples"]) + '</summary><ul>' + examples + '</ul></details>'
      + '<script type="application/json" id="whisky-wheel-data">' + data + '</script></details>')

class HomepageVisitParser(HTMLParser):
    """Reuse the public homepage's visit facts and existing translations."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.values = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        text = attrs.get("data-en", "")
        needles = {"address": "5-chome 21-3", "station": "About a 4-minute walk from Susukino Station", "hours": "21:00–03:00", "cover": "¥500 cover charge (tax included) · One-drink minimum"}
        for key, needle in needles.items():
            if needle in text and key not in self.values:
                self.values[key] = (text, attrs.get("data-ja"))
        if text == "OPENING HOURS":
            self.values["hours_label"] = (text, attrs.get("data-ja"))


def homepage_visit_facts(code):
    parser = HomepageVisitParser()
    parser.feed((ROOT / "source/index.html").read_text(encoding="utf-8"))
    keys = ("address", "station", "hours", "cover", "hours_label")
    if any(key not in parser.values or not parser.values[key][1] for key in keys):
        raise ValueError("Homepage visit facts are missing; update the whisky page builder")
    translations = json.loads((ROOT / "source/translations.json").read_text(encoding="utf-8"))
    def translate(key):
        english, japanese = parser.values[key]
        if code == "en": value = english
        elif code == "ja": value = japanese
        else:
            value = translations.get(code, {}).get(english)
            if not value: raise ValueError(f"Missing {code} homepage translation for {key}")
        return re.sub(r"<br\s*/?>", " · ", value, flags=re.I).replace("\u00a0", " ")
    return {key: translate(key) for key in keys}

FORM_COPY = {
    "en": {"empty_copy": "Sorry, that whisky isn’t on our list. Please let us know which bottle you were looking for.", "suggestion_label": "Whisky bottle name", "suggestion_note": "Submitting sends the bottle name to Google Analytics so we can understand what visitors are looking for. Enter the bottle name only; do not include your name, address, phone number, email address, or other personal information.", "certify": "I certify that this is only a whisky bottle name and contains no personal information.", "submit": "Submit", "map_label": "Google Maps location guide", "map_title": "Google Maps area guide for Rock Bar FxxK Up in Susukino, Sapporo"},
    "ja": {"empty_copy": "お探しのウイスキーはメニューにありません。ご希望の銘柄をお知らせください。", "suggestion_label": "ウイスキーの銘柄名", "suggestion_note": "送信すると、どの銘柄が探されているかを知るために、ボトル名がGoogle アナリティクスに送信されます。銘柄名のみを入力し、氏名、住所、電話番号、メールアドレスなどの個人情報は入力しないでください。", "certify": "入力内容がウイスキーの銘柄名のみで、個人情報を含まないことを確認します。", "submit": "送信", "map_label": "Google マップで周辺を見る", "map_title": "札幌・すすきののRock Bar FxxK Up周辺マップ"},
    "ko": {"empty_copy": "찾으시는 위스키가 메뉴에 없습니다. 원하셨던 제품명을 알려주세요.", "suggestion_label": "위스키 제품명", "suggestion_note": "제출하면 방문자가 어떤 제품을 찾는지 파악하기 위해 제품명이 Google 애널리틱스로 전송됩니다. 제품명만 입력하고 이름, 주소, 전화번호, 이메일 주소 등 개인정보는 입력하지 마세요.", "certify": "입력 내용이 위스키 제품명만 포함하며 개인정보가 없음을 확인합니다.", "submit": "제출", "map_label": "Google 지도 위치 안내", "map_title": "삿포로 스스키노 Rock Bar FxxK Up 주변 지도"},
    "th": {"empty_copy": "ไม่มีวิสกี้ที่ค้นหาในรายการของเรา โปรดแจ้งชื่อขวดที่คุณกำลังมองหา", "suggestion_label": "ชื่อวิสกี้", "suggestion_note": "เมื่อส่ง ชื่อวิสกี้จะถูกส่งไปยัง Google Analytics เพื่อให้เราเข้าใจว่าผู้เข้าชมกำลังมองหาอะไร โปรดกรอกเฉพาะชื่อวิสกี้ และอย่าระบุชื่อ ที่อยู่ หมายเลขโทรศัพท์ อีเมล หรือข้อมูลส่วนบุคคลอื่น ๆ", "certify": "ขอยืนยันว่าข้อความนี้มีเพียงชื่อวิสกี้และไม่มีข้อมูลส่วนบุคคล", "submit": "ส่ง", "map_label": "แผนที่ตำแหน่ง Google Maps", "map_title": "แผนที่บริเวณ Rock Bar FxxK Up ในซูซูกิโนะ ซัปโปโร"},
    "zh-Hans": {"empty_copy": "我们暂时没有这款威士忌。请告诉我们您想找的酒款名称。", "suggestion_label": "威士忌酒款名称", "suggestion_note": "提交后，酒款名称会发送至 Google Analytics，帮助我们了解访客正在寻找哪些酒款。请只填写酒款名称，不要填写姓名、地址、电话号码、电子邮箱或其他个人信息。", "certify": "我确认这里只填写威士忌酒款名称，不含个人信息。", "submit": "提交", "map_label": "Google 地图位置指南", "map_title": "札幌薄野 Rock Bar FxxK Up 周边地图"},
}

TITLE_FALLBACK = "Sapporo Whiskey Bar Menu & Prices | Rock Bar FxxK Up"
DESCRIPTION_FALLBACK = "Browse Japanese whisky, Scotch, bourbon and more at Rock Bar FxxK Up, a whisky bar in Susukino, Sapporo. Check menu prices and directions before you visit."
NOTE_HEADINGS = {
    "en": "Menu data notes",
    "ja": "メニュー情報の確認事項",
    "ko": "메뉴 데이터 확인 사항",
    "th": "หมายเหตุเกี่ยวกับข้อมูลเมนู",
    "zh-Hans": "菜单数据备注",
}

def parse_inventory(config):
    text = (SOURCE / config["file"]).read_text(encoding="utf-8")
    heading = ""
    page_title = TITLE_FALLBACK
    description = DESCRIPTION_FALLBACK
    source_line = ""
    groups = []
    notes = []
    in_notes = False

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# ") and not heading:
            heading = line[2:].strip()
            continue
        if line.startswith(config["title_prefix"]):
            page_title = line[len(config["title_prefix"]):].strip()
            continue
        if line.startswith(config["description_prefix"]):
            description = line[len(config["description_prefix"]):].strip()
            continue
        if not source_line and (line.startswith("Source:") or line.startswith("出典：") or line.startswith("最終更新日：") or line.startswith("출처:") or line.startswith("최종 업데이트:") or line.startswith("ที่มา:") or line.startswith("อัปเดตล่าสุด:") or line.startswith("来源：") or line.startswith("最后更新：") or line.startswith("Last updated ")):
            source_line = line
            continue
        if line.startswith("## "):
            category_name = line[3:].strip()
            if category_name == NOTE_HEADINGS[config["code"]]:
                in_notes = True
            else:
                groups.append({"name": category_name, "items": []})
                in_notes = False
            continue
        if line.startswith("- "):
            entry = line[2:].strip()
            if in_notes:
                notes.append(entry)
            elif groups:
                name, sep, price = entry.partition(" — ")
                groups[-1]["items"].append({"name": name.strip(), "price": price.strip() if sep else ""})
            continue
        if in_notes:
            notes.append(line)

    if not heading or not groups:
        raise ValueError("Inventory source is missing its heading or categories: " + config["file"])
    return {"heading": heading, "title": page_title, "description": description, "source": source_line, "groups": groups, "notes": notes}

def locale_root(config):
    return "/" if not config["folder"] else "/" + config["folder"] + "/"

def page_url(config):
    return ORIGIN + locale_root(config) + "whisky/"

def render_page(config, inventory, menu_urls):
    code = config["code"]
    label = LABELS[code]
    form_copy = FORM_COPY[code]
    lang_root = locale_root(config)
    canonical = page_url(config)
    hreflang_links = "\n".join(
        '<link rel="alternate" hreflang="' + escape(other["code"], quote=True) + '" href="' + escape(page_url(other), quote=True) + '">'
        for other in ACTIVE_LANGUAGES
    ) + '\n<link rel="alternate" hreflang="x-default" href="' + escape(page_url(ACTIVE_LANGUAGES[0]), quote=True) + '">'
    language_options = "\n".join(
        '<a href="' + escape(menu_urls[other["code"]], quote=True) + '" hreflang="' + escape(other["code"], quote=True) + '" lang="' + escape(other["code"], quote=True) + '" data-language="' + escape(other["code"], quote=True) + '" data-track-event="whisky_language_select" data-track-placement="language_menu"' + (' aria-current="page"' if other["code"] == code else '') + '>' + {"en": "English", "ja": "日本語", "ko": "한국어", "th": "ไทย", "zh-Hans": "简体中文"}[other["code"]] + '</a>'
        for other in LANGUAGES
    )
    category_guide = CATEGORY_GUIDE[code]
    english_groups = parse_inventory(LANGUAGES[0])["groups"]
    category_names = [group["name"] for group in english_groups]
    if set(category_guide["categories"]) != set(category_names) or len(inventory["groups"]) != len(category_names):
        raise ValueError(f"Whisky category guide does not match the inventory sections: {code}")
    category_options = ['<option value="all">' + escape(label["all"]) + '</option>']
    category_sections = []
    flat_names = []
    for index, group in enumerate(inventory["groups"], 1):
        category_id = str(index)
        category_options.append('<option value="' + category_id + '">' + escape(group["name"]) + '</option>')
        items_html = []
        for item in group["items"]:
            name = item["name"]
            price = item["price"]
            flat_names.append(name)
            search_value = escape(name + " " + price + " " + group["name"], quote=True)
            price = price.replace("15ml", {"en":"15ml", "ja":"15ml", "ko":"15ml", "th":"15 มล.", "zh-Hans":"15毫升"}[code]).replace("30ml", {"en":"30ml", "ja":"30ml", "ko":"30ml", "th":"30 มล.", "zh-Hans":"30毫升"}[code])
            note_match = re.match(r"^(.*?)(?:\s+([（(].*[）)]))$", price)
            if note_match:
                price_html = '<span class="whisky-price-value">' + escape(note_match.group(1).strip()) + '</span><span class="whisky-item-note">' + escape(note_match.group(2).strip()) + '</span>'
            else:
                price_html = '<span class="whisky-price-value">' + escape(price) + '</span>'
            items_html.append('<li class="whisky-item" data-search="' + search_value + '"><span class="whisky-name">' + escape(name) + '</span><span class="whisky-price">' + price_html + '</span></li>')
        english_name = category_names[index - 1]
        japanese = english_name.startswith("Japanese Whisky — ")
        if japanese and not any(name.startswith("Japanese Whisky — ") for name in category_names[:index - 1]):
            category_sections.append('<p class="whisky-japanese-note" data-whisky-japanese-note>' + escape(category_guide["japanese_note"]) + '</p>')
        origin = ' data-whisky-origin="japanese"' if japanese else ''
        category_sections.append('<section class="whisky-category" data-whisky-group data-category-id="' + category_id + '"' + origin + '><h2 id="category-' + category_id + '">' + escape(group["name"]) + '</h2><p class="whisky-category-guide">' + escape(category_guide["categories"][english_name]) + '</p><ul class="whisky-list">' + "".join(items_html) + '</ul></section>')

    initial_count = sum(len(group["items"]) for group in inventory["groups"])
    lottery = LOTTERY_COPY[code]
    menu_data = json.loads((ROOT / "source" / "menu" / "menu-data.json").read_text(encoding="utf-8"))
    menu_by_id = {item["id"]: item for item in menu_data}
    lottery_items = [menu_by_id[297], menu_by_id[299]]
    if [item["name"] for item in lottery_items] != ["Japanese Lottery", "Islay whiskey lottery"]:
        raise ValueError("Whisky lottery menu IDs no longer match the expected items")
    if any(not isinstance(item.get("prices", {}).get("standard"), int) for item in lottery_items):
        raise ValueError("Whisky lottery prices are missing from menu data")
    # The lottery is a separate page feature, not a searchable whisky item.
    lottery_section = '<section class="whisky-category"><h2 id="category-lottery">' + escape(lottery["title"]) + '</h2><p class="whisky-availability">' + escape(category_guide["lottery"].format(price="¥" + format(lottery_items[0]["prices"]["standard"], ","))) + '</p>' + render_wheel(code) + '</section>'
    display_count = initial_count
    guide = WHISKY_GUIDE[code]
    visit_facts = homepage_visit_facts(code)
    positions = {group["name"]: index for index, group in enumerate(inventory["groups"], 1)}
    missing = [name for name in guide["groups"] if name not in positions]
    if missing:
        raise ValueError(f"Whisky guide categories missing for {code}: {missing}")
    guide_links = '<a href="#category-lottery">' + escape(lottery["title"]) + '</a>' + "".join('<a href="#category-' + str(positions[name]) + '">' + escape(name) + '</a>' for name in guide["groups"])
    guide_intro = guide["intro"].format(count=initial_count)
    intro_html = f'<p class="whisky-intro">{escape(guide_intro)}</p>'
    philosophy_html = f'''<section class="whisky-philosophy" aria-labelledby="whisky-philosophy-title">
      <h2 id="whisky-philosophy-title">{escape(category_guide["philosophy_title"])}</h2>
      <p>{escape(category_guide["philosophy"])}</p>
    </section>'''
    hero_sections = (intro_html, philosophy_html) if code == "en" else (philosophy_html, intro_html)
    hero_copy = "\n    ".join(hero_sections)
    category_options[0] = '<option value="all">' + escape(label["all"]) + '</option>'
    source_note = '<p class="whisky-updated">' + escape(inventory["source"]) + '</p>' if inventory["source"] else ""
    privacy_href = "/privacy/#ja" if code == "ja" else "/privacy/#en"
    website_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": inventory["title"],
        "description": inventory["description"],
        "url": canonical,
        "inLanguage": code,
        "isPartOf": {"@type": "WebSite", "name": "Rock Bar FxxK Up", "url": ORIGIN + "/"},
        "about": {"@type": "BarOrPub", "name": "Rock Bar FxxK Up", "url": ORIGIN + "/"},
        "mainEntity": {"@type": "ItemList", "numberOfItems": initial_count, "itemListElement": [{"@type": "ListItem", "position": pos, "name": name} for pos, name in enumerate(flat_names, 1)]},
    }
    description = escape(inventory["description"], quote=True)
    title = escape(inventory["title"])
    schema = json.dumps(website_schema, ensure_ascii=False).replace("</", "<\\/")
    external_icon = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"></path></svg>'
    body = f'''<!doctype html>
<html lang="{escape(code, quote=True)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#161414">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{escape(canonical, quote=True)}">
{hreflang_links}
<link rel="icon" href="/assets/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&amp;family=DM+Sans:wght@400;500;600;700&amp;family=Noto+Sans+JP:wght@400;600;800&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<style>{(ROOT / "source/whisky-wheel.css").read_text(encoding="utf-8")}\n{(ROOT / "source/whisky-guide.css").read_text(encoding="utf-8")}</style>
<script src="/whisky.js" defer></script>
<script src="/whisky-wheel.js" defer></script>
<script>window.dataLayer=window.dataLayer||[];window.gtag=window.gtag||function(){{dataLayer.push(arguments);}};if(['rockbarfxxkup.com','www.rockbarfxxkup.com'].includes(location.hostname)){{gtag('js',new Date());gtag('config','G-JPYT9JRWBT',{{allow_google_signals:false,allow_ad_personalization_signals:false}});const analyticsScript=document.createElement('script');analyticsScript.async=true;analyticsScript.src='https://www.googletagmanager.com/gtag/js?id=G-JPYT9JRWBT';document.head.appendChild(analyticsScript);}}</script>
<script src="/analytics.js" defer></script>
<meta property="og:type" content="website">
<meta property="og:site_name" content="Rock Bar FxxK Up">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{escape(canonical, quote=True)}">
<meta property="og:image" content="{ORIGIN}/assets/neon-social-preview.jpg">
<meta property="og:locale" content="{ {"en":"en_US","ja":"ja_JP","ko":"ko_KR","th":"th_TH","zh-Hans":"zh_CN"}[code] }">
<script type="application/ld+json">{schema}</script>
</head>
<body class="whisky-page">
<a class="skip" href="#main">{escape({"en":"Skip to content","ja":"本文へ移動","ko":"본문으로 이동","th":"ข้ามไปยังเนื้อหา","zh-Hans":"跳至正文"}[code])}</a>
<header class="whisky-header">
  <a class="brand" href="{escape(lang_root, quote=True)}" aria-label="Rock Bar FxxK Up home" data-track-event="whisky_home_click" data-track-destination="home" data-track-placement="whisky_logo"><img src="/assets/logo.svg" alt="Rock Bar FxxK Up" width="66" height="66"><span>SUSUKINO<br>SAPPORO, JP</span></a>
  <nav aria-label="Main navigation"><a href="{escape(lang_root, quote=True)}" data-track-event="whisky_home_click" data-track-destination="home" data-track-placement="whisky_navigation">{escape(label["home"])}</a><a href="{escape(lang_root + '#drinks', quote=True)}" data-track-event="whisky_drinks_click" data-track-destination="drinks_section" data-track-placement="whisky_navigation">{escape(label["drinks"])}</a><a href="{escape(lang_root + '#visit', quote=True)}" data-track-event="whisky_find_us_click" data-track-destination="visit_section" data-track-placement="whisky_navigation">{escape(label["find"])}</a></nav>
  <div class="header-actions"><details class="language-menu"><summary id="language">{escape(label["language"])}</summary><nav class="language-options" aria-label="{escape(label['languages'], quote=True)}">{language_options}</nav></details></div>
</header>
<main id="main">
  <section class="whisky-hero">
    <div class="section-tag">{escape(label["area"])}</div>
    <h1>{escape(inventory["heading"])}</h1>
    {hero_copy}
    <p class="whisky-availability">{escape(label["availability"])}</p>
    {source_note}
    <p class="whisky-availability">{escape(visit_facts["address"])} · {escape(visit_facts["station"])} · {escape(visit_facts["cover"])}</p>
    <p class="whisky-availability"><strong>{escape(visit_facts["hours_label"])}</strong> · {escape(visit_facts["hours"])}</p>
    <details class="whisky-start-guide"><summary>{escape(category_guide["start_title"])}</summary><p>{escape(category_guide["start"])}</p></details>
    <nav class="whisky-visit-links" aria-label="{escape(guide['explore'], quote=True)}">{guide_links}</nav>
  <div class="whisky-visit-links"><a href="{escape(lang_root + 'menu/', quote=True)}" data-track-event="menu_open" data-track-destination="static_menu" data-track-placement="whisky_visit_links">{escape(label["full_menu"])} {external_icon}</a><a class="whisky-directions-button" href="https://maps.app.goo.gl/95hYVdZMdPot4WQy5" target="_blank" rel="noopener" data-track-event="whisky_directions_click" data-track-destination="google_maps" data-track-placement="whisky_visit_links">{escape(label["directions"])} {external_icon}</a></div>
  </section>
  <section class="whisky-catalog" aria-label="{escape(inventory['heading'], quote=True)}">
    <div class="whisky-controls" hidden>
      <label class="sr-only" for="whisky-search">{escape(label["search"])}</label>
      <input id="whisky-search" type="search" placeholder="{escape(label['placeholder'], quote=True)}" autocomplete="off">
      <label class="sr-only" for="whisky-category">{escape(label["category"])}</label>
      <div class="whisky-category-control">
        <select id="whisky-category">{"".join(category_options)}</select>
        <p id="whisky-count" data-suffix="{escape(label['count'], quote=True)}" aria-live="polite">({display_count} {escape(label['count'])})</p>
      </div>
      <button id="whisky-clear" type="button">{escape(label["clear"])}</button>
    </div>
    <section id="whisky-empty" class="whisky-empty" aria-live="polite" hidden>
      <p class="whisky-empty-title">{escape(label["no_results"])}</p>
      <p>{escape(form_copy["empty_copy"])}</p>
      <form id="whisky-suggestion-form" class="whisky-suggestion" novalidate>
        <label for="whisky-suggestion">{escape(form_copy["suggestion_label"])}</label>
        <input id="whisky-suggestion" name="suggestion" type="text" maxlength="80" autocomplete="off" required>
        <p class="whisky-suggestion-note">{escape(form_copy["suggestion_note"])}</p>
        <label class="whisky-suggestion-consent"><input id="whisky-suggestion-certify" type="checkbox" required> {escape(form_copy["certify"])}</label>
        <button class="button yellow" type="submit">{escape(form_copy["submit"])}</button>
        <p id="whisky-suggestion-status" class="whisky-suggestion-status" role="status" aria-live="polite"><svg class="whisky-suggestion-status-icon" viewBox="0 0 48 32" aria-hidden="true"><rect x="4" y="5" width="15" height="23" rx="2"/><path d="M8 11h7M8 16h7M8 21h4M19 17h4"/><g class="whisky-gate-arm"><path d="M23 17h21"/><circle cx="23" cy="17" r="2"/></g></svg><span id="whisky-suggestion-message"></span></p>
      </form>
    </section>
    {"".join(category_sections)}
    {lottery_section}
    <section class="whisky-map" aria-label="{escape(form_copy['map_label'], quote=True)}">
      <iframe src="https://storage.googleapis.com/maps-solutions-y33v72la8f/commutes/2na5/commutes.html" width="100%" height="420" style="border:0;" loading="lazy" title="{escape(form_copy['map_title'], quote=True)}"></iframe>
    </section>
  </section>
</main>
<nav class="language-links" aria-label="Website languages">{language_options}</nav>
<footer><span>© 2026 ROCK BAR FxxK UP</span><span>ROCK &amp; WHISKY. SUSUKINO, SAPPORO.</span><a href="{escape(privacy_href, quote=True)}" data-track-event="whisky_privacy_click" data-track-destination="privacy_policy" data-track-placement="whisky_footer">{escape(label["privacy"])}</a></footer>
<div class="mobile-bar"><a href="https://maps.app.goo.gl/95hYVdZMdPot4WQy5" target="_blank" rel="noopener" data-track-event="whisky_directions_click" data-track-destination="google_maps" data-track-placement="whisky_mobile_bar">{escape(label["directions"])} {external_icon}</a><a href="https://www.instagram.com/rockbar_fxxkup/" target="_blank" rel="noopener" data-track-event="whisky_instagram_click" data-track-destination="bar" data-track-placement="whisky_mobile_bar">{escape(label["instagram"])} {external_icon}</a></div>
</body>
</html>'''
    return body

def add_home_links(config):
    path = DIST / (config["folder"] + "/index.html" if config["folder"] else "index.html")
    text = path.read_text(encoding="utf-8")
    # build-seo.py creates every locale from the canonical homepage template,
    # which already contains the translated navigation link and primary CTA.
    # Older builds injected a second link because their route is locale-prefixed.
    text = re.sub(r'<a class="whisky-nav-link"[^>]*>.*?</a>', '', text, flags=re.DOTALL)
    text = re.sub(r'<a class="text-link whisky-index-link"[^>]*>.*?</a>', '', text, flags=re.DOTALL)
    path.write_text(text, encoding="utf-8")

def remove_home_links(config):
    path = DIST / (config["folder"] + "/index.html" if config["folder"] else "index.html")
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<a class="whisky-nav-link"[^>]*>.*?</a>', '', text, flags=re.DOTALL)
    text = re.sub(r'<a class="text-link whisky-index-link"[^>]*>.*?</a>', '', text, flags=re.DOTALL)
    path.write_text(text, encoding="utf-8")

def write_sitemap():
    sitemap_ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    ET.register_namespace("", sitemap_ns)
    ET.register_namespace("xhtml", xhtml_ns)
    sitemap_path = DIST / "sitemap.xml"
    if sitemap_path.exists():
        root = ET.parse(sitemap_path).getroot()
    else:
        root = ET.Element("{" + sitemap_ns + "}urlset")
    existing = {
        node.find("{" + sitemap_ns + "}loc").text: node
        for node in root.findall("{" + sitemap_ns + "}url")
        if node.find("{" + sitemap_ns + "}loc") is not None
    }
    alternates = [(config["code"], page_url(config)) for config in ACTIVE_LANGUAGES]
    for config in ACTIVE_LANGUAGES:
        url = page_url(config)
        node = existing.get(url)
        if node is None:
            node = ET.SubElement(root, "{" + sitemap_ns + "}url")
            ET.SubElement(node, "{" + sitemap_ns + "}loc").text = url
        for alternate in node.findall("{" + xhtml_ns + "}link"):
            node.remove(alternate)
        for lang, alternate_url in alternates:
            ET.SubElement(node, "{" + xhtml_ns + "}link", {"rel":"alternate", "hreflang":lang, "href":alternate_url})
        ET.SubElement(node, "{" + xhtml_ns + "}link", {"rel":"alternate", "hreflang":"x-default", "href":page_url(ACTIVE_LANGUAGES[0])})
    sitemap_path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: " + ORIGIN + "/sitemap.xml\n", encoding="utf-8")

def main():
    inventories = {config["code"]: parse_inventory(config) for config in ACTIVE_LANGUAGES}
    menu_urls = {
        config["code"]: ("/" + (config["folder"] + "/" if config["folder"] else "") + "whisky/")
        if config in ACTIVE_LANGUAGES else locale_root(config)
        for config in LANGUAGES
    }
    for config in LANGUAGES:
        if config not in ACTIVE_LANGUAGES:
            if config["folder"]:
                shutil.rmtree(DIST / config["folder"] / "whisky", ignore_errors=True)
            remove_home_links(config)
            continue
        target = DIST / (config["folder"] + "/whisky/index.html" if config["folder"] else "whisky/index.html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(config, inventories[config["code"]], menu_urls), encoding="utf-8")
        add_home_links(config)
    shutil.copyfile(ROOT / "source" / "whisky.js", DIST / "whisky.js")
    shutil.copyfile(ROOT / "source" / "whisky-wheel.js", DIST / "whisky-wheel.js")
    write_sitemap()
    import subprocess
    import sys
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build-menu.py")], check=True)
    print("Built all active localized whisky pages from the source inventories.")

if __name__ == "__main__":
    main()
