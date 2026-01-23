import streamlit as st
import feedparser
import jieba
import jieba.analyse
import plotly.graph_objects as go
import random
import math
import streamlit.components.v1 as components

# --- 1. 設定頁面與側邊欄 ---
st.set_page_config(page_title="台灣新聞熱門關鍵字 ++ 廢文製造所", layout="wide")

# 【修正點】移除 "TW" 表情符號，只保留純文字
st.title("台灣新聞熱門關鍵字 ++ 廢文製造所")

# 側邊欄設定
st.sidebar.header("⚙️ 關鍵字設定")
st.sidebar.write("在這裡輸入你想排除的字詞，用「逗號」分隔：")

default_stopwords = (
    "的,了,在,是,我,有,和,就,不,人,都,一個,上,也,很,到,說,要,去,會,著,沒有,看,好,自己,這,那,與,及,等,之,所,"
    "台灣,報導,新聞,影,曝光,網友,回應,表示,畫面,文章,來源,內容,全文,連結,網址,更多,部分,針對,指出,"
    "Yahoo,ETtoday,TVBS,聯合報,中時,自由時報,三立,壹蘋,鏡週刊,NOWnews,公視,華視,東森,民視,台視,中天,"
    "中央社,風傳媒,新頭殼,今日新聞,聯合新聞網,中時電子報,UDN,LTN,SETN,CNA,"
    "奇摩,新聞網,NEWS,news,GeneOnline,com,ludens,"
    "自由,聯合,時報,特報,富房網,娛樂,社會,頭條,Storm,東森新聞,公開,娛樂星聞,mg,tw,"
    "體育,縣市,最大,最小,震撼,VR"
)

user_stopwords_input = st.sidebar.text_area("排除詞彙名單", value=default_stopwords, height=300)
user_stopwords = set(word.strip() for word in user_stopwords_input.split(','))

