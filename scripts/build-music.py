from copy import deepcopy
from pathlib import Path
import json
from lxml import etree, html

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/music/index.html"
SOURCE_CSS = ROOT / "source/music/music.css"
DIST = ROOT / "dist"
ORIGIN = "https://www.rockbarfxxkup.com"
LANGUAGES = ["en", "ja", "ko", "th", "zh-Hans"]
LABELS = {"en":"English", "ja":"日本語", "ko":"한국어", "th":"ไทย", "zh-Hans":"简体中文"}
ROUTES = {lang: ORIGIN + ("/music/" if lang == "en" else f"/{lang.lower()}/music/") for lang in LANGUAGES}

# These translations keep the team's names and the Rock Bar FxxK Up brand intact.
COPY = {
"ja": {
"nav_bar":"バーについて", "nav_music":"音楽", "nav_whisky":"ウイスキー", "nav_find":"アクセス", "nav_aria":"メインナビゲーション",
"eyebrow":"札幌の夜 / 音楽", "h1":"札幌の<br>音楽バー<span class=\"accent\">。</span>", "hero_line":"ロック、パンク。<br>メタル。今夜は何を聴く？", "hero_desc":"すすきののロックバー Rock Bar FxxK Up。カウンターに立つメンバーによって選曲も変わります。聴きたい曲があれば気軽にリクエストしてください。", "hero_cta":"FxxK Upの音楽を聴く", "directions":"アクセスを見る", "meta_genres":"ロック / パンク / メタル", "meta_requests":"曲のリクエスト歓迎",
"art_aria":"ロック、パンク、メタル。A面とB面。", "art_location":"すすきの / 札幌", "art_side":"A面 / B面", "art_title":"音楽が<br>変わるのは<br><em>この夜。</em>", "ticker":"ロック / パンク / メタル / 曲のリクエスト歓迎",
"sound_tag":"01 / 音楽", "sound_title":"ロック、パンク<br>＆メタル。", "sound_intro":"札幌で音楽を楽しめるバーをお探しですか？すすきののロックバー、FxxK Upではロック、パンク、メタルを中心に、ダブ、レゲエ、ブルースなどを流す夜もあります。その日の雰囲気に合わせて選曲し、曲のリクエストも歓迎しています。", "sound_aria":"音楽ジャンル", "genre_rock":"ロック", "genre_rock_desc":"思わず口ずさむサビ、聴きなじみのあるリフ、そして時々ちょっと意外な一曲。", "genre_punk":"パンク", "genre_punk_desc":"まっすぐで勢いのある、フロアの空気を変える音。", "genre_metal":"メタル", "genre_metal_desc":"重いギター、深いグルーヴ。聴きたい曲のリクエストもどうぞ。",
"team_tag":"02 / プレイリストの裏側", "team_title":"4人それぞれの音。<br>同じフロア。", "mixer_aria":"4人の異なる音楽の好みを表す4つのミキサーチャンネル", "mix_top":"ライブミックス / 4チャンネル", "mix_right":"毎晩違う組み合わせ", "mix_roots":"ルーツ", "mix_leftfield":"アヴァンギャルド", "mix_indie":"インディー", "mix_heavy":"ヘヴィ", "mix_footer":"4つの好み / ひとつのフロア", "team_p1":"カウンターに立つ人によってプレイリストも変わります。それぞれ違う音楽の好みがあるから、夜ごとにサウンドも変化します。", "team_p2":"好きなバンドの話をしたり、今流れている曲を尋ねたり、聴きたい曲をリクエストしたり。音楽の話から会話が広がるのも、この場所の楽しみです。", "nori_tag":"01 / パンクのルーツ", "nori_desc":"80年代、90年代、2000年代のパンクが好き。レゲエ、ブルース、クラシックロックもよく聴きます。", "chuck_tag":"02 / アンダーグラウンド", "chuck_desc":"アンダーグラウンドや前衛的な音楽が中心。ポピュラー音楽は少し苦手ですが、クラシックには敬意を持っています。", "haruka_tag":"03 / 好奇心のままに", "haruka_desc":"インディーロックやクラシックロック、新しい音楽との出会いが好きです。", "kanata_tag":"04 / ヘヴィな音", "kanata_desc":"モダン・スラッシュ、メタルを中心に、とにかくヘヴィな音楽が好き。リフも音量も遠慮なし。",
"request_art_index":"NO. 001 / ゲストのリクエスト", "request_art_title":"曲の<br>リクエスト<br><em>歓迎。</em>", "request_art_footer":"聴きたい曲を / あなたの一曲を", "request_tag":"03 / あなたのリクエスト", "request_title":"聴きたい曲は<br>ありますか<span class=\"accent\">？</span>", "request_desc":"曲のリクエストを歓迎しています。NoriかChuckに、今夜聴きたい音楽を気軽に教えてください。できる限りお応えします。", "come_find":"お店へのアクセス", "next_tag":"04 / 今夜を楽しもう", "next_title":"いい音楽。<br>いいウイスキー。", "next_desc":"ボトルを選んで、曲を選んで、6階のバーへ。", "whisky_link":"ウイスキーリストを見る", "find_link":"すすきので見つける", "footer_line":"ロック / パンク / メタル / すすきの、札幌", "back_top":"トップへ戻る ↑", "privacy":"プライバシー", "mobile_directions":"アクセス", "languages_aria":"音楽ページの言語", "language_summary":"日本語"
},
"ko": {
"nav_bar":"바 소개", "nav_music":"음악", "nav_whisky":"위스키", "nav_find":"찾아오기", "nav_aria":"주 메뉴",
"eyebrow":"삿포로의 밤 / 음악", "h1":"삿포로<br>뮤직 바<span class=\"accent\">.</span>", "hero_line":"록. 펑크.<br>메탈. 오늘은 당신의 선택.", "hero_desc":"스스키노의 록 바 Rock Bar FxxK Up. 바에 서는 멤버에 따라 음악도 달라집니다. 듣고 싶은 곡이 있으면 편하게 신청해 주세요.", "hero_cta":"FxxK Up의 음악 듣기", "directions":"오시는 길", "meta_genres":"록 / 펑크 / 메탈", "meta_requests":"신청곡 환영",
"art_aria":"록, 펑크, 메탈. A면과 B면.", "art_location":"스스키노 / 삿포로", "art_side":"A면 / B면", "art_title":"밤마다 바뀌는<br>우리의 음악<br><em>이 밤의 사운드.</em>", "ticker":"록 / 펑크 / 메탈 / 신청곡 환영",
"sound_tag":"01 / 음악", "sound_title":"록, 펑크<br>&amp; 메탈.", "sound_intro":"삿포로에서 음악을 즐길 바를 찾고 계신가요? 스스키노의 록 바 FxxK Up에서는 록, 펑크, 메탈을 중심으로 틀고, 어떤 밤에는 덥, 레게, 블루스 등 다양한 음악도 들려드립니다. 그날의 분위기에 따라 선곡하며 신청곡도 환영합니다.", "sound_aria":"음악 장르", "genre_rock":"록", "genre_rock_desc":"함께 따라 부를 후렴, 익숙한 리프, 그리고 가끔은 예상 밖의 한 곡.", "genre_punk":"펑크", "genre_punk_desc":"빠르고 솔직한 사운드로 공간의 분위기를 깨웁니다.", "genre_metal":"메탈", "genre_metal_desc":"묵직한 기타와 깊은 그루브. 듣고 싶은 곡도 신청해 주세요.",
"team_tag":"02 / 플레이리스트 뒤편", "team_title":"네 사람의 취향.<br>하나의 공간.", "mixer_aria":"서로 다른 네 가지 음악 취향을 나타내는 믹서 채널", "mix_top":"라이브 믹스 / 4채널", "mix_right":"매일 다른 조합", "mix_roots":"루츠", "mix_leftfield":"실험음악", "mix_indie":"인디", "mix_heavy":"헤비", "mix_footer":"네 가지 취향 / 하나의 공간", "team_p1":"바에 누가 서 있느냐에 따라 플레이리스트도 달라집니다. 각자 음악 취향이 달라서 밤마다 사운드에 새로운 색이 더해집니다.", "team_p2":"좋아하는 밴드 이야기를 나누고, 지금 나오는 곡을 물어보고, 듣고 싶은 음악을 신청해 보세요. 음악 이야기가 이어지는 것도 이곳의 즐거움입니다.", "nori_tag":"01 / 펑크의 뿌리", "nori_desc":"80·90·2000년대 펑크를 좋아합니다. 레게, 블루스, 클래식 록도 즐겨 들어요.", "chuck_tag":"02 / 언더그라운드", "chuck_desc":"언더그라운드와 아방가르드 음악을 좋아합니다. 대중음악은 조금 어려워하지만 클래식에는 애정이 있어요.", "haruka_tag":"03 / 열린 귀", "haruka_desc":"인디 록과 클래식 록, 그리고 새로운 음악을 발견하는 걸 좋아합니다.", "kanata_tag":"04 / 묵직한 사운드", "kanata_desc":"모던 스래시와 메탈, 묵직한 음악이라면 무엇이든 좋아합니다. 더 많은 리프, 더 큰 볼륨으로.",
"request_art_index":"NO. 001 / 손님의 선곡", "request_art_title":"신청곡<br>환영합니다<br><em>당신의 한 곡.</em>", "request_art_footer":"듣고 싶은 곡 / 당신의 선택", "request_tag":"03 / 당신의 신청곡", "request_title":"듣고 싶은 곡이<br>있나요<span class=\"accent\">?</span>", "request_desc":"신청곡을 환영합니다. Nori나 Chuck에게 오늘 듣고 싶은 음악을 편하게 알려주세요. 가능한 한 플레이리스트에 담아볼게요.", "come_find":"찾아오는 길", "next_tag":"04 / 오늘 밤을 즐겨요", "next_title":"좋은 음악.<br>좋은 위스키.", "next_desc":"한 병을 고르고, 한 곡을 고르고, 6층으로 올라오세요.", "whisky_link":"위스키 리스트 보기", "find_link":"스스키노에서 찾아오기", "footer_line":"록 / 펑크 / 메탈 / 삿포로 스스키노", "back_top":"맨 위로 ↑", "privacy":"개인정보 보호", "mobile_directions":"찾아오기", "languages_aria":"음악 페이지 언어", "language_summary":"한국어"
},
"th": {
"nav_bar":"เกี่ยวกับบาร์", "nav_music":"ดนตรี", "nav_whisky":"วิสกี้", "nav_find":"แผนที่", "nav_aria":"เมนูหลัก",
"eyebrow":"ค่ำคืนในซัปโปโร / ดนตรี", "h1":"มิวสิกบาร์<br>ในซัปโปโร<span class=\"accent\">.</span>", "hero_line":"ร็อก พังก์<br>เมทัล เลือกเพลงได้ตามใจ", "hero_desc":"Rock Bar FxxK Up บาร์ร็อกในซูซูกิโนะ เพลงที่เปิดเปลี่ยนไปตามคนที่อยู่หลังเคาน์เตอร์ ถ้ามีเพลงที่อยากฟัง ขอเพลงกับเราได้เลย", "hero_cta":"ฟังเสียงของ FxxK Up", "directions":"ดูเส้นทาง", "meta_genres":"ร็อก / พังก์ / เมทัล", "meta_requests":"ขอเพลงได้",
"art_aria":"ร็อก พังก์ เมทัล ด้าน A และด้าน B", "art_location":"ซูซูกิโนะ / ซัปโปโร", "art_side":"ด้าน A / ด้าน B", "art_title":"เสียงเพลง<br>เปลี่ยนไปตาม<br><em>ค่ำคืนนี้</em>", "ticker":"ร็อก / พังก์ / เมทัล / ขอเพลงได้",
"sound_tag":"01 / เสียงดนตรี", "sound_title":"ร็อก พังก์<br>&amp; เมทัล", "sound_intro":"กำลังมองหาบาร์เพลงในซัปโปโรอยู่หรือเปล่า? FxxK Up คือบาร์ร็อกในซูซูกิโนะที่เปิดร็อก พังก์ และเมทัล บางคืนก็มีดั๊บ เร็กเก้ บลูส์ และแนวอื่น ๆ ตามบรรยากาศของค่ำคืนนั้น เรายินดีรับคำขอเพลงด้วย", "sound_aria":"แนวดนตรี", "genre_rock":"ร็อก", "genre_rock_desc":"ท่อนฮุกที่ร้องตามได้ ริฟฟ์คุ้นหู และบางครั้งก็มีเพลงที่คาดไม่ถึง", "genre_punk":"พังก์", "genre_punk_desc":"จังหวะเร็ว ตรงไปตรงมา ปลุกบรรยากาศให้คึกคัก", "genre_metal":"เมทัล", "genre_metal_desc":"กีตาร์หนักแน่น กรูฟลึก ๆ ขอเพลงที่อยากฟังได้เลย",
"team_tag":"02 / เบื้องหลังเพลย์ลิสต์", "team_title":"สี่คนสี่รสนิยม.<br>พื้นที่เดียวกัน.", "mixer_aria":"ช่องมิกเซอร์สี่ช่องแทนรสนิยมดนตรีที่แตกต่างกันของทีม", "mix_top":"ไลฟ์มิกซ์ / 4 แชนเนล", "mix_right":"แต่ละคืนไม่ซ้ำกัน", "mix_roots":"รากดนตรี", "mix_leftfield":"นอกกระแส", "mix_indie":"อินดี้", "mix_heavy":"หนักแน่น", "mix_footer":"สี่รสนิยม / ห้องเดียวกัน", "team_p1":"เพลย์ลิสต์เปลี่ยนไปตามคนที่อยู่หลังเคาน์เตอร์ แต่ละคนมีรสนิยมทางดนตรีไม่เหมือนกัน ทำให้เสียงของแต่ละค่ำคืนเปลี่ยนไปเสมอ", "team_p2":"ชวนคุยเรื่องวงโปรด ถามว่าเพลงที่เปิดอยู่คือเพลงอะไร หรือขอเพลงที่อยากฟังได้เลย บทสนทนาเรื่องดนตรีก็เป็นส่วนหนึ่งของค่ำคืนที่นี่", "nori_tag":"01 / รากพังก์", "nori_desc":"ชอบพังก์ยุค 80s, 90s และ 2000s รวมถึงเร็กเก้ บลูส์ และคลาสสิกร็อก", "chuck_tag":"02 / ใต้ดินและนอกกรอบ", "chuck_desc":"ชอบดนตรีใต้ดินและแนวอาวองการ์ด ไม่ค่อยถูกกับเพลงป๊อป แต่ยังชื่นชอบเพลงคลาสสิก", "haruka_tag":"03 / เปิดหูฟัง", "haruka_desc":"ชอบอินดี้ร็อก คลาสสิกร็อก และการค้นพบเพลงใหม่ ๆ", "kanata_tag":"04 / สายหนัก", "kanata_desc":"ชอบโมเดิร์นแทรช เมทัล และดนตรีหนัก ๆ ทุกแบบ ริฟฟ์แน่น เสียงดังเต็มที่",
"request_art_index":"NO. 001 / เพลงที่แขกเลือก", "request_art_title":"ยินดีรับ<br>คำขอเพลง<br><em>เพลงของคุณ</em>", "request_art_footer":"เพลงที่อยากฟัง / คุณเลือกได้", "request_tag":"03 / เพลงที่คุณอยากฟัง", "request_title":"มีเพลงที่อยาก<br>ฟังไหม<span class=\"accent\">?</span>", "request_desc":"เรายินดีรับคำขอเพลง บอก Nori หรือ Chuck ได้เลยว่าคืนนี้อยากฟังอะไร เราจะพยายามเปิดให้", "come_find":"แวะมาหาเรา", "next_tag":"04 / สนุกกับค่ำคืนนี้", "next_title":"ดนตรีดี ๆ<br>วิสกี้ชั้นดี", "next_desc":"เลือกวิสกี้สักขวด เลือกเพลงสักเพลง แล้วขึ้นมาที่ชั้น 6", "whisky_link":"ดูรายการวิสกี้", "find_link":"มาหาเราในซูซูกิโนะ", "footer_line":"ร็อก / พังก์ / เมทัล / ซูซูกิโนะ ซัปโปโร", "back_top":"กลับขึ้นด้านบน ↑", "privacy":"นโยบายความเป็นส่วนตัว", "mobile_directions":"ดูเส้นทาง", "languages_aria":"ภาษาในหน้าดนตรี", "language_summary":"ไทย"
},
"zh-Hans": {
"nav_bar":"酒吧介绍", "nav_music":"音乐", "nav_whisky":"威士忌", "nav_find":"到店路线", "nav_aria":"主导航",
"eyebrow":"札幌夜生活 / 音乐", "h1":"札幌音乐酒吧<span class=\"accent\">。</span>", "hero_line":"摇滚、朋克。<br>金属乐。今晚听什么？", "hero_desc":"Rock Bar FxxK Up 是薄野的一家摇滚酒吧。驻吧成员不同，播放的音乐也会变化。想听哪首歌，欢迎告诉我们。", "hero_cta":"聆听 FxxK Up 的声音", "directions":"查看路线", "meta_genres":"摇滚 / 朋克 / 金属", "meta_requests":"欢迎点歌",
"art_aria":"摇滚、朋克、金属乐。唱片 A 面与 B 面。", "art_location":"薄野 / 札幌", "art_side":"A 面 / B 面", "art_title":"每个夜晚<br>都有不同的<br><em>音乐。</em>", "ticker":"摇滚 / 朋克 / 金属 / 欢迎点歌",
"sound_tag":"01 / 音乐风格", "sound_title":"摇滚、朋克<br>与金属乐。", "sound_intro":"在札幌寻找音乐酒吧吗？薄野的 Rock Bar FxxK Up 以摇滚、朋克和金属乐为主。有些晚上也会播放 Dub、雷鬼、蓝调等其他风格，一切随当晚氛围而变。欢迎向我们点歌。", "sound_aria":"音乐风格", "genre_rock":"摇滚", "genre_rock_desc":"熟悉的副歌、耳熟的 riff，偶尔来一首意想不到的歌。", "genre_punk":"朋克", "genre_punk_desc":"快速、直接，让整个空间都醒过来的声音。", "genre_metal":"金属乐", "genre_metal_desc":"厚重的吉他与深沉的律动，也欢迎点一首你想听的歌。",
"team_tag":"02 / 播放列表背后", "team_title":"四种耳朵。<br>同一个空间。", "mixer_aria":"代表四位成员不同音乐品味的四条混音轨道", "mix_top":"现场混音 / 4 个频道", "mix_right":"每晚都不一样", "mix_roots":"根源", "mix_leftfield":"先锋", "mix_indie":"独立", "mix_heavy":"重型", "mix_footer":"四种品味 / 同一个房间", "team_p1":"播放列表会随着吧台后的成员而变化。每个人的音乐口味都不一样，所以每个夜晚的声音也会有所不同。", "team_p2":"聊聊喜欢的乐队，问问正在播放的歌，或点一首想听的音乐。音乐也会成为开启交流的话题。", "nori_tag":"01 / 朋克根源", "nori_desc":"喜欢 80、90 和 2000 年代的朋克，也喜欢雷鬼、蓝调和经典摇滚。", "chuck_tag":"02 / 地下与先锋", "chuck_desc":"偏爱地下与先锋音乐，对流行音乐有点过敏，但经典作品除外。", "haruka_tag":"03 / 开放聆听", "haruka_desc":"喜欢独立摇滚、经典摇滚，也乐于发现新音乐。", "kanata_tag":"04 / 重型到底", "kanata_desc":"喜欢现代鞭击金属、金属乐，以及各种重型音乐。更多 riff，更大音量。",
"request_art_index":"NO. 001 / 来宾点歌", "request_art_title":"欢迎<br>点歌<br><em>选一首吧。</em>", "request_art_footer":"你想听的歌 / 由你决定", "request_tag":"03 / 点一首你想听的歌", "request_title":"今晚想听<br>哪首歌<span class=\"accent\">？</span>", "request_desc":"欢迎点歌。告诉 Nori 或 Chuck 今晚想听什么，我们会尽量安排进播放列表。", "come_find":"来酒吧坐坐", "next_tag":"04 / 让夜晚继续", "next_title":"好音乐。<br>好威士忌。", "next_desc":"选一瓶酒，选一首歌，来大楼 6 楼找我们。", "whisky_link":"查看威士忌清单", "find_link":"前往薄野酒吧", "footer_line":"摇滚 / 朋克 / 金属 / 札幌薄野", "back_top":"返回顶部 ↑", "privacy":"隐私政策", "mobile_directions":"查看路线", "languages_aria":"音乐页面语言", "language_summary":"简体中文"
}}

