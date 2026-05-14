# skill-graph

安装到：

```bash
~/.claude/skills/skill-graph/
```

推荐安装命令：

```bash
mkdir -p ~/.claude/skills/skill-graph
cp -R SKILL.md skill.meta.yaml scripts templates ~/.claude/skills/skill-graph/
```

生成中文版 HTML 图：

```bash
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py
```

输出：

```bash
~/.claude/skills/SKILL_GRAPH.html
```

项目级 skills：

```bash
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --root .claude/skills
```

只补齐 metadata：

```bash
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --init-meta-only
```
