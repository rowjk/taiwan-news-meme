# 台灣新聞熱門關鍵字 ++ 廢文製造所

### Taiwan News 3D Word Cloud & Meme Generator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://taiwan-news-meme-makr.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

這是一個結合 **即時新聞爬蟲**、**自然語言處理 (NLP)** 與 **3D 資料視覺化** 的趣味專案。程式會即時抓取 Google News 台灣焦點新聞，分析出當下最熱門的關鍵字，並將其製作成 3D 自動旋轉的文字雲，最後隨機填入 100 組幽默的「廢文模板」中，博君一笑。

## 🚀 線上展示 (Live Demo)
 **[https://taiwan-news-meme-makr.streamlit.app/](https://taiwan-news-meme-makr.streamlit.app/)**

---

## ✨ 主要功能 (Features)

* **📰 即時新聞爬蟲**：使用 `feedparser` 抓取 Google News RSS (台灣版)，確保關鍵字永遠是最新的。
* **🔍 關鍵字分析**：利用 `jieba` 進行中文斷詞與 TF-IDF 權重分析，精準提煉熱門詞彙。
* **☁️ 3D 互動文字雲**：使用 `Plotly` 繪製 3D 散點圖，並透過 JavaScript 注入技術實現 **全自動 360 度無限旋轉**。
* **🤖 AI 廢文製造機**：內建 100 組爆笑文案模板，將嚴肅的新聞關鍵字填入荒謬的情境中。
    * *分類包含：動漫動漫動動漫、高流量網紅往紅、時空旅人史萊姆、零異現象好怕怕、我沒錢我驕傲...等。*
* **⚙️ 高度客製化**：提供側邊欄控制面板，使用者可即時新增「排除名單」，過濾不想看到的關鍵字。

---
## 🛠️ 使用技術 (Tech Stack)

* **[Python](https://www.python.org/)**: 核心程式語言
* **[Streamlit](https://streamlit.io/)**: 快速網頁應用程式框架
* **[Plotly](https://plotly.com/python/)**: 3D 互動圖表繪製
* **[Jieba](https://github.com/fxsjy/jieba)**: 中文斷詞與關鍵字提取
* **[Feedparser](https://pypi.org/project/feedparser/)**: RSS 訂閱源解析

