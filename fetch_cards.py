#!/usr/bin/env python3
"""製卡機制：輸入卡名 → 從 Scryfall 抓卡圖存入 cards/、規則文字寫入 cards.json。

用法：
  python3 fetch_cards.py "Lightning Bolt" "Dark Ritual"   # 抓指定卡
  python3 fetch_cards.py --all                            # 補齊 decks.json 全部用卡缺少的圖
  python3 fetch_cards.py --force "Dark Ritual"            # 重抓（覆蓋既有圖檔與資料）

卡圖檔名規則（tabletop.html／deck_viewer.html 用同一規則找圖）：
  英文卡名 → 小寫 → 非英數字元換成 '-' → decks/cards/<slug>.jpg
  例：\"Lin Sivvi, Defiant Hero\" → decks/cards/lin-sivvi-defiant-hero.jpg
"""
import json, os, re, sys, time, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(ROOT, "decks", "cards")
CARDS_JSON = os.path.join(ROOT, "cards.json")
DECKS_JSON = os.path.join(ROOT, "decks.json")
API = "https://api.scryfall.com/cards/named"
DELAY = 0.12  # Scryfall 禮貌間隔


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def http_get(url):
    # Scryfall 要求同時帶 User-Agent 與 Accept，缺一律回 400
    req = urllib.request.Request(url, headers={"User-Agent": "KMTG-tabletop/1.0", "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fetch_one(name, cards_db, force=False):
    img_path = os.path.join(CARDS_DIR, slug(name) + ".jpg")
    need_img = force or not os.path.exists(img_path)
    need_data = force or name not in cards_db
    if not need_img and not need_data:
        return "skip"

    data = json.loads(http_get(f"{API}?exact={urllib.parse.quote(name)}"))
    time.sleep(DELAY)

    if need_img:
        # 雙面/連體牌的圖在 card_faces 裡
        uris = data.get("image_uris") or data.get("card_faces", [{}])[0].get("image_uris")
        if not uris:
            return "no-image"
        with open(img_path, "wb") as f:
            f.write(http_get(uris["normal"]))
        time.sleep(DELAY)

    if need_data:
        entry = {"cost": data.get("mana_cost", ""), "type": data.get("type_line", "")}
        if data.get("power") is not None:
            try:
                entry["power"] = int(data["power"])
                entry["toughness"] = int(data["toughness"])
            except ValueError:  # 例如 power = "*"
                entry["power"] = data["power"]
                entry["toughness"] = data["toughness"]
        text = data.get("oracle_text")
        if text is None and data.get("card_faces"):
            text = "\n//\n".join(f.get("oracle_text", "") for f in data["card_faces"])
        entry["text"] = text or ""
        cards_db[data["name"]] = entry

    return "ok"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    fetch_all = "--all" in sys.argv

    if not args and not fetch_all:
        print(__doc__)
        return

    os.makedirs(CARDS_DIR, exist_ok=True)
    cards_db = json.load(open(CARDS_JSON)) if os.path.exists(CARDS_JSON) else {}

    names = list(args)
    if fetch_all:
        decks = json.load(open(DECKS_JSON))
        names += sorted({n for d in decks.values() for n, _ in d["cards"]})

    ok = skip = fail = 0
    for i, name in enumerate(names, 1):
        try:
            r = fetch_one(name, cards_db, force=force)
        except Exception as e:
            print(f"[{i}/{len(names)}] ✗ {name}: {e}")
            fail += 1
            continue
        if r == "skip":
            skip += 1
        else:
            ok += 1
            print(f"[{i}/{len(names)}] ✓ {name}")

    with open(CARDS_JSON, "w") as f:
        json.dump(cards_db, f, ensure_ascii=False, indent=2)
    write_js()
    print(f"完成：{ok} 抓取、{skip} 已存在、{fail} 失敗（卡圖在 cards/，規則在 cards.json）")


def write_js():
    """把 cards.json / decks.json 包成 .js（tabletop.html 用 <script src> 載入，
    file:// 直接開檔也能玩，不受 fetch 的 CORS 限制）。JSON 仍是唯一資料來源。"""
    for src, dst, var in [(CARDS_JSON, "cards.js", "CARDS_DATA"),
                          (DECKS_JSON, "decks.js", "DECKS_DATA")]:
        if os.path.exists(src):
            data = open(src, encoding="utf-8").read()
            with open(os.path.join(ROOT, dst), "w") as f:
                f.write(f"window.{var} = {data};\n")


if __name__ == "__main__":
    main()