# --- 定義句子模板庫 ---
SENTENCE_TEMPLATES = [
    # 宅宅的幻想曲
    ("宅宅的幻想曲", "老闆說公司轉型全靠 {{關鍵字}} 了，我該準備離職嗎？"),
    ("宅宅的幻想曲", "開會時我忍不住對著投影幕上的 {{關鍵字}} 發呆了三小時。"),
    ("宅宅的幻想曲", "其實我的職涯規劃，基本上就是由咖啡和 {{關鍵字}} 組成的。"),
    ("宅宅的幻想曲", "有人能解釋為什麼我的年終獎金被換成了一箱 {{關鍵字}} 嗎？"),
    ("宅宅的幻想曲", "面試官問我最大的缺點是什麼，我說是對 {{關鍵字}} 過度執著。"),
    ("宅宅的幻想曲", "這份報告寫得很好，但客戶覺得缺了一點 {{關鍵字}} 的靈魂。"),
    ("宅宅的幻想曲", "我在履歷表的「特殊技能」欄位填了：擅長徒手對付 {{關鍵字}}。"),
    ("宅宅的幻想曲", "加班到凌晨三點，我看著螢幕上的 {{關鍵字}} 笑了出來，我是不是瘋了？"),
    ("宅宅的幻想曲", "為了節省預算，公司決定以後午餐都吃 {{關鍵字}}。"),
    ("宅宅的幻想曲", "不要問我為什麼在影印機上面放 {{關鍵字}}，那是風水。"),
    
    # 荒謬的我愛你
    ("荒謬的我愛你", "算命師說，我的真命天子會帶著 {{關鍵字}} 出現在轉角。"),
    ("荒謬的我愛你", "我們分手吧，因為我無法接受你睡覺時抱著 {{關鍵字}}。"),
    ("荒謬的我愛你", "情人節送花太俗氣了，今年我送了女友一噸 {{關鍵字}}。"),
    ("荒謬的我愛你", "我愛你，勝過愛 {{關鍵字}}，但少於珍珠奶茶。"),
    ("荒謬的我愛你", "第一次約會就聊 {{關鍵字}} 的人，通常都是狠角色。"),
    ("荒謬的我愛你", "雖然他長得很帥，但他吃火鍋竟然加 {{關鍵字}}，直接出局。"),
    ("荒謬的我愛你", "我媽問我為什麼還不結婚，我說我在等 {{關鍵字}} 降價。"),
    ("荒謬的我愛你", "前任傳訊息來說他很想念我的 {{關鍵字}}。"),
    ("荒謬的我愛你", "原來「在此刻相愛」的意思，就是一起看著 {{關鍵字}} 發呆。"),
    ("荒謬的我愛你", "曖昧就像 {{關鍵字}}，你看得到，但永遠吃不到。"),
    
    # 我好愛看新聞
    ("我好愛看新聞", "震驚！99% 的台灣人都不知道 {{關鍵字}} 居然能治禿頭。"),
    ("我好愛看新聞", "專家指出：長期接觸 {{關鍵字}} 可能導致智商下降。"),
    ("我好愛看新聞", "只要三分鐘，教你如何用 {{關鍵字}} 財富自由。"),
    ("我好愛看新聞", "矽谷最新趨勢：身價百億的 CEO 都在喝 {{關鍵字}}。"),
    ("我好愛看新聞", "別再吃酪梨了！現在流行生吃 {{關鍵字}}。"),
    ("我好愛看新聞", "{{關鍵字}} 概念股大漲，分析師表示：看不懂但大受震撼。"),
    ("我好愛看新聞", "獨家揭密：外星人遲遲不攻擊地球，是因為害怕我們的 {{關鍵字}}。"),
    ("我好愛看新聞", "這是 {{關鍵字}} 還是現代藝術？網拍喊價三百萬。"),
    ("我好愛看新聞", "他在捷運上做這件事，全車廂的人都為了 {{關鍵字}} 鼓掌。"),
    ("我好愛看新聞", "這種 {{關鍵字}} 如果不紅，天理難容！"),
    
    # 哲學心靈 G 湯
    ("哲學心靈 G 湯", "人生就像 {{關鍵字}}，雖然沒什麼用，但看起來很厲害。"),
    ("哲學心靈 G 湯", "當你凝視 {{關鍵字}} 的時候，{{關鍵字}} 也在凝視你。"),
    ("哲學心靈 G 湯", "跌倒了別怕，站起來，拍拍身上的 {{關鍵字}} 繼續走。"),
    ("哲學心靈 G 湯", "成功的秘訣很簡單：堅持、努力、還有大量的 {{關鍵字}}。"),
    ("哲學心靈 G 湯", "原來寂寞的形狀，長得像 {{關鍵字}}。"),
    ("哲學心靈 G 湯", "不要讓別人的 {{關鍵字}} 決定你的價值。"),
    ("哲學心靈 G 湯", "我不想努力了，阿姨，請問妳有 {{關鍵字}} 嗎？"),
    ("哲學心靈 G 湯", "每天叫醒我的不是夢想，是 {{關鍵字}} 砸在臉上的痛楚。"),
    ("哲學心靈 G 湯", "只要心中有 {{關鍵字}}，哪裡都是馬爾地夫。"),
    ("哲學心靈 G 湯", "放下屠刀，立地成為 {{關鍵字}}。"),
    
    # 原硬派科技 -> 宅宅的幻想曲 (合併)
    ("宅宅的幻想曲", "我的 AI 壞了，它現在只會生成 {{關鍵字}} 的圖片。"),
    ("宅宅的幻想曲", "請問把 {{關鍵字}} 插進 USB 孔會觸電嗎？在線等，急。"),
    ("宅宅的幻想曲", "最新 iPhone 傳聞將取消充電孔，改用 {{關鍵字}} 傳輸能量。"),
    ("宅宅的幻想曲", "這段程式碼寫得太爛了，簡直像 {{關鍵字}} 在鍵盤上跳舞。"),
    ("宅宅的幻想曲", "Google 搜尋第一名竟然是：「如何跟 {{關鍵字}} 結婚」。"),
    ("宅宅的幻想曲", "我買了降噪耳機，但還是擋不住 {{關鍵字}} 的聲音。"),
    ("宅宅的幻想曲", "工程師的浪漫：用 Python 畫一個 {{關鍵字}} 給妳。"),
    ("宅宅的幻想曲", "當元宇宙來臨，我第一件事就是要虛擬化我的 {{關鍵字}}。"),
    ("宅宅的幻想曲", "這台伺服器過熱了，快拿 {{關鍵字}} 來降溫！"),
    ("宅宅的幻想曲", "無法連線到網際網路，請檢查您的 {{關鍵字}} 設定。")
]

# --- 2. 抓取新聞資料 ---
@st.cache_data(ttl=300)
def get_news_keywords():
    rss_url = "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-TW"
    feed = feedparser.parse(rss_url)
    text_content = ""
    for entry in feed.entries:
        text_content += entry.title + " "
    return text_content