TARGETS = {
"genre_rock":'//article[contains(@class,"sound-row")][1]/h3', "genre_rock_desc":'//article[contains(@class,"sound-row")][1]/p', "genre_punk":'//article[contains(@class,"sound-row")][2]/h3', "genre_punk_desc":'//article[contains(@class,"sound-row")][2]/p', "genre_metal":'//article[contains(@class,"sound-row")][3]/h3', "genre_metal_desc":'//article[contains(@class,"sound-row")][3]/p',
"nav_bar":'//header/nav/a[1]', "nav_music":'//header/nav/a[2]', "nav_whisky":'//header/nav/a[3]', "nav_find":'//header/nav/a[4]',
"eyebrow":'//section[contains(@class,"music-hero")]//div[contains(@class,"eyebrow")]/span[2]', "h1":'//*[@id="page-title"]', "hero_line":'//p[contains(@class,"music-hero-line")]', "hero_desc":'//p[contains(@class,"music-hero-desc")]', "hero_cta":'//div[contains(@class,"music-hero-actions")]/a[1]', "directions":'//div[contains(@class,"music-hero-actions")]/a[2]', "meta_genres":'//div[contains(@class,"hero-meta")]/span[1]', "meta_requests":'//div[contains(@class,"hero-meta")]/span[2]',
"art_location":'//div[contains(@class,"music-art-top")]/span[2]', "art_side":'//div[contains(@class,"music-art-bottom")]/span', "art_title":'//div[contains(@class,"music-art-bottom")]/strong', "ticker":'//div[contains(@class,"music-ticker")]/div',
"sound_tag":'//section[@id="sound"]/div[contains(@class,"section-tag")]', "sound_title":'//section[@id="sound"]//h2', "sound_intro":'//section[@id="sound"]//div[contains(@class,"music-section-head")]/p', "sound_aria":'//div[contains(@class,"sound-list")]',
"team_tag":'//section[contains(@class,"music-team")]/div[contains(@class,"section-tag")]', "team_title":'//h2[contains(@class,"team-headline")]', "mixer_aria":'//div[contains(@class,"team-mix-art")]', "mix_top":'//div[contains(@class,"team-mix-top")]/span[1]', "mix_right":'//div[contains(@class,"team-mix-top")]/span[2]', "mix_roots":'//div[contains(@class,"mixer-channel")][1]/span', "mix_leftfield":'//div[contains(@class,"mixer-channel")][2]/span', "mix_indie":'//div[contains(@class,"mixer-channel")][3]/span', "mix_heavy":'//div[contains(@class,"mixer-channel")][4]/span', "mix_footer":'//div[contains(@class,"team-mix-footer")]', "team_p1":'//div[contains(@class,"music-team-copy")]/p[1]', "team_p2":'//div[contains(@class,"music-team-copy")]/p[2]',
"nori_tag":'//article[contains(@class,"taste-card")][1]/span', "nori_desc":'//article[contains(@class,"taste-card")][1]/p', "chuck_tag":'//article[contains(@class,"taste-card")][2]/span', "chuck_desc":'//article[contains(@class,"taste-card")][2]/p', "haruka_tag":'//article[contains(@class,"taste-card")][3]/span', "haruka_desc":'//article[contains(@class,"taste-card")][3]/p', "kanata_tag":'//article[contains(@class,"taste-card")][4]/span', "kanata_desc":'//article[contains(@class,"taste-card")][4]/p',
"request_art_index":'//div[contains(@class,"request-art")]/span[contains(@class,"request-art-index")]', "request_art_title":'//div[contains(@class,"request-art")]/strong', "request_art_footer":'//div[contains(@class,"request-art")]/span[contains(@class,"request-art-footer")]', "request_tag":'//div[contains(@class,"request-copy")]/div[contains(@class,"section-tag")]', "request_title":'//*[@id="request-title"]', "request_desc":'//div[contains(@class,"request-copy")]/p', "come_find":'//div[contains(@class,"request-copy")]/a',
"next_tag":'//section[contains(@class,"music-next")]//div[contains(@class,"section-tag")]', "next_title":'//section[contains(@class,"music-next")]//h2', "next_desc":'//section[contains(@class,"music-next")]//p', "whisky_link":'//div[contains(@class,"music-next-actions")]/a[1]', "find_link":'//div[contains(@class,"music-next-actions")]/a[2]', "footer_line":'//footer[contains(@class,"music-footer")]/span[2]', "back_top":'//footer[contains(@class,"music-footer")]/a[1]', "privacy":'//footer[contains(@class,"music-footer")]/a[2]', "mobile_directions":'//div[contains(@class,"mobile-bar")]/a[1]'
}

