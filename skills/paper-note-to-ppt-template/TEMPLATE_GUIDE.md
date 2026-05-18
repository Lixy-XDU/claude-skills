# TEMPLATE_GUIDE.md

将用户下载的 PNG 模板放入：

```text
templates/
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

## 使用方式

- renderer 会把每张 PNG 作为整页背景图铺满 16:9 页面。
- 文本、公式、图片会被叠加到 `layouts/template_layouts_16x9.json` 中定义的 slot。
- 模板图片中已有卡片框、曲线、图案，renderer 默认不额外画卡片背景。

## 推荐图片规格

- 16:9 横版
- 推荐 1920×1080 或更高
- PNG 格式
- 不要带文字
- 不要带校徽或机构名，除非希望固定显示

## 文件名兼容

优先匹配中文文件名；如果找不到，也会尝试匹配英文别名：

```text
title.png
agenda.png
section.png
one_column.png
two_column.png
three_column.png
image_text.png
closing.png
```
