# paper-note-to-ppt-template

这是一个 Claude Code Skill，用用户提供的一套 PNG 背景模板实现论文 / 笔记转科研 PPT。

## 安装

```bash
mkdir -p ~/.claude/skills
cp -R paper-note-to-ppt-template ~/.claude/skills/paper-note-to-ppt-template
```

## 放入模板

将以下图片放入：

```text
~/.claude/skills/paper-note-to-ppt-template/templates/
```

需要的文件名：

```text
标题模板.png
目录模板.png
子标题模板.png
单列模板.png
两列模板.png
三列模板.png
图文模板.png
结尾模板.png
```

## 依赖

```bash
pip install python-pptx pillow matplotlib pypdf
```

## 调用

```bash
/paper-note-to-ppt-template ./paper.pdf "中文组会，12页，偏方法和实验"
```

## 设计原则

- 模板 PNG 作为整页背景。
- 文字、图片、公式只放入固定 slot。
- 不额外绘制卡片背景，避免与模板卡片冲突。
- 公式图片化后插入。
- 图片 contain 等比缩放。