def set_inner(node, value):
    icon = node.find("svg") if node.tag == "a" else None
    for child in list(node):
        if child is not icon:
            node.remove(child)
    node.text = None
    if icon is not None:
        node.insert(0, icon)
        icon.tail = value
    else:
        for frag in html.fragments_fromstring(value):
            if isinstance(frag, str):
                if len(node): node[-1].tail = (node[-1].tail or "") + frag
                else: node.text = (node.text or "") + frag
            else: node.append(frag)

def page_path(lang):
    return DIST / ("music/index.html" if lang == "en" else f"{lang.lower()}/music/index.html")

base = html.document_fromstring(SOURCE.read_text())
for node in base.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," draft-banner ")]'):
    node.getparent().remove(node)
css_link = base.xpath('//head/link[@href="/music/music.css"]')
if css_link: css_link[0].set("href", "/music/music.css")

for lang in LANGUAGES:
    doc = deepcopy(base)
    doc.set("lang", lang)
    head = doc.find("head")
    title = {
        "en":"Music Bar in Sapporo | Rock, Punk & Metal | Rock Bar FxxK Up",
        "ja":"札幌・すすきのの音楽バー｜ロック・パンク・メタル｜Rock Bar FxxK Up",
        "ko":"삿포로 스스키노 뮤직 바 | 록·펑크·메탈 | Rock Bar FxxK Up",
        "th":"มิวสิกบาร์ในซัปโปโร | ร็อก พังก์ เมทัล | Rock Bar FxxK Up",
        "zh-Hans":"札幌薄野音乐酒吧｜摇滚、朋克与金属乐｜Rock Bar FxxK Up"}[lang]
    desc = {
        "en":"Looking for a music bar in Sapporo? Rock Bar FxxK Up in Susukino plays rock, punk and metal. Song requests welcome. Find us on the 6th floor.",
        "ja":"札幌・すすきのの音楽バー、Rock Bar FxxK Up。ロック、パンク、メタルを中心に、曲のリクエストも歓迎。21時オープン、6階。",
        "ko":"삿포로 스스키노의 음악 바 Rock Bar FxxK Up. 록, 펑크, 메탈을 중심으로 신청곡도 환영합니다. 매일 21시 오픈, 6층.",
        "th":"กำลังมองหามิวสิกบาร์ในซัปโปโรหรือเปล่า? Rock Bar FxxK Up ในซูซูกิโนะเปิดเพลงร็อก พังก์ และเมทัล ขอเพลงได้ เปิด 21:00 อยู่ชั้น 6",
        "zh-Hans":"在札幌寻找音乐酒吧？薄野的 Rock Bar FxxK Up 以摇滚、朋克和金属乐为主，也欢迎点歌。每晚 21:00 营业，位于 6 楼。"}[lang]
    title_node = head.find("title")
    ga = etree.Element("script")
    ga.text = "window.dataLayer=window.dataLayer||[];window.gtag=window.gtag||function(){dataLayer.push(arguments);};if(['rockbarfxxkup.com','www.rockbarfxxkup.com'].includes(location.hostname)){gtag('js',new Date());gtag('config','G-JPYT9JRWBT',{allow_google_signals:false,allow_ad_personalization_signals:false});const analyticsScript=document.createElement('script');analyticsScript.async=true;analyticsScript.src='https://www.googletagmanager.com/gtag/js?id=G-JPYT9JRWBT';document.head.appendChild(analyticsScript);}"
    head.insert(0, ga)
    etree.SubElement(head, "script", src="/analytics.js", defer="defer")
    title_node.text = title
    font = head.xpath('link[contains(@href,"fonts.googleapis.com")]')
    if font:
        families = "family=Barlow+Condensed:wght@600;700;800;900&family=DM+Sans:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;600;800&family=Noto+Sans+KR:wght@400;600;800&family=Noto+Sans+Thai:wght@400;600;800&family=Noto+Sans+SC:wght@400;600;800&display=swap"
        font[0].set("href", "https://fonts.googleapis.com/css2?" + families)
    for m in head.xpath('meta[@name="description"]'): head.remove(m)
    robots = head.xpath('meta[@name="robots"]')
    if robots: robots[0].set("content", "index,follow,max-image-preview:large")
    else: etree.SubElement(head, "meta", name="robots", content="index,follow,max-image-preview:large")
    etree.SubElement(head, "meta", name="description", content=desc)
    for el in head.xpath('link[@rel="canonical"]|link[@rel="alternate"]|meta[starts-with(@property,"og:")]|meta[starts-with(@name,"twitter:")]|script[@type="application/ld+json"]'):
        head.remove(el)
    etree.SubElement(head, "link", rel="canonical", href=ROUTES[lang])
    for other in LANGUAGES:
        etree.SubElement(head, "link", rel="alternate", hreflang=other, href=ROUTES[other])
    etree.SubElement(head, "link", rel="alternate", hreflang="x-default", href=ROUTES["en"])
    og = {"type":"website", "site_name":"Rock Bar FxxK Up", "title":title, "description":desc, "url":ROUTES[lang], "image":ORIGIN+"/assets/neon-social-preview.jpg"}
    for name, value in og.items(): etree.SubElement(head, "meta", property="og:"+name, content=value)
    etree.SubElement(head, "meta", name="twitter:card", content="summary_large_image")
    etree.SubElement(head, "meta", name="twitter:title", content=title)
    etree.SubElement(head, "meta", name="twitter:description", content=desc)
    etree.SubElement(head, "meta", name="twitter:image", content=ORIGIN+"/assets/neon-social-preview.jpg")
    schema = {"@context":"https://schema.org", "@type":"WebPage", "@id":ROUTES[lang]+"#webpage", "url":ROUTES[lang], "name":title, "description":desc, "inLanguage":lang, "isPartOf":{"@id":ORIGIN+"/#website"}, "about":{"@id":ORIGIN+"/#bar"}}
    etree.SubElement(head, "script", type="application/ld+json").text = json.dumps(schema, ensure_ascii=False)

    # A native-language selector keeps all five music routes one click apart.
    header_actions = doc.xpath('//header/div[contains(@class,"header-actions")]')[0]
    old_language = header_actions.xpath('./span[contains(@class,"preview-language")]')
    if old_language: header_actions.remove(old_language[0])
    switch = etree.Element("details", **{"class":"music-language-menu"})
    summary = etree.SubElement(switch, "summary", **{"aria-label": (COPY[lang]["languages_aria"] if lang != "en" else "Music page language")})
    summary.text = (COPY[lang]["language_summary"] if lang != "en" else "ENGLISH")
    options = etree.SubElement(switch, "nav", **{"class":"music-language-options", "aria-label": (COPY[lang]["languages_aria"] if lang != "en" else "Music page language")})
    for other in LANGUAGES:
        a = etree.SubElement(options, "a", href=ROUTES[other], hreflang=other, lang=other)
        if other == lang: a.set("aria-current", "page")
        a.text = LABELS[other]
    header_actions.insert(0, switch)

    if lang != "en":
        for key, value in COPY[lang].items():
            if key in TARGETS and key not in ("sound_aria", "mixer_aria"):
                found = doc.xpath(TARGETS[key])
                if not found: raise RuntimeError(f"Missing {key} target for {lang}")
                set_inner(found[0], value)
        for nav in doc.xpath('//header/nav'): nav.set("aria-label", COPY[lang]["nav_aria"])
        for el, aria_key in [("//div[contains(@class,'music-hero-art')]", "art_aria"), ("//div[contains(@class,'team-mix-art')]", "mixer_aria"), ("//div[contains(@class,'sound-list')]", "sound_aria")]:
            item = doc.xpath(el)
            if item: item[0].set("aria-label", COPY[lang][aria_key])
        # The visual mixer’s channel names are also translated without changing its motion.
        for i, key in enumerate(["mix_roots", "mix_leftfield", "mix_indie", "mix_heavy"], 1):
            doc.xpath(f'//div[contains(@class,"mixer-channel")][{i}]/span')[0].text = COPY[lang][key]
        # Native-language text in the animated request graphic.
        art = doc.xpath('//div[contains(@class,"request-art")]')[0]
        art.set("aria-hidden", "true")
    else:
        nav = doc.xpath('//header/nav')[0]
        nav.set("aria-label", "Main navigation")
        art = doc.xpath('//div[contains(@class,"request-art")]')[0]
        art.set("aria-hidden", "true")

    # Shared analytics.js sends these named actions with page_language on every route.
    events = [
        ('//header/nav/a[2]', 'music_section_open', 'main_navigation'),
        ('//header/nav/a[3]', 'whisky_page_open', 'main_navigation'),
        ('//header/nav/a[4]', 'find_us_click', 'main_navigation'),
        ('//div[contains(@class,"music-hero-actions")]/a[1]', 'music_section_open', 'hero'),
        ('//div[contains(@class,"music-hero-actions")]/a[2]', 'directions_click', 'hero'),
        ('//div[contains(@class,"request-copy")]/a', 'directions_click', 'song_request'),
        ('//div[contains(@class,"music-next-actions")]/a[1]', 'whisky_page_open', 'music_next'),
        ('//div[contains(@class,"music-next-actions")]/a[2]', 'find_us_click', 'music_next'),
        ('//header/a[contains(@class,"small-cta")]', 'instagram_click', 'header'),
        ('//div[contains(@class,"mobile-bar")]/a[1]', 'directions_click', 'mobile_bar'),
        ('//div[contains(@class,"mobile-bar")]/a[2]', 'instagram_click', 'mobile_bar')]
    for path, event, placement in events:
        for link in doc.xpath(path):
            link.set("data-track-event", event)
            link.set("data-track-placement", placement)
            if event == "instagram_click": link.set("data-track-destination", "bar")
    for link in doc.xpath('//nav[contains(@class,"music-language-options")]/a'):
        link.set("data-language", link.get("hreflang"))
        link.set("data-track-event", "language_select")
        link.set("data-track-placement", "language_menu")

    # Preserve official names and the established brand across localizations.
    # Every language links to its own translated whisky menu.
    whisky = doc.xpath('//a[contains(@class,"music-next-actions")]/@href')
    local_root = "/" if lang == "en" else f"/{lang.lower()}/"
    nav_links = doc.xpath('//header/nav/a')
    if lang != "en":
        nav_links[0].set("href", local_root + "#about")
        nav_links[3].set("href", local_root + "#visit")
        doc.xpath('//header/a[contains(@class,"brand")]')[0].set("href", local_root)
    for a in doc.xpath('//header/nav/a[3] | //div[contains(@class,"music-next-actions")]/a[1]'):
        a.set("href", "/whisky/" if lang == "en" else f"/{lang.lower()}/whisky/")
    if lang != "en":
        doc.xpath('//div[contains(@class,"music-next-actions")]/a[2]')[0].set("href", local_root + "#visit")
    out = page_path(lang)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("<!doctype html>\n" + html.tostring(doc, encoding="unicode", method="html"))

(DIST / "music/music.css").write_text(SOURCE_CSS.read_text())

# Add all five music routes, with language alternates, to the existing sitemap.
sitemap = etree.parse(str(DIST / "sitemap.xml"))
root = sitemap.getroot()
ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
xns = "http://www.w3.org/1999/xhtml"
for old in list(root):
    loc = old.xpath('./s:loc/text()', namespaces={"s":ns})
    if loc and loc[0].endswith("/music/"):
        root.remove(old)
for lang in LANGUAGES:
    item = etree.SubElement(root, "{"+ns+"}url")
    etree.SubElement(item, "{"+ns+"}loc").text = ROUTES[lang]
    for other in LANGUAGES:
        etree.SubElement(item, "{"+xns+"}link", rel="alternate", hreflang=other, href=ROUTES[other])
    etree.SubElement(item, "{"+xns+"}link", rel="alternate", hreflang="x-default", href=ROUTES["en"])
(DIST / "sitemap.xml").write_bytes(etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True))
print("Built English, Japanese, Korean, Thai and Simplified Chinese music pages with localized metadata and sitemap alternates.")
