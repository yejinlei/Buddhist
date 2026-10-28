import re
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 找到原来的renderGraph函数位置，替换为新版
new_render = '''        function renderGraph() {
            const activeTypes = Array.from(document.querySelectorAll('.node-filter:checked')).map(cb => cb.dataset.type);
            
            const nodes = [];
            const nodeMap = {};
            const links = [];
            
            const colorMap = {
                concept: '#1E4D2B',
                sutra: '#8B2500',
                buddha: '#DAA520',
                bodhisattva: '#DB7093',
                arhat: '#9370DB',
                master: '#2F4F4F',
                scholar: '#20B2AA',
                folk: '#CD853F',
                sect: '#4A148C',
                category: '#5D4037'
            };
            const nameMap = {
                concept: '义理概念', sutra: '经典', buddha: '佛', bodhisattva: '菩萨',
                arhat: '阿罗汉', master: '祖师/译师', scholar: '学者', folk: '民间人物',
                sect: '宗派', category: '部类'
            };
            
            // 添加概念节点
            if (activeTypes.includes('concept')) {
                ontologyData.concepts.forEach(c => {
                    const id = 'c_' + c.id;
                    nodes.push({
                        id: id, name: c.name, category: 'concept',
                        symbolSize: c.layer === 'L1' ? 28 : 20,
                        itemStyle: {color: colorMap.concept},
                        data: c
                    });
                    nodeMap[id] = c;
                });
            }
            
            // 添加人物节点
            if (activeTypes.includes('person')) {
                ontologyData.persons.forEach(p => {
                    const id = 'p_' + p.id;
                    nodes.push({
                        id: id, name: p.name, category: p.class,
                        symbolSize: p.class === 'buddha' ? 30 : (p.class === 'bodhisattva' ? 25 : 20),
                        itemStyle: {color: colorMap[p.class] || '#666'},
                        data: p
                    });
                    nodeMap[id] = p;
                });
            }
            
            // 添加宗派节点
            if (activeTypes.includes('sect')) {
                ontologyData.sects.forEach(s => {
                    const id = 's_' + s.id;
                    nodes.push({
                        id: id, name: s.name, category: 'sect',
                        symbolSize: 28,
                        itemStyle: {color: colorMap.sect},
                        data: s
                    });
                    nodeMap[id] = s;
                });
            }
            
            // 添加部类节点
            if (activeTypes.includes('category')) {
                ontologyData.categories.forEach(c => {
                    const id = 'ca_' + c.id;
                    nodes.push({
                        id: id, name: c.name, category: 'category',
                        symbolSize: Math.min(15 + c.count/8, 50),
                        itemStyle: {color: colorMap.category},
                        data: c
                    });
                    nodeMap[id] = c;
                });
            }
            
            // 添加经典节点
            if (activeTypes.includes('sutra')) {
                ontologyData.sutras.forEach(s => {
                    const id = 'su_' + s.id;
                    nodes.push({
                        id: id, name: s.name, category: 'sutra',
                        symbolSize: s.word_count > 100000 ? 22 : 16,
                        itemStyle: {color: colorMap.sutra},
                        data: s
                    });
                    nodeMap[id] = s;
                });
            }
            
            // 添加边，统一转换节点id前缀
            function getNodeId(type, rawId) {
                const prefix = {concept:'c_', person:'p_', sect:'s_', category:'ca_', sutra:'su_'};
                // 判断原始id前缀
                if (rawId.startsWith('c')) return 'c_' + rawId;
                if (rawId.startsWith('p')) return 'p_' + rawId;
                if (rawId.startsWith('sect')) return 's_' + rawId;
                if (rawId.startsWith('cat_')) return 'ca_' + rawId;
                if (rawId.startsWith('t')) return 'su_' + rawId;
                return rawId;
            }
            
            ontologyData.relations.forEach(r => {
                const sId = getNodeId('', r.source);
                const tId = getNodeId('', r.target);
                if (nodeMap[sId.split('_').slice(1).join('_')] || nodes.some(n => n.id === sId)) {
                    if (nodeMap[tId.split('_').slice(1).join('_')] || nodes.some(n => n.id === tId)) {
                        if (nodes.some(n => n.id === sId) && nodes.some(n => n.id === tId)) {
                            links.push({
                                source: sId,
                                target: tId,
                                label: {show: false, formatter: r.label, fontSize: 10},
                                lineStyle: {width: 1.2, opacity: 0.6, curveness: 0.1},
                                data: r
                            });
                        }
                    }
                }
            });
            
            const categories = Object.keys(colorMap).map(k => ({name: nameMap[k] || k, itemStyle: {color: colorMap[k]}}));
            
            const option = {
                tooltip: {
                    formatter: params => {
                        if (params.dataType === 'node') {
                            const d = params.data.data;
                            let html = `<div class="font-bold text-lg mb-1">${params.name}</div>`;
                            if (d.definition) html += `<div>${d.definition}</div>`;
                            if (d.core_doctrine) html += `<div>核心教义：${d.core_doctrine}</div>`;
                            if (d.translator) html += `<div>译者：${d.translator}</div>`;
                            if (d.count) html += `<div>本类共 ${d.count} 部经</div>`;
                            return html;
                        } else {
                            return `<b>${params.data.data.label}</b><br/>${params.data.data.description || ''}`;
                        }
                    }
                },
                legend: [{data: categories.map(c => c.name), top: 10, textStyle: {fontSize: 12}}],
                series: [{
                    type: 'graph',
                    layout: 'force',
                    data: nodes,
                    links: links,
                    categories: categories,
                    roam: true,
                    draggable: true,
                    label: {show: true, position: 'right', fontSize: 11},
                    force: {repulsion: 300, edgeLength: [80, 150], gravity: 0.1},
                    emphasis: {focus: 'adjacency', lineStyle: {width: 3}}
                }]
            };
            
            graphChart.setOption(option, true);
        }'''

# 替换renderGraph函数，找到function renderGraph开头，到下一个function之前
pattern = r'function renderGraph\(\) \{.*?\n        \}'
html = re.sub(pattern, new_render, html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ 图谱渲染代码更新完成")
