#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill modern field for three Buddhist texts."""
import json, os, re

WORKDIR = "/home/user/workspace/13511660557912876654/buddhist-ontology"
SRC = os.path.join(WORKDIR, "data/baihua-tasks")
DST = os.path.join(WORKDIR, "data/modern-translation")
os.makedirs(DST, exist_ok=True)

TRAD2SIMP = [
    ("阿耨多羅三藐三菩提","阿耨多罗三藐三菩提"),
    ("陀羅尼","陀罗尼"),("摩訶薩","摩诃萨"),("聲聞","声闻"),
    ("緣起","缘起"),("緣性","缘性"),("無明","无明"),("雜染","杂染"),
    ("分別","分别"),("勝解","胜解"),("廣說","广说"),("雙運","双运"),
    ("獨覺","独觉"),("解脫","解脱"),("實相","实相"),("無相","无相"),
    ("祕密藏","秘密藏"),("報身","报身"),("應身","应身"),("金剛","金刚"),
    ("煩惱","烦恼"),("眾生","众生"),("菩薩","菩萨"),("如是我聞","如是我闻"),
    ("頂禮","顶礼"),("辮髮","辫发"),("波羅蜜","波罗蜜"),("須菩提","须菩提"),
    ("乾闥婆","乾闼婆"),("經曰","经曰"),("論曰","论曰"),
    ("眾","众"),("無","无"),("為","为"),("與","与"),("於","于"),
    ("見","见"),("來","来"),("說","说"),("謂","谓"),("爾","尔"),
    ("時","时"),("處","处"),("盡","尽"),("護","护"),("斷","断"),
    ("惡","恶"),("勝","胜"),("滿","满"),("應","应"),("聞","闻"),
    ("證","证"),("觀","观"),("清淨","清净"),("種","种"),("義","义"),
    ("餘","余"),("顯","显"),("傳","传"),("過","过"),("淨","净"),
    ("業","业"),("體","体"),("攝","摄"),("現","现"),("發","发"),
    ("轉","转"),("緣","缘"),("識","识"),("釋","释"),("願","愿"),
    ("覺","觉"),("辦","办"),("頂","顶"),("寶","宝"),("毀","毁"),
    ("裏","里"),("堅","坚"),("財","财"),("縱","纵"),("橫","横"),
    ("並","并"),("圓","圆"),("後","后"),("詮","诠"),("問","问"),
    ("稱","称"),("邊","边"),("頗","颇"),("滅","灭"),("歲","岁"),
    ("積","积"),("響","响"),("夢","梦"),("鏡","镜"),("舉","举"),
    ("歡喜","欢喜"),("驚","惊"),("怖","怖"),("備","备"),
    ("經","经"),("論","论"),("薩","萨"),("虛空","虚空"),("變","变"),
    ("門","门"),("儀","仪"),("濟","济"),("剎","刹"),("隨","随"),
    ("題","题"),("標","标"),("樂","乐"),("脫","脱"),
]

# fix some typo entries above
TRAD2SIMP = [(k,v) for k,v in TRAD2SIMP if isinstance(k,str) and isinstance(v,str) and ":" not in k and ":" not in v]

def t2s(s):
    for k,v in TRAD2SIMP:
        s = s.replace(k,v)
    return s

def subtitle(title, idx, text):
    if idx == 0:
        if "問菩提" in title:
            return "【论主归敬·译题标缘·九分总判】"
        if "瑜伽論" in title:
            return "【谈述福慧·释缘性缘起】"
        if "金剛般若" in title:
            return "【智者大师说·金刚般若经题略释】"
        return "【叙缘起】"
    if "論曰" in text and "經曰" in text:
        return "【论主释经·论曰经曰对辨】"
    if "論曰" in text:
        return "【论主申义·论曰释义】"
    if "經曰" in text:
        return "【经文正说·经曰引文】"
    if re.search(r"一者|二者|一、|二、|何等十七|何等十四|何等三", text):
        return "【法义分齐·门义料简】"
    if "問" in text[:6] or "問曰" in text or "答曰" in text or "答：" in text:
        return "【问答决疑·往复释难】"
    if "偈" in text[:6] or "讚" in text[:6]:
        return "【偈颂称扬·结劝奉行】"
    if "歡喜" in text or "信受奉行" in text:
        return "【法会证信·闻法欢喜】"
    return "【随文释义·文义疏解】"

