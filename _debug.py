import sys; sys.path.insert(0,'/home/user/workspace/13511660557912876654/buddhist-ontology')
import importlib.util
spec=importlib.util.spec_from_file_location('_check','/home/user/workspace/13511660557912876654/buddhist-ontology/_check.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
body='若自中毒，当正念作五字观，以󰚨诃字从顶趁之，结莾羯罗等三印散身上差矣。五字观者，贺空顶、唵火心、跛水脐、莎嚩（二合）风膝、佉使（二合）地脚下。迦楼罗纵日毒法（白月十四日为之），但日光所及皆効，千里万里益验。'
i=67
non_sidd=0
while i<len(body):
    c=body[i]
    prose=m._is_prose_start_at(body,i)
    keep=c in m.MANTRA_KEEP_ORIG
    sid=m._is_siddham_char(c)
    print(f'i={i} c={repr(c)} prose={prose} keep={keep} sidd={sid} non_sidd={non_sidd}')
    if prose: print('  BREAK prose'); break
    if c in ' \t\u3000、0123456789．.·\n': i+=1; continue
    if c in '（）()': i+=1; continue
    if c in '「＂"':
        after=body[i+1:i+5]
        kw_l=['世尊','佛言','佛告','若诸','若有','尔时','这时','是时','你今','我今','善男','善女','大王','当知','是名','我当','汝今','我常','尔时','我于','彼诸','汝等','我已','若人']
        if any(after.startswith(k) for k in kw_l): print('  BREAK open quote'); break
        i+=1; continue
    if c in '」＂"': print('  BREAK close'); break
    if keep or sid: non_sidd=0; i+=1; continue
    if '\u4e00'<=c<='\u9fff':
        non_sidd+=1
        if non_sidd>=3: print('  BREAK non_sidd'); break
        i+=1; continue
    i+=1
print(f'final i={i}')