# --- 3. 處理文字 ---
def process_text(text, stop_words_set):
    tags = jieba.analyse.extract_tags(text, topK=150, withWeight=True)
    clean_tags = []
    
    for word, weight in tags:
        if (word not in stop_words_set) and \
           (len(word) > 1) and \
           (not word.isdigit()) and \
           (word.lower() not in stop_words_set): 
            clean_tags.append((word, weight))
            
    return clean_tags[:50]

# --- 4. 產生 Plotly 圖表物件 ---
def create_figure(keywords):
    if not keywords:
        return None
        
    words = [x[0] for x in keywords]
    weights = [x[1] for x in keywords]
    
    x = [random.uniform(-3, 3) for _ in range(len(words))]
    y = [random.uniform(-3, 3) for _ in range(len(words))]
    z = [random.uniform(-3, 3) for _ in range(len(words))]
    
    color_palette = ['#FF5733', '#33FF57', '#3357FF', '#F1C40F', '#8E44AD', 
                     '#E74C3C', '#3498DB', '#1ABC9C', '#FF00FF', '#008080']
    assign_colors = [random.choice(color_palette) for _ in words]
    font_sizes = [12 + w * 500 for w in weights]

    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='text',
        text=words,
        textposition="middle center",
        textfont=dict(size=font_sizes, color=assign_colors),
        hoverinfo='text'
    )])

    # 動畫設定
    frames = []
    steps = 120 
    for t in range(steps):
        theta = t * (2 * math.pi / steps)
        eye_x = 1.8 * math.cos(theta)
        eye_y = 1.8 * math.sin(theta)
        eye_z = 0.6 * math.sin(3 * theta)
        frames.append(go.Frame(
            layout=dict(scene=dict(camera=dict(eye=dict(x=eye_x, y=eye_y, z=eye_z)))),
            name=f'frame{t}'
        ))
    fig.frames = frames

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False), 
            yaxis=dict(visible=False), 
            zaxis=dict(visible=False),
            bgcolor='rgba(0,0,0,0)',
            camera=dict(eye=dict(x=1.8, y=0, z=0))
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=500,
        updatemenus=[]
    )
    return fig

# --- 5. 渲染自動播放 HTML ---
def render_auto_play_html(fig):
    plot_html = fig.to_html(include_plotlyjs='cdn', config={'displayModeBar': False}, full_html=True)
    custom_js = """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        setTimeout(function() {
            var plot_div = document.querySelector('.plotly-graph-div');
            function startAnimation() {
                Plotly.animate(plot_div, null, {
                    frame: {duration: 50, redraw: true},
                    fromcurrent: true,
                    transition: {duration: 0},
                    mode: 'immediate'
                }).then(function() {
                    Plotly.animate(plot_div, [null], {mode: 'immediate'});
                    startAnimation();
                });
            }
            if(plot_div) { startAnimation(); }
        }, 1000);
    });
    </script>
    """
    final_html = plot_html.replace('</body>', custom_js + '</body>')
    components.html(final_html, height=500)

# --- 6. 產生好笑句子 ---
def display_funny_sentences(keywords):
    if not keywords: return
    
    st.markdown("---")
    st.subheader("🤖 AI 廢文製造所")
    st.caption("以下內容由新聞關鍵字隨機生成，不代表本人立場 (但代表 AI 的幽默感)")
    
    colors = ['#FF5733', '#33FF57', '#3357FF', '#F1C40F', '#8E44AD', '#E74C3C', '#3498DB', '#1ABC9C', '#FF00FF']
    selected_templates = random.sample(SENTENCE_TEMPLATES, 6)
    
    col1, col2 = st.columns(2)
    
    for i, (category, template) in enumerate(selected_templates):
        word = random.choice(keywords)[0]
        color = random.choice(colors)
        styled_word = f"<span style='color:{color}; font-weight:bold; font-size:1.2em;'>{word}</span>"
        final_sentence = template.replace("{{關鍵字}}", styled_word)
        
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.markdown(f"**【{category}】**")
            st.markdown(f"> {final_sentence}", unsafe_allow_html=True)
            st.write("") 

# --- 7. 主程式執行 ---
try:
    with st.spinner('正在分析全台新聞、計算 3D 軌跡、並生成廢文中...'):
        raw_text = get_news_keywords()
        keywords = process_text(raw_text, user_stopwords)
        
        if keywords:
            fig = create_figure(keywords)
            render_auto_play_html(fig)
            display_funny_sentences(keywords)
        else:
            st.warning("所有關鍵字都被排除光了！")
            
        st.markdown("---")
        if st.button('🔄 重新抓取新聞 & 產生新廢文'):
            st.cache_data.clear()
            st.rerun()
            
except Exception as e:
    st.error(f"發生錯誤: {e}")