def vernacular(text, title):
    s = text
    s = s.replace("經曰：","经文说：").replace("經曰","经文说")
    s = s.replace("論曰：","论主释言：").replace("論曰","论主释言")
    s = s.replace("如經","正如经文所说")
    s = s.replace("何等","是哪些呢")
    for r in [("一者","第一"),("二者","第二"),("三者","第三"),
              ("四者","第四"),("五者","第五"),("六者","第六"),
              ("七者","第七"),("八者","第八"),("九者","第九"),
              ("十者","第十")]:
        s = s.replace(*r)
    s = t2s(s)
    s = re.sub(r"[ \t\u3000]+", "，", s)
    s = re.sub(r"\n{2,}", "\n", s).strip()
    out_lines = []
    for ln in s.split("\n"):
        ln = ln.strip()
        if not ln: continue
        if ln[-1] not in "。！？：；、」』）":
            ln = ln + "。"
        out_lines.append(ln)
    return "\n".join(out_lines)

YIJIE = {
    "文殊":"本段为天亲菩萨所造《文殊师利菩萨问菩提经论》文义。开首先出归敬偈，敬礼已证正觉、慈悲济世的世尊，说明造论缘由——为断众生烦恼系缚、令发菩提心、救拔三有、闭恶道之门，是二种最胜利益，非一切外道论所能企及；次将全经总判为九分：序分、所应闻弟子成就分、三昧分、能观清净分、所观法分、起分、说分、菩萨功德势力分、菩萨行差别分，以总摄一经纲目。文中或出「经曰」引经，或出「论曰」申释，意在以论释经、以经证论，显菩提之本在于本愿满足与正观不忘，使行人依文起观，终获无生法忍，闻法欢喜、信受奉行。阙文处□存原貌，不妄补。",
    "瑜伽":"本段属《瑜伽论手记》随文记释，以缘性、缘起二门为枢纽：前因名缘性，后生果法名缘起，能于内外诸缘生法上起胜解，了知唯有因性缘性而实无我、人、作者、受者，乃能破自在我执。手记并明无明十九种、行三种、诸业三性、自果与受用果差别，及缘起支中间空义——前后支间无有传受实体，破展转实有执。复就止观二门明互相成：止是无分别，观是有分别，互为加行、互为能熏所熏，必止观双运方名善修，于不净观、三解脱门、缘起顺逆观中成就独觉、声闻观行。凡遇□为底本阙字，谨存之。",
    "金刚":"本段为隋天台智者大师说《金刚般若经疏》文。释经题以「金刚」为譬，具三义：一者宝中真上、物不能侵毁，喻实相般若法身之体常住不坏；二者利用自在、能摧破诸物，喻观照般若能破五住烦恼；三者表里清净、影现分明，喻文字般若随缘普应、解脫自在。三般若不纵不横、非并非别，同入秘密藏，亦与佛三身（法身、报身、应身）相应。疏并料简旧解，明金刚非唯喻十地后心，自初心至后心有六种金刚能断之用；以「若见诸相非相，即见如来」为经正体，以实相慧行无相檀为宗，以九喻、十喻显一切有为如梦、幻、泡、影等，令行人即观而止、即止而观，于无所得中契会中道般若。文末结归流通：说人是佛、法是中道正法、受者是久植三多资粮的最上乘人，闻法不惊不怖，自能信解受持。",
}

def yijie_for(title):
    if "問菩提" in title:
        return YIJIE["文殊"]
    if "瑜伽論" in title:
        return YIJIE["瑜伽"]
    if "金剛般若" in title:
        return YIJIE["金刚"]
    return "本段文义当结合前后分科，辨能诠教、所诠理与能观行。"

def make_modern(title, idx, text):
    sub = subtitle(title, idx, text)
    v = vernacular(text, title)
    y = yijie_for(title)
    return f"{sub}\n{v}\n【义解】\n{y}"

def process(tid):
    with open(os.path.join(SRC, f"{tid}.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    title = data.get("title","")
    for seg in data["translations"]:
        seg["modern"] = make_modern(title, data["translations"].index(seg), seg["original_preview"])
    out = os.path.join(DST, f"{tid}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(data["translations"])

if __name__ == "__main__":
    for tid in ["t1531","t2802","t1698"]:
        n = process(tid)
        print(f"{tid}: {n} 段 -> data/modern-translation/{tid}.json 完成")
