# Naming and Planning Reference

## Best Source Naming

Prefer file names that match the cooking steps:

```text
01_成品展示.MOV
02_准备食材.MOV
03_虾仁加生抽.MOV
04_虾仁加白胡椒.MOV
05_虾仁加料酒.MOV
06_虾仁调味完成静置.MOV
07_芦笋切尾部.MOV
08_芦笋削硬皮.MOV
09_芦笋斜切段.MOV
10_杏鲍菇切块.MOV
11_蒜切块.MOV
12_芦笋焯水.MOV
13_芦笋捞出.MOV
14_虾仁下锅.MOV
15_虾仁煎至金黄.MOV
16_炒蒜和花椒.MOV
17_炒杏鲍菇.MOV
18_倒入芦笋.MOV
19_倒入虾仁.MOV
20_调味翻炒.MOV
21_出锅装盘.MOV
```

Use completion-state names when there is no action shot:

```text
06_虾仁调味完成静置.MOV
```

This avoids pairing a subtitle like "搅拌均匀" with unrelated action footage.

## `clip_plan.tsv` Format

Columns:

```text
idx	src	start	duration	zh	en	jp	pos
```

Example:

```text
001	01_成品展示.MOV	0.30	2.20	芦笋杏鲍菇炒虾仁	Asparagus, King Oyster Mushroom and Shrimp Stir-fry	アスパラとエリンギとエビの炒め物	title
002	02_准备食材.MOV	0.60	1.80	准备芦笋、虾仁、杏鲍菇、蒜和花椒粒	Prepare asparagus, shrimp, king oyster mushroom, garlic and Sichuan pepper	アスパラ、エビ、エリンギ、にんにく、花椒を用意	normal
003	03_虾仁加生抽.MOV	0.20	1.50	虾仁加入1汤匙生抽	Add 1 tbsp light soy sauce to the shrimp	エビに醤油大さじ1を加える	normal
```

## Review Heuristics

- Check all seasoning steps; they are easy to mismatch.
- Check "mix well" rows; if no mixing is visible, show the completed seasoned bowl and adjust wording.
- Check final title/cover frame; the dish should be recognizable and not motion-blurred.
- Keep intermediate project files under `菜名/project/`.
