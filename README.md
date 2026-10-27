# 佛学本体论 Buddhist Ontology
> 全量义理知识图谱与智能推演平台

参考[红楼未完](https://yejinlei.github.io/hongloumeng/)、[水浒传人物图谱](https://yejinlei.github.io/shuihu/)、[诺奖图谱](https://yejinlei.github.io/nobel/)范式构建的佛学知识本体站。

## 项目特性
- 📚 **完备七层本体架构**：教理本体→义理范畴→宗派判教→文本载体→人物传承→文化外延，兼容RDF/OWL规范
- 🗂️ **多译本对比**：核心大乘经典收录108个译本，支持《心经》7译本、《金刚经》6译本等同经异译对照
- 🕸️ **义理关系图谱**：60+种语义关系（摄属/对破/相即/次第/化现等），ECharts力导向图可视化
- 🧘 **八大宗派体系**：含各宗判教理论、法脉传承、核心教义对比
- ⚙️ **概念路径推演**：纯前端本体推理引擎，自动推导概念间义理关联路径
- 🧑‍🤝‍🧑 **完整圣众体系**：诸佛、菩萨、罗汉、祖师、译经师、现代学者，含济公、布袋和尚等文化外延人物
- ⏳ **译传时间轴**：六百年佛经汉译史可视化

## 快速部署到GitHub Pages
1. Fork本仓库或直接在GitHub创建名为 `Buddhist` 的空仓库
2. 运行本目录下 `deploy.sh` 脚本，按提示输入你的GitHub用户名
3. 进入仓库 Settings → Pages → Source 选择 `main` 分支，保存
4. 等待1-2分钟即可访问 `https://yejinlei.github.io/Buddhist/`

## 本地预览
```bash
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000
```

## 目录结构
```
├── data/          # 本体数据（YAML/JSON）
├── pages/         # 子页面（宗派、人物、经典）
├── sutras/        # 经论页面
├── sects/         # 宗派页面
├── js/            # 本体推理引擎与交互脚本
└── index.html     # 首页
```

## 路线图
- [ ] 全量大正藏3493部经批量导入脚本
- [ ] 科判树形导航交互
- [ ] 跨译本文本差异比对
- [ ] 学者原文锚点跳转
