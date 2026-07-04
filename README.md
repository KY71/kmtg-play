# KMTG — MTG 自由桌面

瀏覽器裡的 Magic: The Gathering 數位桌面：牌桌＋道具，玩家自由操作。
規則計算（法力、傷害、勝負）由玩家自己進行，程式不干涉、不裁判。

## 概念

- **桌面只是道具**：牌庫、手牌、戰場、墳場、流放區、生命計數器、指示物、token、骰子
- **玩家自由優先**：不驗法力、不自動結算傷害、不強制階段、沒有 undo
- **卡圖本地化**：190 張卡圖已下載到 `decks/cards/`，離線可玩；缺圖自動 fallback 到 Scryfall

## 快速開始

**直接雙擊 `tabletop.html` 用瀏覽器開啟即可**（資料由 `cards.js`／`decks.js` 載入，不需要伺服器）。
也可以 `python3 server.py` 後開 http://localhost:8000/tabletop.html。

開新局：選兩副牌組 → 洗牌各抽 7 張 → 擲硬幣決定先手 → 開玩。

## 桌面操作

| 操作 | 方式 |
|------|------|
| 抽牌 | 點牌庫 |
| 洗牌／搜尋牌庫／占卜／磨牌 | 牌庫下方按鈕（洗牌／檢視／頂X／磨1） |
| 移動卡片 | 拖曳到任何區域（手牌、戰場、墳場、流放、牌庫頂/底） |
| 橫置／解橫 | 點戰場上的卡；「全部解橫」一鍵處理 |
| 翻面 | 雙擊卡片 |
| Aura 結附 | 直接把 Aura 疊放在生物卡上 |
| 指示物 | 從托盤拖 +1/+1、−1/−1、通用計數器到卡上；點徽章移除 |
| Token | 「產Token」按鈕（松鼠、骷髏等預設＋自訂）；拖離戰場即消失 |
| 生命 | ±1／±5 按鈕，點數字直接輸入 |
| 檢視墳場／流放區 | 點該牌堆攤開，可移回任何區域 |
| 先手／隨機 | 擲硬幣、D6、D20 |
| 續局 | 狀態自動存瀏覽器 localStorage，開新局前可「繼續上一局」 |

## 可用牌組

| 牌組代號 | 環境 | 描述 |
|------|------|------|
| `black` | 克薩時代 | 黑控快攻 v1.1（Carnophage、Skittering Skirge、Abyssal Specter） |
| `green` | 克薩時代 | 綠色 Stompy（Pouncing Jaguar、Deranged Hermit、Masticore） |
| `red` | 克薩時代 | 紅色 Sligh（Mogg Fanatic、Incinerate、Fault Line） |
| `grixis` | 大戰役 | Grixis 控制（Undermine、Fact or Fiction、Void） |
| `machine` | 大戰役 | Machine Head 黑紅（Blazing Specter、Urza's Rage） |
| `wu` | 大戰役 | 白藍解決方案（Meddling Mage、Absorb、Voice of All） |
| `rg-kavu` | 大戰役 | 紅綠卡烏快攻（Kavu Titan、Flametongue Kavu） |
| `slivers` | Extended 1999 | 反制裂片妖（Crystalline Sliver、Force of Will） |
| `slivers-legacy` | Legacy 2015 | 裂片妖 Legacy（Galerider Sliver、Aether Vial） |
| `slivers-modern` | Modern 2015 | 裂片妖 Modern（Collected Company、Manaweft Sliver） |
| `tron` | Modern | Eldrazi 鐵三角（Karn、Thought-Knot Seer） |
| `winter` | Modern 2016 | Eldrazi 寒冬（Eye of Ugin、Chalice of the Void） |
| `ramp` | 標準 2010 | Eldrazi 狂飆（Primeval Titan、Emrakul） |
| `rebel` | 馬凱迪亞 | 白色叛軍（Lin Sivvi、Parallax Wave） |

各牌組詳細卡表在 `decks/` 目錄下，可用 `deck_viewer.html` 瀏覽
（雙擊直接開，牌組下拉選單會自動從 `decks.json` 產生，不需要伺服器，新增牌組也不用手動改這個檔案）。

## 新增卡牌／牌組（標準流程）

```bash
python3 fetch_cards.py "Lightning Bolt"   # 抓單卡：卡圖存 decks/cards/、規則寫入 cards.json
python3 fetch_cards.py --all              # 補齊 decks.json 全部用卡
```

- **已經抓過的卡會自動跳過**（圖檔已存在就不重抓），所以 `--all` 隨時可以對整個
  `decks.json` 重跑一次，只會處理新出現的卡名，不會浪費時間
- 要強制重抓覆蓋，加 `--force`：`python3 fetch_cards.py --force "Dark Ritual"`
- 新牌組：寫 `decks/<名稱>.md` ＋ 加進 `decks.json` ＋ 跑 `--all` 補圖，完成
  （也可以直接請 Claude 做，流程寫在 `CLAUDE.md`）
- 手動改過 `decks.json`／`cards.json` 之後記得跑一次 `fetch_cards.py`（或
  `python3 -c "import fetch_cards; fetch_cards.write_js()"`），
  它會重新產生 `cards.js`／`decks.js`，桌面和牌組瀏覽器才會讀到最新資料

## 檔案結構

```
├── tabletop.html    # 自由桌面
├── deck_viewer.html # 牌組瀏覽器（動態讀 decks.js，不需伺服器）
├── decks.json       # 牌表（機器讀）
├── decks/           # 牌組文件（人讀 .md）與本地卡圖
│   └── cards/       #   190 張卡圖（<英文卡名 slug>.jpg）
├── cards.json       # 卡牌資料庫（費用、類型、P/T、規則文字）
├── cards.js、decks.js  # 上兩個 JSON 的 <script src> 包裝（自動產生，勿手改）
├── fetch_cards.py   # 製卡機制（Scryfall；已有的圖片會自動跳過）
├── server.py        # 本機靜態伺服器（非必要，方便偶爾用）
└── 工作紀錄.md      # 設計決策與進度
```
