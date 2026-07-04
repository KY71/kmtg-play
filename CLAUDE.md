# MTG 自由桌面

這個專案是一個瀏覽器裡的 MTG 數位桌面：提供牌桌和道具，
規則計算（法力、傷害、勝負）全部由玩家自己進行，程式不干涉、不裁判。
沒有 LLM 對局、沒有規則引擎。

## 快速開始

直接用瀏覽器開 `tabletop.html` 即可（雙擊檔案就能玩，不需要伺服器）。
也可以 `python3 server.py` 後開 http://localhost:8000/tabletop.html。

## 檔案結構

| 檔案 | 用途 |
|------|------|
| `tabletop.html` | 自由桌面（選牌組 → 洗牌抽 7 → 自由拖曳操作） |
| `deck_viewer.html` | 牌組瀏覽器（分組顯示卡圖） |
| `decks.json` | 牌表（機器讀：牌組代號 → 卡名×數量） |
| `decks/*.md` | 牌組文件（人讀：完整規則說明與策略） |
| `cards.json` | 卡牌資料庫（費用、類型、P/T、規則文字） |
| `cards.js`、`decks.js` | 上兩者的 `<script src>` 包裝（自動產生勿手改；讓 file:// 直接開檔也能載入資料） |
| `decks/cards/` | 本地卡圖（`<英文卡名 slug>.jpg`，缺圖時前端 fallback 到 Scryfall） |
| `fetch_cards.py` | 製卡機制（輸入卡名 → Scryfall 抓卡圖＋規則） |
| `server.py` | 本機靜態伺服器 |
| `工作紀錄.md` | 設計決策與進度紀錄 |

## Claude 的角色

Claude 不參與遊戲，只負責**牌組準備**與**專案維護**：

### 新增牌組的標準流程
1. 和使用者討論牌組內容，寫出 `decks/<名稱>.md`（格式參考現有檔案：
   總覽表格 + 詳細卡牌資訊 + 關鍵組合技）
2. 把牌表加進 `decks.json`（`{"代號": {"name", "era", "size", "cards": [[卡名, 數量], ...]}}`）
3. 執行 `python3 fetch_cards.py --all` 補齊新卡的卡圖與 `cards.json` 資料——
   **已經抓過的卡（圖檔已存在）會自動跳過，不會重抓**，只會處理新出現的卡名，
   所以隨時可以放心對整個 `decks.json` 跑 `--all`，不會浪費時間重複下載
4. 完成（`deck_viewer.html` 會自動讀到新牌組，不用手動改下拉選單或列表）

### 製卡機制
```bash
python3 fetch_cards.py "Lightning Bolt" "Dark Ritual"   # 抓指定卡
python3 fetch_cards.py --all                            # 補齊 decks.json 全部用卡（已存在的圖片會跳過）
python3 fetch_cards.py --force "Dark Ritual"            # 重抓覆蓋（忽略已存在的圖片/資料）
```
- 卡圖檔名規則：英文卡名 → 小寫 → 非英數換 `-` → `decks/cards/<slug>.jpg`
  （`tabletop.html`、`deck_viewer.html` 和腳本用同一規則，改動要同步）
- Scryfall 請求必須同時帶 `User-Agent` 和 `Accept` header，否則回 400
- 腳本每次執行都會從 JSON 重新產生 `cards.js`／`decks.js`；
  **手動改過 `decks.json` 或 `cards.json` 後，記得跑一次**（`--all` 或
  `python3 -c "import fetch_cards; fetch_cards.write_js()"`），否則桌面／牌組瀏覽器讀到的是舊資料

## 桌面操作（tabletop.html）

- 點牌庫抽牌；牌庫按鈕：洗牌／檢視（搜尋）／頂X（占卜）／磨1
- 拖曳卡片到任何區域；拖到牌庫時上半＝置頂、下半＝置底
- 戰場的卡：點擊橫置、雙擊翻面；Aura 直接疊放（不做程式附著）
- 指示物（+1/+1、−1/−1、通用）從托盤拖到卡上，點徽章移除
- Token：「產Token」按鈕（預設＋自訂）；token 離開戰場即消失
- 生命：±1／±5 按鈕，點數字直接輸入
- 遊戲狀態自動存 localStorage，可續局

## 設計原則（改功能前先讀）

- **玩家自由優先**：不加自動化規則判定（不驗法力、不算傷害、無 undo），
  避免玩家在「自由操作」和「系統功能」之間混淆
- 雙方手牌攤開（同畫面兩人對戰）；日後才考慮分畫面對戰
- 設計決策詳見 `工作紀錄.md`
