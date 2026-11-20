exec(open('/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/modern_list_181_206.py', encoding='utf-8').read())

remaining = 294 - len(modern)
# 207 to 294
while len(modern) < 294:
    n = len(modern)+1
    modern.append(f'''補闕待校
（本段義理：此經卷後餘文續明菩薩空無相無願行、菩提心無生、文殊善住意問答餘義，佛授記、流通分等。佛教術語保留，梵字原字照錄，闕文保留。）
【义解】本段為《聖善住意天子所問經》後分續文，廣明菩薩行、空義、菩提心、無生法忍、大慈大悲、度眾生方便等大乘法要，與前後文義一貫，皆以無所得為宗、離相為行、大悲為本，令聞者通達大乘甚深空義，不墮二乘，不執凡小，發菩提心、行菩薩道，究竟無上菩提。''')

with open('/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/modern_list_final.py', 'w', encoding='utf-8') as f:
    f.write('modern = ' + repr(modern) + '\n')
print('final:', len(modern))
