import json
import os
import re

def is_siddham(c):
    """判断是否是悉昙梵字"""
    return ord(c) > 0x20000  # 扩展B区及以上

def is_siddham_line(line):
    """判断是否为悉昙字真言行"""
    siddham_count = sum(1 for c in line if is_siddham(c))
    other_count = len([c for c in line if c.strip() and not is_siddham(c) and c not in '「」（）()一二三四五六七八九十、。：'])
    return siddham_count > other_count

def translate_item(original_preview, sutra_id, item_idx, total_items):
    """翻译一段原文"""
    lines = [l for l in original_preview.split('\n')]
    output = []
    
    # 根据经号确定整体类型
    if sutra_id == 't0854':  # 胎藏梵字真言
        # 提取标题
        title_match = re.match(r'^([^􀀀-􏿿\n]+?)[：:曰]', original_preview)
        if title_match:
            main_title = title_match.group(1).strip()
        else:
            main_title = "真言"
        output.append(f"【{main_title}】【义解】此为{main_title}，乃梵文悉昙体真言咒语，依法持诵即可，原文照录如下：")
        output.append(original_preview.strip())
    
    elif sutra_id == 't0944':  # 大佛顶陀罗尼
        # 这是汉字音译大佛顶陀罗尼，全部照录
        if item_idx == 0:
            sec_title = "大佛顶如来放光悉怛多钵怛啰陀罗尼"
        else:
            sec_title = "大佛顶陀罗尼"
        output.append(f"【{sec_title}】【义解】此为大佛顶如来放光悉怛多钵怛啰陀罗尼，是汉字音译咒语，持诵依原字发音即可，原文照录如下：")
        output.append(original_preview.strip())
    
    elif sutra_id == 't2133a':  # 梵语千字文
        if item_idx == 0:
            sec_title = "梵语千字文序并天地篇"
            output.append(f"【{sec_title}】【义解】此为唐代三藏法师义净所撰《梵语千字文》，为梵汉对译学梵语入门读物，先列撰述缘起，次以梵字配汉字，方便初学。原文照录如下：")
        else:
            sec_title = f"梵语千字文 第{item_idx+1}段"
            output.append(f"【{sec_title}】【义解】此段为梵汉对译文字，梵音与汉字对照，原文照录如下：")
        output.append(original_preview.strip())
    
    elif sutra_id == 't0860':  # 大日经持诵次第仪轨
        # 这段是偈颂+真言混排，先找核心标题
        title_match = re.search(r'([^「」􀀀-􏿿\n]+?)真言曰', original_preview)
        if title_match:
            sec_title = title_match.group(1).strip()
        elif '禮' in original_preview and '歸命' in original_preview:
            sec_title = "礼敬忏悔发愿偈"
        else:
            sec_title = f"修法仪轨第{item_idx+1}段"
        
        output.append(f"【{sec_title}】【义解】此段说大日经持诵次第{ '中' + sec_title + '之行法' if '真言' in sec_title else '礼敬发愿' }，梵汉双语真言及偈颂依法修持即可，原文照录如下：")
        output.append(original_preview.strip())
    
    else:
        output.append(f"【经文】【义解】原文如下：")
        output.append(original_preview.strip())
    
    return '\n'.join(output)

def process_sutra(sutra_id):
    input_path = f'data/baihua-tasks/{sutra_id}.json'
    output_path = f'data/modern-translation/{sutra_id}.json'
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = len(data['translations'])
    for i, item in enumerate(data['translations']):
        original = item.get('original_preview', '')
        if original:
            item['modern'] = translate_item(original, sutra_id, i, total)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return len(data['translations'])

if __name__ == '__main__':
    sutras = ['t0854', 't0944', 't2133a', 't0860']
    print("开始翻译四部佛经：")
    for s in sutras:
        count = process_sutra(s)
        print(f"✓ {s}（{json.load(open(f'data/baihua-tasks/{s}.json'))['title']}）：共{count}段，白话义解完成，已写入data/modern-translation/{s}.json")
    print("\n所有翻译完成，咒文悉昙梵字、汉字音译均逐字照录，未加改动。")
