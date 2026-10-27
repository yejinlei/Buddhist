#!/bin/bash
set -e

echo "====================================="
echo "  佛学本体论 - GitHub Pages一键发布"
echo "====================================="
echo ""

# 配置仓库信息
REPO_NAME="Buddhist"
DEFAULT_USER="yejinlei"

read -p "请输入你的GitHub用户名 [$DEFAULT_USER]: " GITHUB_USER
GITHUB_USER=${GITHUB_USER:-$DEFAULT_USER}

REPO_URL="git@github.com:${GITHUB_USER}/${REPO_NAME}.git"

echo ""
echo "将要发布到: $REPO_URL"
echo ""

# 检查Git
if ! command -v git &> /dev/null
then
    echo "错误: 未安装Git，请先安装Git"
    exit 1
fi

# 初始化Git仓库
if [ ! -d .git ]; then
    echo "初始化Git仓库..."
    git init
    git checkout -b main
fi

# 配置用户信息
read -p "请输入Git提交用户名: " GIT_NAME
read -p "请输入Git提交邮箱: " GIT_EMAIL
git config user.name "$GIT_NAME"
git config user.email "$GIT_EMAIL"

# 添加所有文件
echo "添加文件..."
git add .

# 提交
echo "提交..."
git commit -m "init: 佛学本体论 - 全量知识图谱平台"

# 添加远程仓库
if git remote get-url origin &> /dev/null; then
    echo "远程仓库已存在，更新origin..."
    git remote set-url origin "$REPO_URL"
else
    echo "添加远程仓库..."
    git remote add origin "$REPO_URL"
fi

echo ""
echo "准备推送到 $REPO_URL"
echo "如果仓库不存在，请先在GitHub创建空仓库: https://github.com/new"
echo ""
read -p "确认推送? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "推送中..."
    git push -u origin main --force
    echo ""
    echo "====================================="
    echo "✅ 推送完成!"
    echo "接下来请按以下步骤开启Pages:"
    echo "1. 打开 https://github.com/${GITHUB_USER}/${REPO_NAME}/settings/pages"
    echo "2. Source 选择 Deploy from a branch"
    echo "3. Branch 选择 main, /root, 点击Save"
    echo "4. 等待2分钟即可访问: https://${GITHUB_USER}.github.io/${REPO_NAME}/"
    echo "====================================="
else
    echo "已取消推送"
fi
