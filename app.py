import streamlit as st
import random
import datetime
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- YAPAY ZEKA KÜTÜPHANELERİ ---
try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# --- API ANAHTARLARI (ELİNDE OLANLARI GİR, OLMAYANLARI BOŞ BIRAK) ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")


# Tarayıcı sekmesinde görünecek başlık
st.set_page_config(page_title="Sude'nin Çalışma Alanı", page_icon="🌻", layout="wide")

# --- SİSTEM DEĞİŞKENLERİ ---
if 'tema' not in st.session_state: st.session_state['tema'] = 'Gündüz Bahçesi 🌻'
if 'arayuz' not in st.session_state: st.session_state['arayuz'] = 'sekmeler'
if 'aktif_uygulama' not in st.session_state: st.session_state['aktif_uygulama'] = None
if 'toplam_calisilan_dakika' not in st.session_state: st.session_state['toplam_calisilan_dakika'] = 0

# --- ÜST TEMA SEÇİM PANELİ (TEK TIKLA GEÇİŞ İÇİN RADIO) ---
st.markdown("---")
st.markdown("<h4 style='text-align: center; margin-bottom: 5px;'>🎨 Tema Dünyası Seç</h4>", unsafe_allow_html=True)
st.radio(
    "Tema Seç", 
    ["Gündüz Bahçesi 🌻", "Gece Moru 🌙", "Doğa Yeşili 🌿", "Coffee Latte ☕", "Kozmik Galaksi 🌌", "Sakura Pembe 🌸"], 
    key="tema", 
    horizontal=True,
    label_visibility="collapsed"
)

tema_secimi = st.session_state['tema']

if tema_secimi == "Gece Moru 🌙":
    bg = "#1E1E24"; card = "#2B2B36"; hdr = "#C084FC"; txt = "#E2E8F0"
    btn = "#3B2859"; btn_hover = "#503080"; btn_txt = "#E9D5FF"; border = "#7E22CE"
    guller_filter = "grayscale(100%) brightness(40%) sepia(100%) hue-rotate(250deg) saturate(300%)" 
elif tema_secimi == "Doğa Yeşili 🌿":
    bg = "#F4F9F4"; card = "#FFFFFF"; hdr = "#2D6A4F"; txt = "#2b3e34"
    btn = "#B7E4C7"; btn_hover = "#95D5B2"; btn_txt = "#1B4332"; border = "#52B788"
    guller_filter = "grayscale(100%) brightness(40%) sepia(100%) hue-rotate(80deg) saturate(200%)"
elif tema_secimi == "Coffee Latte ☕":
    bg = "#FDF6EC"; card = "#FFFFFF"; hdr = "#7F5539"; txt = "#4A3525"
    btn = "#DDBEA9"; btn_hover = "#CB997E"; btn_txt = "#582F0E"; border = "#B08968"
    guller_filter = "grayscale(100%) brightness(50%) sepia(80%) hue-rotate(30deg) saturate(200%)"
elif tema_secimi == "Kozmik Galaksi 🌌":
    bg = "#0F172A"; card = "#1E293B"; hdr = "#38BDF8"; txt = "#F1F5F9"
    btn = "#1E3A8A"; btn_hover = "#2563EB"; btn_txt = "#BFDBFE"; border = "#38BDF8"
    guller_filter = "grayscale(100%) brightness(50%) sepia(100%) hue-rotate(180deg) saturate(400%)"
elif tema_secimi == "Sakura Pembe 🌸":
    bg = "#FFF0F3"; card = "#FFFFFF"; hdr = "#FF4D6D"; txt = "#590D22"
    btn = "#FFB3C1"; btn_hover = "#FF758F"; btn_txt = "#590D22"; border = "#FF4D6D"
    guller_filter = "grayscale(100%) brightness(60%) sepia(100%) hue-rotate(300deg) saturate(300%)"
else: # Gündüz Bahçesi 🌻
    bg = "#FFF5F5"; card = "#FFFFFF"; hdr = "#D6336C"; txt = "#495057"
    btn = "#FFB3C6"; btn_hover = "#FF8FAB"; btn_txt = "#590D22"; border = "#D6336C"
    guller_filter = "grayscale(100%) brightness(0%) opacity(25%)"

# --- DİNAMİK CSS YÜKLEMESİ ---
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg} !important; transition: background-color 0.3s; }}
    h1, h2, h3, h4, h5, h6 {{ color: {hdr} !important; font-family: 'Trebuchet MS', sans-serif; }}
    p, span, label, [data-testid="stMetricValue"], [data-testid="stMetricLabel"], .stMarkdown, .stText {{ color: {txt} !important; }}
    div.stButton > button:first-child {{
        background-color: {btn} !important; color: {btn_txt} !important;
        border-radius: 12px !important; border: 2px solid {border} !important;
        padding: 10px 20px !important; font-weight: bold !important; font-size: 16px !important;
        transition: all 0.3s ease !important; width: 100% !important; 
    }}
    div.stButton > button:first-child:hover {{ background-color: {btn_hover} !important; color: {txt} !important; border-color: {hdr} !important; transform: translateY(-2px); }}
    .stTextInput input, .stTextArea textarea, .stNumberInput input {{ background-color: {card} !important; color: {txt} !important; border: 1px solid {border} !important; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

if st.session_state['arayuz'] == 'mobil' and st.session_state['aktif_uygulama'] is None:
    st.markdown("""<style>div.stButton > button:first-child {aspect-ratio: 1 / 1 !important; height: auto !important; border-radius: 25px !important; font-size: 18px !important; white-space: pre-wrap !important; box-shadow: 4px 6px 15px rgba(0,0,0,0.15) !important; display: flex !important; flex-direction: column !important; justify-content: center !important; align-items: center !important; line-height: 1.4 !important;} div.stButton > button:first-child:hover {transform: translateY(-5px) scale(1.03) !important;}</style>""", unsafe_allow_html=True)

# --- SİNYAL KONTROL SİSTEMİ ---
signal_dosya = "ardadan_mesaj.json"
if os.path.exists(signal_dosya):
    try:
        with open(signal_dosya, "r", encoding="utf-8") as f:
            signal_data = json.load(f)
            if signal_data.get("aktif", False):
                st.markdown(f"""
                <div style="background-color: {card}; border: 3px solid {hdr}; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 20px rgba(0,0,0,0.2);">
                    <h2 style="color: {hdr}; margin: 0 0 10px 0;">🚨 Arda'dan Sinyal Var!</h2>
                    <p style="font-size: 18px; font-weight: bold; color: {txt};">"{signal_data.get('mesaj', 'Sana ulaşmaya çalışıyor!')}"</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Mesajı Gördüm / Kapat 🔕"):
                    signal_data["aktif"] = False
                    with open(signal_dosya, "w", encoding="utf-8") as f:
                        json.dump(signal_data, f)
                    st.rerun()
    except Exception:
        pass

# Üst Menü Görünüm Toggle'ı
hizli_menu = st.toggle("📱 Hızlı Menü (Tablet/Telefon Görünümü)", value=(st.session_state['arayuz'] == 'mobil'))
if hizli_menu and st.session_state['arayuz'] == 'sekmeler': st.session_state['arayuz'] = 'mobil'; st.session_state['aktif_uygulama'] = None; st.rerun()
elif not hizli_menu and st.session_state['arayuz'] == 'mobil': st.session_state['arayuz'] = 'sekmeler'; st.rerun()

st.markdown(f"<h1 style='text-align: center; color: {hdr}; margin-top: 10px;'>Sude'nin Motivasyon İstasyonu 🚀</h1>", unsafe_allow_html=True)

sozler = [
    "Başarı, her gün tekrarlanan küçük çabaların toplamıdır.",
    "Bugün yapacağın fedakarlıklar, yarınki özgürlüğünün bedelidir.",
    "Senin yarışın sadece kendinle. Dünden bir adım daha ileri git.",
    "Hayallerin, onlara inandığın kadar gerçektir."
]
random.seed(datetime.date.today().toordinal()); gunun_sozu = random.choice(sozler); random.seed()

if st.session_state['arayuz'] == 'sekmeler' or st.session_state['aktif_uygulama'] is None:
    st.markdown(f"<div style='text-align: center; font-style: italic; color: {txt}; margin-bottom: 20px; font-size: 18px;'>✨ \"{gunun_sozu}\"</div>", unsafe_allow_html=True)

# --- ARKA PLAN GÜLLERİ ---
if 'guller_html' not in st.session_state:
    guller_html = "<div style='position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 999; overflow: hidden;'>"
    for i in range(30):
        sol_konum = random.randint(0, 100); hiz = random.randint(15, 30); gecikme = random.randint(0, 20); boyut = random.randint(14, 24)
        guller_html += f"<div style='position: absolute; top: -10%; left: {sol_konum}%; font-size: {boyut}px; animation: ucusan_guller {hiz}s linear -{gecikme}s infinite;'>🌹</div>"
    guller_html += "</div>"
    st.session_state['guller_html'] = guller_html

st.markdown(f"""
<style>
@keyframes ucusan_guller {{
    0% {{ transform: translateY(0) rotate(0deg) translateX(0); opacity: 0; }}
    10% {{ opacity: 0.8; }}
    50% {{ transform: translateY(50vh) rotate(180deg) translateX(20px); }}
    90% {{ opacity: 0.8; }}
    100% {{ transform: translateY(105vh) rotate(360deg) translateX(-20px); opacity: 0; }}
}}
.guller-kapsayici div {{ filter: {guller_filter}; }}
</style>
<div class="guller-kapsayici">{st.session_state['guller_html']}</div>
""", unsafe_allow_html=True)

st.divider()

def c_karsilama():
    st.subheader("Hoş Geldin Canım! ❤")
    st.write("Bu zorlu maratonda her anında yanındayım. Derin bir nefes al ve asla pes etme.")
    st.write("---") 
    st.subheader("Biraz Mola & Motivasyon ☕")
    
    if st.button("Günün Sürpriz Notunu Oku 💌", key="not_btn"):
        genis_not_havuzu = [
            "Bütün emeklerinin karşılığını fazlasıyla alacaksın, buna yürekten inanıyorum!",
            "Şu an yorulduğunu biliyorum ama hayallerine her zamankinden çok daha yakınsın. ❤️",
            "Seninle ne kadar gurur duyduğumu kelimelerle anlatamam Sude!",
            "Kahveni yudumla, derin bir nefes al. Bu işin üstesinden geleceksin!",
            "Unutma; en karanlık gecenin sabahı en güzel güneştir. Harika gidiyorsun!",
            "Zorluklar seni durdurmak için değil, ne kadar güçlü olduğunu göstermek içindir.",
            "Bugün attığın her küçük adım, yarınki üniversite kapısını aralıyor 🎓",
            "Arda arkanda! Ne zaman yorulsan buradayım, birlikte başaracağız."
        ]
        msj = random.choice(genis_not_havuzu)
        st.markdown(f"""<div style="background-color: {card}; padding: 25px; border-left: 5px solid {border}; border-radius: 8px; box-shadow: 2px 2px 15px rgba(0,0,0,0.1); margin-top: 15px; font-style: italic; color: {txt}; text-align: center;">"{msj}"<span style="font-weight: bold; color: {hdr}; margin-top: 15px; display: block;">— Arda</span></div>""", unsafe_allow_html=True)
        st.balloons()
    st.write("---")

def c_todo():
    st.subheader("📝 Yapılacaklar Listesi")
    todo_dosya = "todo_listesi.csv"
    try:
        df_todo = pd.read_csv(todo_dosya) if os.path.exists(todo_dosya) else pd.DataFrame(columns=["Görev", "Tamamlandi"])
    except Exception:
        df_todo = pd.DataFrame(columns=["Görev", "Tamamlandi"])
        
    with st.form("todo_form", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        with c1: yeni_gorev = st.text_input("Yeni görev:", placeholder="Soru çözümü vb...", label_visibility="collapsed")
        with c2: ekle_btn = st.form_submit_button("Ekle ➕")
        if ekle_btn and yeni_gorev.strip():
            df_todo = pd.concat([df_todo, pd.DataFrame([{"Görev": yeni_gorev.strip(), "Tamamlandi": False}])], ignore_index=True)
            try: df_todo.to_csv(todo_dosya, index=False)
            except Exception: pass
            st.rerun()
    if len(df_todo) > 0:
        st.write("")
        for idx, row in df_todo.iterrows():
            if not row["Tamamlandi"]:
                if st.checkbox(row["Görev"], key=f"aktif_{idx}"):
                    df_todo.at[idx, "Tamamlandi"] = True
                    try: df_todo.to_csv(todo_dosya, index=False)
                    except Exception: pass
                    st.balloons(); st.rerun()
            else: st.checkbox(f"~~{row['Görev']}~~", value=True, disabled=True, key=f"pasif_{idx}")
        if df_todo["Tamamlandi"].any() and st.button("🧹 Temizle"):
            df_todo = df_todo[df_todo["Tamamlandi"] == False]
            try: df_todo.to_csv(todo_dosya, index=False)
            except Exception: pass
            st.rerun()
    else: st.info("Listen şu an boş."); st.write("---")

def c_su():
    st.subheader("💧 Su İçmeyi Unutma!")
    su_dosya = "su_takip.csv"; bugun_str = datetime.date.today().strftime("%d.%m.%Y")
    try:
        if os.path.exists(su_dosya):
            df_su = pd.read_csv(su_dosya)
            if df_su.iloc[0]["Tarih"] != bugun_str: df_su = pd.DataFrame([{"Tarih": bugun_str, "Bardak": 0}]); df_su.to_csv(su_dosya, index=False)
        else: df_su = pd.DataFrame([{"Tarih": bugun_str, "Bardak": 0}]); df_su.to_csv(su_dosya, index=False)
    except Exception:
        df_su = pd.DataFrame([{"Tarih": bugun_str, "Bardak": 0}])
        
    mevcut_su = int(df_su.iloc[0]["Bardak"])
    s1, s2 = st.columns([2, 1])
    with s1:
        bardaklar = "💧" * mevcut_su + "🧊" * (8 - mevcut_su) if mevcut_su <= 8 else "💧" * 8 + f" (+{mevcut_su-8})"
        st.markdown(f"<h3 style='margin:0; padding:0; font-size: 24px;'>{bardaklar}</h3>", unsafe_allow_html=True); st.caption(f"Hedef: 8 Bardak | İçilen: {mevcut_su}")
    with s2:
        if st.button("İçtim 🚰", use_container_width=True):
            df_su.at[0, "Bardak"] = mevcut_su + 1
            try: df_su.to_csv(su_dosya, index=False)
            except Exception: pass
            if mevcut_su + 1 == 8: st.success("Hedef tamam!"); st.balloons()
            st.rerun()
    st.write("---")

def c_oduller():
    st.subheader("🎁 Arda'nın Ödül Sistemi")
    max_tyt = 0.0; max_saat = 0.0; kayitli_gun_sayisi = 0
    try:
        if os.path.exists("deneme_netleri.csv"):
            tdf = pd.read_csv("deneme_netleri.csv"); tdf = tdf[tdf["Sınav"] == "TYT"]
            if len(tdf) > 0: max_tyt = tdf["Toplam Net"].max()
        if os.path.exists("gunluk_ozet.csv"):
            gdf = pd.read_csv("gunluk_ozet.csv"); kayitli_gun_sayisi = len(gdf)
            if kayitli_gun_sayisi > 0: max_saat = gdf["CalismaSaati"].max()
    except Exception:
        pass
        
    with st.expander("Kilitli Başarılar ve Ödülleri Gör 👀"):
        if max_saat >= 8.0: st.success("🔓 **Demir İrade (8 Saat!)** \n\nÖdül: İlk fırsatta favori yemeğin benden!")
        else: st.warning(f"🔒 **Demir İrade:** Bir günde en az 8 saat çalış. (Rekorun: {max_saat}s)")
        if kayitli_gun_sayisi >= 5: st.success("🔓 **İstikrar Zinciri (5 Gün!)** \n\nÖdül: Ufak bir sürpriz hediye seni bekliyor!")
        else: st.info(f"🔒 **İstikrar Zinciri:** Sistemi pes etmeden 5 gün kullan. (Mevcut: {kayitli_gun_sayisi} gün)")
        if max_tyt >= 85.0: st.success("🔓 **Zirve Yürüyüşü (85 Net!)** \n\nÖdül: Birlikte geziyor ve tatlı yiyoruz! 🎉")
        else: st.error(f"🔒 **Zirve Yürüyüşü:** TYT'de 85 neti aş! (Rekorun: {max_tyt} net)")
        ozel_dosya = "ozel_gorevler.csv"
        try:
            if os.path.exists(ozel_dosya) and len(pd.read_csv(ozel_dosya)) > 0:
                st.write("---")
                for idx, row in pd.read_csv(ozel_dosya).iterrows(): st.info(f"🎯 **Özel Görev:** {row['Gorev']}\n\n🎁 **Ödül:** {row['Odul']}")
        except Exception:
            pass

# --- TAM OTOMATİK KRONOMETRE & POMODORO SİSTEMİ ---
def c_pomodoro():
    sayac_js = """<script>var countDownDate = new Date("Jun 19, 2027 10:15:00").getTime(); setInterval(function() { var now = new Date().getTime(); var distance = countDownDate - now; document.getElementById("clock").innerHTML = Math.floor(distance / (1000 * 60 * 60 * 24)) + " Gün " + Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)) + " Saat " + Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)) + " Dk"; }, 1000);</script>"""
    saniyeli_sayac = f"""<style>body {{ background-color: {bg}; margin: 0; padding: 0; overflow: hidden; }}</style><div style="text-align: center; font-family: 'Arial', sans-serif; padding: 20px; background-color: {card}; border-radius: 10px; border: 2px solid {border}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;"><div id="clock" style="font-size: 24px; font-weight: bold; color: {hdr};">Yükleniyor...</div><p style="color: {txt}; font-size: 14px; margin-top: 10px;">YKS'ye Kalan Süre</p></div>""" + sayac_js
    components.html(saniyeli_sayac, height=130)

    st.subheader("🍅 Çalışma Masası")
    calisma_turu = st.radio("Mod:", ["Pomodoro (25 dk odak)", "Kronometre (Serbest)"], horizontal=True, label_visibility="collapsed")

    if 'pomo_baslama' not in st.session_state: st.session_state['pomo_baslama'] = None
    if 'krono_baslama' not in st.session_state: st.session_state['krono_baslama'] = None

    if calisma_turu == "Pomodoro (25 dk odak)":
        if st.session_state['pomo_baslama'] is None:
            if st.button("▶️ 25 Dakika Pomodoro Başlat", use_container_width=True):
                st.session_state['pomo_baslama'] = datetime.datetime.now()
                st.rerun()
        else:
            gecen_sn = int((datetime.datetime.now() - st.session_state['pomo_baslama']).total_seconds())
            kalan_sn = max(25 * 60 - gecen_sn, 0)
            
            pomodoro_js = f"""<script>let tl = {kalan_sn}; let d = document.getElementById('p-time'); setInterval(()=>{{if(tl>0)tl--; let m=Math.floor(tl/60); let s=tl%60; d.textContent=(m<10?"0"+m:m)+":"+(s<10?"0"+s:s);}},1000);</script>"""
            pom_html = f"""<style>body {{ background-color: {bg}; margin: 0; padding: 0; font-family: Arial; text-align: center; color: {txt}; }}</style><div style="background-color: {card}; border: 2px solid {border}; border-radius: 10px; padding: 20px;"><div id="p-time" style="font-size: 48px; font-weight: bold; color: {hdr};">--:--</div></div>""" + pomodoro_js
            components.html(pom_html, height=130)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🏁 Bitir ve 25 Dakikayı Kaydet", use_container_width=True):
                    st.session_state['toplam_calisilan_dakika'] += 25
                    st.session_state['pomo_baslama'] = None
                    st.success("🎉 25 dakika eklendi!")
                    st.rerun()
            with c2:
                if st.button("❌ İptal Et (Kaydetme)", use_container_width=True):
                    st.session_state['pomo_baslama'] = None
                    st.rerun()

    else:
        if st.session_state['krono_baslama'] is None:
            if st.button("▶️ Kronometreyi Başlat", use_container_width=True):
                st.session_state['krono_baslama'] = datetime.datetime.now()
                st.rerun()
        else:
            gecen_sn = int((datetime.datetime.now() - st.session_state['krono_baslama']).total_seconds())
            krono_js = f"""<script>let seconds = {gecen_sn}; let d = document.getElementById('k-time'); setInterval(()=>{{seconds++; let h=Math.floor(seconds/3600); let m=Math.floor((seconds%3600)/60); let s=seconds%60; let pad=v=>v<10?"0"+v:v; d.textContent=pad(h)+":"+pad(m)+":"+pad(s);}},1000);</script>"""
            kron_html = f"""<style>body {{ background-color: {bg}; margin: 0; padding: 0; font-family: Arial; text-align: center; color: {txt}; }}</style><div style="background-color: {card}; border: 2px solid {border}; border-radius: 10px; padding: 20px;"><div id="k-time" style="font-size: 48px; font-weight: bold; color: {hdr};">00:00:00</div></div>""" + krono_js
            components.html(kron_html, height=130)
            
            gercek_dk = gecen_sn // 60
            kaydedilecek_dk = max(gercek_dk, 1) # En az 1 dakika kaydetsin
            
            st.info(f"Şu ana kadar geçen süre: **{gercek_dk} dakika**")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"🏁 Bitir ve {kaydedilecek_dk} Dk Kaydet", use_container_width=True):
                    st.session_state['toplam_calisilan_dakika'] += kaydedilecek_dk
                    st.session_state['krono_baslama'] = None
                    st.success(f"🎉 {kaydedilecek_dk} dakika eklendi!")
                    st.rerun()
            with c2:
                if st.button("❌ İptal Et (Kaydetme)", use_container_width=True):
                    st.session_state['krono_baslama'] = None
                    st.rerun()

    st.markdown(f"""
    <div style="background-color: {card}; border: 2px dashed {border}; padding: 15px; border-radius: 10px; text-align: center; margin-top: 15px;">
        <h4 style="color: {hdr}; margin: 0;">⏱ Bugün Toplam Çalışılan: <span style="color:{hdr};">{st.session_state['toplam_calisilan_dakika']} Dakika</span></h4>
        <p style="font-size: 13px; color: {txt}; margin-top: 5px;">Gün sonunda bu sayıya bakarak günlük çalışma saatine yazabilirsin! (Örn: {round(st.session_state['toplam_calisilan_dakika']/60, 2)} saat)</p>
    </div>
    """, unsafe_allow_html=True)

    nefes_html = f"""<style>body {{ background-color: {bg}; margin: 0; padding: 0; overflow: hidden; }}</style><div style="text-align: center; padding: 15px; background-color: {card}; border-radius: 10px; border: 2px solid {border}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);"><p style="color: {txt}; font-size: 13px; margin-bottom: 25px; margin-top:0;"><b>Stres anında çemberi izle:</b><br><span style="color:{hdr};">4sn Al - 7sn Tut - 8sn Ver</span></p><div style="position: relative; width: 80px; height: 80px; margin: 0 auto;"><div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 20px; height: 20px; background-color: {btn}; border-radius: 50%; animation: breathe 19s infinite linear;"></div></div></div><style>@keyframes breathe {{ 0% {{ transform: translate(-50%, -50%) scale(1); background-color: {btn}; }} 21% {{ transform: translate(-50%, -50%) scale(3.5); background-color: {btn_hover}; }} 58% {{ transform: translate(-50%, -50%) scale(3.5); background-color: {border}; }} 100% {{ transform: translate(-50%, -50%) scale(1); background-color: {btn}; }} }}</style>"""
    components.html(nefes_html, height=200)

def c_gunluk():
    st.header("🌙 Günü Kapat & İç Dök")
    gunluk_dosya = "gunluk_ozet.csv"
    try:
        df_gunluk = pd.read_csv(gunluk_dosya) if os.path.exists(gunluk_dosya) else pd.DataFrame(columns=["Tarih", "CalismaSaati", "GunlukNotu"])
    except Exception:
        df_gunluk = pd.DataFrame(columns=["Tarih", "CalismaSaati", "GunlukNotu"])

    with st.form("gunu_kapat_formu", clear_on_submit=True):
        bugun = datetime.date.today().strftime("%d.%m.%Y"); st.write(f"**Tarih:** {bugun}")
        tavsiye_saat = round(st.session_state['toplam_calisilan_dakika'] / 60.0, 2)
        calisma_saati = st.number_input(f"Kaç Saat Çalıştın? (Sayaçta biriken: {tavsiye_saat} saat)", min_value=0.0, max_value=24.0, value=tavsiye_saat, step=0.5)
        gunluk_not = st.text_area("Gizli Günlüğün:", placeholder="Bugün çok yoruldum ama...")
        if st.form_submit_button("Günü Kaydet ve Uyumaya Git 💤"):
            df_gunluk = pd.concat([df_gunluk, pd.DataFrame([{"Tarih": bugun, "CalismaSaati": calisma_saati, "GunlukNotu": gunluk_not}])], ignore_index=True)
            try: df_gunluk.to_csv(gunluk_dosya, index=False)
            except Exception: pass
            st.success("Kaydedildi! Harika bir iş çıkardın. 💖"); st.balloons()

def c_net_takibi():
    st.header("📈 Net Takibi ve Analiz")
    hedef_universite = "Hayalimdeki Üniversite & Bölüm"; hedef_tyt_net = 90.0; rekor_net = 0.0
    dosya_adi = "deneme_netleri.csv"
    try:
        df_netler = pd.read_csv(dosya_adi) if os.path.exists(dosya_adi) else pd.DataFrame(columns=["Deneme Adı", "Sınav", "Türkçe/Edebiyat", "Matematik", "Sosyal", "Fen", "Toplam Net"])
    except Exception:
        df_netler = pd.DataFrame(columns=["Deneme Adı", "Sınav", "Türkçe/Edebiyat", "Matematik", "Sosyal", "Fen", "Toplam Net"])
        
    tyt = df_netler[df_netler["Sınav"] == "TYT"]
    if len(tyt) > 0: rekor_net = tyt["Toplam Net"].max()
    yuzde = min(int((rekor_net / hedef_tyt_net) * 100), 100)
    
    st.markdown(f"""<div style="background-color: {card}; padding: 20px; border-radius: 10px; border: 2px solid {border}; margin-bottom: 25px;"><h3 style="color: {hdr}; margin-top: 0; text-align: center;">🎓 Hedef: {hedef_universite}</h3><p style="text-align: center; color: {txt}; font-weight: bold;">TYT Hedefi: {hedef_tyt_net} | Rekor: {rekor_net}</p><div style="background-color: {btn}; border-radius: 20px; width: 100%; height: 25px; margin-top: 10px;"><div style="background-color: {border}; width: {yuzde}%; height: 100%; border-radius: 20px; text-align: center; color: white; font-weight: bold; line-height: 25px;">%{yuzde}</div></div></div>""", unsafe_allow_html=True)

    with st.form("net_giris_formu"):
        st.subheader("Yeni Deneme Sonucu Ekle 📝")
        deneme_adi = st.text_input("Deneme Adı:")
        sinav_turu = st.radio("Hangi Sınav?", ["TYT", "AYT"], horizontal=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1: turkce = st.number_input("Tr/Edb", min_value=0.0, step=0.25)
        with col2: mat = st.number_input("Mat", min_value=0.0, step=0.25)
        with col3: sosyal = st.number_input("Sos", min_value=0.0, step=0.25)
        with col4: fen = st.number_input("Fen", min_value=0.0, step=0.25)
        if st.form_submit_button("Netleri Kaydet 💾") and deneme_adi:
            df_netler = pd.concat([df_netler, pd.DataFrame([{"Deneme Adı": deneme_adi, "Sınav": sinav_turu, "Türkçe/Edebiyat": turkce, "Matematik": mat, "Sosyal": sosyal, "Fen": fen, "Toplam Net": turkce+mat+sosyal+fen}])], ignore_index=True)
            try: df_netler.to_csv(dosya_adi, index=False)
            except Exception: pass
            st.success(f"Eklendi!"); st.rerun()

    if len(df_netler) > 0:
        tab_tyt, tab_ayt = st.tabs(["TYT Analizi", "AYT Analizi"])
        with tab_tyt:
            tyt_v = df_netler[df_netler["Sınav"] == "TYT"]
            if len(tyt_v) > 0:
                i = tyt_v.iloc[0]; s = tyt_v.iloc[-1]; m1,m2,m3,m4,m5 = st.columns(5)
                m1.metric("Türkçe", f"{s['Türkçe/Edebiyat']}", f"{s['Türkçe/Edebiyat']-i['Türkçe/Edebiyat']:.2f}")
                m2.metric("Mat", f"{s['Matematik']}", f"{s['Matematik']-i['Matematik']:.2f}")
                m3.metric("Sos", f"{s['Sosyal']}", f"{s['Sosyal']-i['Sosyal']:.2f}")
                m4.metric("Fen", f"{s['Fen']}", f"{s['Fen']-i['Fen']:.2f}")
                m5.metric("TOPLAM", f"{s['Toplam Net']}", f"{s['Toplam Net']-i['Toplam Net']:.2f}")
                st.line_chart(tyt_v.set_index("Deneme Adı")["Toplam Net"])
        with tab_ayt:
            ayt_v = df_netler[df_netler["Sınav"] == "AYT"]
            if len(ayt_v) > 0:
                i = ayt_v.iloc[0]; s = ayt_v.iloc[-1]; m1,m2,m3,m4,m5 = st.columns(5)
                m1.metric("Edb", f"{s['Türkçe/Edebiyat']}", f"{s['Türkçe/Edebiyat']-i['Türkçe/Edebiyat']:.2f}")
                m2.metric("Mat", f"{s['Matematik']}", f"{s['Matematik']-i['Matematik']:.2f}")
                m3.metric("Sos", f"{s['Sosyal']}", f"{s['Sosyal']-i['Sosyal']:.2f}")
                m4.metric("Fen", f"{s['Fen']}", f"{s['Fen']-i['Fen']:.2f}")
                m5.metric("TOPLAM", f"{s['Toplam Net']}", f"{s['Toplam Net']-i['Toplam Net']:.2f}")
                st.line_chart(ayt_v.set_index("Deneme Adı")["Toplam Net"])

def c_konu_ilerleme():
    st.divider()
    st.subheader("📚 Müfredat & Konu İlerleme Durumu")
    konu_dosya = "konu_ilerleme.csv"
    varsayilan_konular = [
        # TÜRKÇE
        {"Ders": "Türkçe", "Konu": "Sözcükte Anlam", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Cümlede Anlam", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Paragrafta Anlam", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Anlatım Biçimleri", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Ses Bilgisi", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Yazım Kuralları", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Noktalama İşaretleri", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Sözcükte Yapı", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Sözcük Türleri", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Edat-Bağlaç-Ünlem", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Fiil-Ek Fiil", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Fiilimsi", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Fiilde Çatı", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Deyim ve Atasözü", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Cümlenin Öğeleri", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Cümle Türleri", "Bitti": False}, {"Ders": "Türkçe", "Konu": "Anlatım Bozuklukları", "Bitti": False},
        # MATEMATİK
        {"Ders": "Matematik", "Konu": "Temel Kavramlar", "Bitti": False}, {"Ders": "Matematik", "Konu": "Sayı Basamakları", "Bitti": False}, {"Ders": "Matematik", "Konu": "Bölme ve Bölünebilme", "Bitti": False}, {"Ders": "Matematik", "Konu": "EBOB-EKOK", "Bitti": False}, {"Ders": "Matematik", "Konu": "Rasyonel Sayılar-Ondalık Sayılar", "Bitti": False}, {"Ders": "Matematik", "Konu": "Basit Eşitsizlikler", "Bitti": False}, {"Ders": "Matematik", "Konu": "Mutlak Değer", "Bitti": False}, {"Ders": "Matematik", "Konu": "Üslü Sayılar", "Bitti": False}, {"Ders": "Matematik", "Konu": "Köklü Sayılar", "Bitti": False}, {"Ders": "Matematik", "Konu": "Çarpanlara Ayırma", "Bitti": False}, {"Ders": "Matematik", "Konu": "Oran Orantı", "Bitti": False}, {"Ders": "Matematik", "Konu": "Denklem Çözme", "Bitti": False}, {"Ders": "Matematik", "Konu": "Problemler", "Bitti": False}, {"Ders": "Matematik", "Konu": "Kümeler-Kartezyen Çarpımı", "Bitti": False}, {"Ders": "Matematik", "Konu": "Fonksiyonlar", "Bitti": False}, {"Ders": "Matematik", "Konu": "Permütasyon", "Bitti": False}, {"Ders": "Matematik", "Konu": "Kombinasyon", "Bitti": False}, {"Ders": "Matematik", "Konu": "Binom", "Bitti": False}, {"Ders": "Matematik", "Konu": "Olasılık", "Bitti": False}, {"Ders": "Matematik", "Konu": "İstatistik", "Bitti": False}, {"Ders": "Matematik", "Konu": "2. Dereceden Denklemler", "Bitti": False}, {"Ders": "Matematik", "Konu": "Karmaşık Sayılar", "Bitti": False}, {"Ders": "Matematik", "Konu": "Polinomlar", "Bitti": False}, {"Ders": "Matematik", "Konu": "Mantık", "Bitti": False}, {"Ders": "Matematik", "Konu": "Veri Analizi", "Bitti": False},
        # GEOMETRİ
        {"Ders": "Geometri", "Konu": "Doğruda ve Üçgende Açılar", "Bitti": False}, {"Ders": "Geometri", "Konu": "Üçgende Açı-Kenar Bağıntıları", "Bitti": False}, {"Ders": "Geometri", "Konu": "Üçgende Benzerlik", "Bitti": False}, {"Ders": "Geometri", "Konu": "Üçgende Açıortay-Kenarortay", "Bitti": False}, {"Ders": "Geometri", "Konu": "Dik Üçgen", "Bitti": False}, {"Ders": "Geometri", "Konu": "İkizkenar Üçgen", "Bitti": False}, {"Ders": "Geometri", "Konu": "Eşkenar Üçgen", "Bitti": False}, {"Ders": "Geometri", "Konu": "Üçgende Alan", "Bitti": False}, {"Ders": "Geometri", "Konu": "Çokgenler", "Bitti": False}, {"Ders": "Geometri", "Konu": "Dörtgenler", "Bitti": False}, {"Ders": "Geometri", "Konu": "Yamuk-Paralelkenar", "Bitti": False}, {"Ders": "Geometri", "Konu": "Eşkenar Dörtgen", "Bitti": False}, {"Ders": "Geometri", "Konu": "Dikdörtgen", "Bitti": False}, {"Ders": "Geometri", "Konu": "Kare", "Bitti": False}, {"Ders": "Geometri", "Konu": "Deltoid", "Bitti": False}, {"Ders": "Geometri", "Konu": "Çemberde Açı", "Bitti": False}, {"Ders": "Geometri", "Konu": "Çemberde Uzunluk", "Bitti": False}, {"Ders": "Geometri", "Konu": "Dairenin Çevresi ve Alanı", "Bitti": False}, {"Ders": "Geometri", "Konu": "Doğrunun Analitik İncelenmesi", "Bitti": False}, {"Ders": "Geometri", "Konu": "Çemberin Analitik İncelenmesi", "Bitti": False}, {"Ders": "Geometri", "Konu": "Katı Cisimler (Prizma, Küp, Piramit, Silindir, Koni, Küre)", "Bitti": False},
        # TARİH
        {"Ders": "Tarih", "Konu": "Tarih Bilimine Giriş", "Bitti": False}, {"Ders": "Tarih", "Konu": "Uygarlığın Doğuşu ve İlk Uygarlıklar", "Bitti": False}, {"Ders": "Tarih", "Konu": "İlk Türk Devletleri", "Bitti": False}, {"Ders": "Tarih", "Konu": "İslam Tarihi ve Uygarlığı", "Bitti": False}, {"Ders": "Tarih", "Konu": "Türk-İslam Devletleri", "Bitti": False}, {"Ders": "Tarih", "Konu": "Türkler'in İslamiyeti Kabulü", "Bitti": False}, {"Ders": "Tarih", "Konu": "Türkiye Tarihi", "Bitti": False}, {"Ders": "Tarih", "Konu": "Beylikten Devlete (1300-1453)", "Bitti": False}, {"Ders": "Tarih", "Konu": "Dünya Gücü: Osmanlı Devleti", "Bitti": False}, {"Ders": "Tarih", "Konu": "Osmanlı Duraklama Dönemi", "Bitti": False}, {"Ders": "Tarih", "Konu": "Gerileme Devri (1699 – 1792)", "Bitti": False}, {"Ders": "Tarih", "Konu": "Arayış Yılları (17. Yüzyıl)", "Bitti": False}, {"Ders": "Tarih", "Konu": "Avrupa ve Osmanlı Devleti (18. Yüzyıl)", "Bitti": False}, {"Ders": "Tarih", "Konu": "En Uzun Yüzyıl (1800-1922)", "Bitti": False}, {"Ders": "Tarih", "Konu": "20. Yüzyıl Başlarında Osmanlı Devleti", "Bitti": False}, {"Ders": "Tarih", "Konu": "XIX. YY Osmanlı Devleti", "Bitti": False}, {"Ders": "Tarih", "Konu": "1. Dünya Savaşı – Milli Mücadeleye Hazırlık D.", "Bitti": False}, {"Ders": "Tarih", "Konu": "Kurtuluş Savaşında Cepheler", "Bitti": False}, {"Ders": "Tarih", "Konu": "Türk İnkılabı", "Bitti": False}, {"Ders": "Tarih", "Konu": "Atatürkçülük ve Atatürk İlkeleri", "Bitti": False}, {"Ders": "Tarih", "Konu": "Türk Dış Politikası", "Bitti": False},
        # COĞRAFYA
        {"Ders": "Coğrafya", "Konu": "İnsan ve Doğa", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Dünya'nın Şekli ve Hareketleri", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Coğrafi Konum", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Harita Bilgisi", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Atmosfer ve Sıcaklık", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "İklimler", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Basınç ve Rüzgarlar", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Nem, Yağış ve Buharlaşma", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "İç Kuvvetler / Dış Kuvvetler", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Su – Toprak ve Bitkiler", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Nüfus-Göç-Yerleşme", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Türkiye'nin Yer Şekilleri", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Ekonomik Faaliyetler", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Bölgeler ve Ülkeler", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Uluslararası Ulaşım Hatları", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Çevre ve Toplum", "Bitti": False}, {"Ders": "Coğrafya", "Konu": "Doğal Afetler", "Bitti": False},
        # FİZİK
        {"Ders": "Fizik", "Konu": "Fizik Bilimine Giriş", "Bitti": False}, {"Ders": "Fizik", "Konu": "Madde ve Özellikleri", "Bitti": False}, {"Ders": "Fizik", "Konu": "Kuvvet ve Hareket", "Bitti": False}, {"Ders": "Fizik", "Konu": "İş, Güç ve Enerji", "Bitti": False}, {"Ders": "Fizik", "Konu": "Isı, Sıcaklık ve Genleşme", "Bitti": False}, {"Ders": "Fizik", "Konu": "Basınç", "Bitti": False}, {"Ders": "Fizik", "Konu": "Kaldırma Kuvveti", "Bitti": False}, {"Ders": "Fizik", "Konu": "Elektrik ve Manyetizma", "Bitti": False}, {"Ders": "Fizik", "Konu": "Dalgalar", "Bitti": False}, {"Ders": "Fizik", "Konu": "Optik", "Bitti": False},
        # KİMYA
        {"Ders": "Kimya", "Konu": "Kimya Bilimi", "Bitti": False}, {"Ders": "Kimya", "Konu": "Atom ve Periyodik Sistem", "Bitti": False}, {"Ders": "Kimya", "Konu": "Kimyasal Türler Arası Etkileşimler", "Bitti": False}, {"Ders": "Kimya", "Konu": "Maddenin Halleri", "Bitti": False}, {"Ders": "Kimya", "Konu": "Doğa ve Kimya", "Bitti": False}, {"Ders": "Kimya", "Konu": "Kimyanın Temel Kanunları ve Kimyasal Hesaplamalar", "Bitti": False}, {"Ders": "Kimya", "Konu": "Karışımlar", "Bitti": False}, {"Ders": "Kimya", "Konu": "Asitler-Bazlar ve Tuzlar", "Bitti": False}, {"Ders": "Kimya", "Konu": "Kimya Her Yerde", "Bitti": False},
        # BİYOLOJİ
        {"Ders": "Biyoloji", "Konu": "Yaşam Bilimi Biyoloji", "Bitti": False}, {"Ders": "Biyoloji", "Konu": "Hücre", "Bitti": False}, {"Ders": "Biyoloji", "Konu": "Canlılar Dünyası", "Bitti": False}, {"Ders": "Biyoloji", "Konu": "Hücre Bölünmeleri ve Üreme", "Bitti": False}, {"Ders": "Biyoloji", "Konu": "Kalıtımın Genel İlkeleri", "Bitti": False}, {"Ders": "Biyoloji", "Konu": "Ekosistem Ekolojisi ve Güncel Çevre Sorunları", "Bitti": False},
        # FELSEFE
        {"Ders": "Felsefe", "Konu": "Felsefe'nin Alanı", "Bitti": False}, {"Ders": "Felsefe", "Konu": "Bilgi Felsefesi", "Bitti": False}, {"Ders": "Felsefe", "Konu": "Bilim Felsefesi", "Bitti": False}, {"Ders": "Felsefe", "Konu": "Varlık Felsefesi", "Bitti": False}, {"Ders": "Felsefe", "Konu": "Ahlak Felsefesi", "Bitti": False}, {"Ders": "Felsefe", "Konu": "Siyaset Felsefesi", "Bitti": False}, {"Ders": "Felsefe", "Konu": "Sanat Felsefesi", "Bitti": False}, {"Ders": "Felsefe", "Konu": "Din Felsefesi", "Bitti": False},
        # DİN KÜLTÜRÜ
        {"Ders": "Din Kültürü", "Konu": "İnsan ve Din (İnanç)", "Bitti": False}, {"Ders": "Din Kültürü", "Konu": "İbadet", "Bitti": False}, {"Ders": "Din Kültürü", "Konu": "Hz. Muhammed'in Hayatı", "Bitti": False}, {"Ders": "Din Kültürü", "Konu": "Vahiy ve Akıl", "Bitti": False}, {"Ders": "Din Kültürü", "Konu": "İslam Düşüncesi ve Yorumu", "Bitti": False}, {"Ders": "Din Kültürü", "Konu": "İslamda Değerler, Sanat ve Laiklik", "Bitti": False}, {"Ders": "Din Kültürü", "Konu": "Yaşayan Dinler", "Bitti": False}
    ]
    try:
        if os.path.exists(konu_dosya): df_konu = pd.read_csv(konu_dosya)
        else: df_konu = pd.DataFrame(varsayilan_konular); df_konu.to_csv(konu_dosya, index=False)
    except Exception:
        df_konu = pd.DataFrame(varsayilan_konular)
    
    toplam = len(df_konu); biten = int(df_konu["Bitti"].sum()) if not df_konu.empty else 0
    yuzde = int((biten / toplam) * 100) if toplam > 0 else 0
    st.markdown(f"""<div style="background-color: {card}; padding: 15px; border-radius: 10px; border: 2px solid {border}; margin-bottom: 20px;"><h4 style="color: {hdr}; margin-top: 0; text-align: center;">Genel Müfredat Oranı: %{yuzde}</h4><div style="background-color: {btn}; border-radius: 20px; width: 100%; height: 22px;"><div style="background-color: {border}; width: {yuzde}%; height: 100%; border-radius: 20px; text-align: center; color: white; font-weight: bold; font-size: 14px; line-height: 22px;">%{yuzde}</div></div></div>""", unsafe_allow_html=True)
    
    dersler = df_konu["Ders"].unique() if not df_konu.empty else []
    if len(dersler) > 0:
        secilen_ders = st.selectbox("İncelemek İstediğin Dersi Seç:", dersler)
        for idx, row in df_konu[df_konu["Ders"] == secilen_ders].iterrows():
            durum = st.checkbox(row["Konu"], value=row["Bitti"], key=f"konu_{idx}")
            if durum != row["Bitti"]:
                df_konu.at[idx, "Bitti"] = durum
                try: df_konu.to_csv(konu_dosya, index=False)
                except Exception: pass
                st.rerun()

def c_kumbara():
    st.divider(); st.subheader("🎯 Eksik Avcısı (Kumbara)")
    kumbara_dosya = "soru_kumbara.csv"
    try: df_kumbara = pd.read_csv(kumbara_dosya) if os.path.exists(kumbara_dosya) else pd.DataFrame(columns=["Eksik", "Durum"])
    except Exception: df_kumbara = pd.DataFrame(columns=["Eksik", "Durum"])
    
    with st.form("kumbara_form", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        with c1: yeni = st.text_input("Eksik konu/soru:", placeholder="Örn: Ses Bilgisi", label_visibility="collapsed")
        with c2: 
            if st.form_submit_button("Kumbaraya At") and yeni.strip():
                df_kumbara = pd.concat([df_kumbara, pd.DataFrame([{"Eksik": yeni.strip(), "Durum": False}])], ignore_index=True)
                try: df_kumbara.to_csv(kumbara_dosya, index=False)
                except Exception: pass
                st.rerun()
    if len(df_kumbara) > 0:
        for idx, row in df_kumbara.iterrows():
            if not row["Durum"]:
                if st.checkbox(row["Eksik"], key=f"eksik_{idx}"):
                    df_kumbara.at[idx, "Durum"] = True
                    try: df_kumbara.to_csv(kumbara_dosya, index=False)
                    except Exception: pass
                    st.balloons(); st.rerun()
            else: st.checkbox(f"~~{row['Eksik']}~~ ✅", value=True, disabled=True, key=f"coz_{idx}")
        if df_kumbara["Durum"].any() and st.button("🧹 Halledilenleri Temizle"):
            df_kumbara = df_kumbara[df_kumbara["Durum"] == False]
            try: df_kumbara.to_csv(kumbara_dosya, index=False)
            except Exception: pass
            st.rerun()

def c_muzik():
    st.header("🎧 Ders Çalışma Ortamı")
    components.html(f"""<style>body {{ background-color: {bg}; margin: 0; padding: 0; overflow: hidden; }}</style><iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/0zHr4z4SfUeKZOXv3rxVIV?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>""", height=360)

def c_panel():
    st.header("⚙️ Arda'nın Gizli Paneli")
    sifre = st.text_input("Şifre:", type="password")
    if sifre == "1905":
        st.success("Giriş Başarılı!")
        st.markdown("---")
        st.subheader("🚨 Sude'ye Canlı Sinyal Gönder")
        signal_dosya = "ardadan_mesaj.json"
        with st.form("sinyal_formu"):
             sinyal_mesaji = st.text_input("Sude'ye İletilecek Mesaj:", placeholder="Örn: Tablette mola verme zamanı! ☕")
             if st.form_submit_button("Sinyali Gönder 🚀") and sinyal_mesaji.strip():
                 s_data = {"aktif": True, "mesaj": sinyal_mesaji.strip()}
                 try:
                     with open(signal_dosya, "w", encoding="utf-8") as f: json.dump(s_data, f)
                 except Exception: pass
                 st.success("Sinyal Sude'ye iletildi! ✨")
        if st.button("Sinyali İptal Et / Kapat 🛑"):
            if os.path.exists(signal_dosya):
                s_data = {"aktif": False, "mesaj": ""}
                try:
                    with open(signal_dosya, "w", encoding="utf-8") as f: json.dump(s_data, f)
                except Exception: pass
                st.info("Sinyal kapatıldı.")
    elif sifre: st.error("İzinsiz giriş!")

# --- KADEMELİ (FALLBACK) YAPAY ZEKA SİSTEMİ ---
# --- KADEMELİ (FALLBACK) YAPAY ZEKA SİSTEMİ (HATA AYIKLAMA MODU) ---
# --- KADEMELİ (FALLBACK) YAPAY ZEKA SİSTEMİ (HATALAR ÇÖZÜLDÜ) ---
# --- KADEMELİ (FALLBACK) YAPAY ZEKA SİSTEMİ (KESİN ÇÖZÜM) ---
# --- KÜTÜPHANESİZ, KESİN ÇALIŞAN YAPAY ZEKA SİSTEMİ ---
# --- KÜTÜPHANESİZ, TÜM MODELLERİ DENEYEN GARANTİ SİSTEM ---
# --- KÜTÜPHANESİZ, KESİN ÇALIŞAN YAPAY ZEKA SİSTEMİ (GÜNCEL 3.8 FLASH) ---
# --- KÜTÜPHANESİZ, ÇİFT MOTORLU YEDEKLİ YAPAY ZEKA SİSTEMİ ---
# --- HATA DEDEKTİFLİ, ÇİFT MOTORLU YEDEKLİ YAPAY ZEKA SİSTEMİ ---
def c_yapay_zeka():
    import requests 
    
    st.header("🤖 YKS Motivasyon & Çalışma Asistanı")
    st.write("Sınav süreciyle ilgili takıldığın soruları sorabilir, taktikler alabilirsin.")
    soru = st.text_input("Bugün hangi konuda yardıma ihtiyacın var?", placeholder="Örn: Paragraf netlerimi nasıl artırabilirim?")
    

    
    if st.button("✨ Asistana Sor", use_container_width=True):
        if soru.strip():
            if (GEMINI_API_KEY == "BURAYA_KENDI_GEMINI_KEYINI_YAZ" or not GEMINI_API_KEY) and (GROQ_API_KEY == "BURAYA_KENDI_GROQ_KEYINI_YAZ" or not GROQ_API_KEY):
                st.warning("⚠️ Lütfen kodun içindeki API anahtarlarından en az birini yapıştır!")
                return
                
            with st.spinner("🤔 Arda düşünüyor..."):
                cevap = None
                kullanilan_model = ""
                hatalar = [] # Gizli hataları burada toplayacağız
                prompt = f"Sen YKS sınavına hazırlanan Sude adında bir öğrenciye destek olan ve ismi Arda olan profesyonel bir rehberlik asistanısın. Sude sana şunu sordu: '{soru}'. Sude'ye motive edici, çok tatlı, samimi, pratik ve eğitici bir cevap ver (maksimum 3-4 cümle)."

                # 1. MOTOR: GROQ (REST API)
                if GROQ_API_KEY and GROQ_API_KEY != "BURAYA_KENDI_GROQ_KEYINI_YAZ":
                    try:
                        url_groq = "https://api.groq.com/openai/v1/chat/completions"
                        headers_groq = {
                            "Authorization": f"Bearer {GROQ_API_KEY}",
                            "Content-Type": "application/json"
                        }
                        payload_groq = {
                            "model": "qwen/qwen3.8-27b", 
                            "messages": [{"role": "user", "content": prompt}]
                        }
                        res_groq = requests.post(url_groq, json=payload_groq, headers=headers_groq)
                        if res_groq.status_code == 200:
                            cevap = res_groq.json()['choices'][0]['message']['content']
                            kullanilan_model = "Groq"
                        else:
                            hatalar.append(f"🔴 Groq Reddedilme Sebebi: {res_groq.text}")
                    except Exception as e:
                        hatalar.append(f"🔴 Groq Sistem Hatası: {str(e)}")

                # 2. MOTOR: GEMINI (REST API)
                if not cevap and GEMINI_API_KEY and GEMINI_API_KEY != "BURAYA_KENDI_GEMINI_KEYINI_YAZ":
                    try:
                        url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
                        payload_gemini = {"contents": [{"parts": [{"text": prompt}]}]}
                        headers_gemini = {"Content-Type": "application/json"}
                        
                        res_gemini = requests.post(url_gemini, json=payload_gemini, headers=headers_gemini)
                        if res_gemini.status_code == 200:
                            cevap = res_gemini.json()['candidates'][0]['content']['parts'][0]['text']
                            kullanilan_model = "Google Gemini"
                        else:
                            hatalar.append(f"🔵 Gemini Reddedilme Sebebi: {res_gemini.text}")
                    except Exception as e:
                        hatalar.append(f"🔵 Gemini Sistem Hatası: {str(e)}")
                        
                # SONUÇ EKRANI
                if cevap:
                    st.info(f"💡 **Arda'nın Cevabı:**\n\n{cevap}")
                    st.caption(f"⚡ Yanıtlayan servis: {kullanilan_model}")
                else:
                    st.error("⚠️ SİSTEM YANIT VERMEDİ! İşte gerçek hatalar (Bunu bana gönder):")
                    for hata in hatalar:
                        st.write(hata)    
    # ANAHTARLARINI BURAYA YAPIŞTIR (Tırnakları silmeden):


def c_eglence():
    st.header("🕹️ Eğlence & Mola Merkezi")
    bubble_html = f"""
    <style>body {{ background-color: {bg}; margin: 0; padding: 0; overflow: hidden; }}
    .bubble {{ width: 35px; height: 35px; background-color: {btn}; border-radius: 50%; margin: 4px; display: inline-block; cursor: pointer; }}
    .bubble.popped {{ background-color: {bg}; opacity: 0.3; transform: scale(0.85); }}</style>
    <div id="bw" style="max-width: 320px; margin: 0 auto; text-align: center; padding: 15px; background-color: {card}; border-radius: 15px; border: 2px solid {border};"></div>
    <script>
        const bw = document.getElementById('bw');
        for(let i=0; i<30; i++) {{
            let b = document.createElement('div'); b.className = 'bubble';
            b.onclick = function() {{ this.classList.toggle('popped'); }};
            bw.appendChild(b);
        }}
    </script>
    """
    components.html(bubble_html, height=260)

# =========================================================
# ARAYÜZ YÖNETİCİSİ
# =========================================================
if st.session_state['arayuz'] == 'sekmeler':
    t1, t2, t3, t4, t5, t6 = st.tabs(["🏠 Ana Sayfa", "📈 Net & Eksikler", "🤖 Asistan", "🕹️ Eğlence", "🎧 Müzik", "⚙️ Panel"])
    with t1:
        s1, s2 = st.columns(2)
        with s1: c_karsilama(); c_todo(); c_su(); c_oduller()
        with s2: c_pomodoro(); c_gunluk()
    with t2: c_net_takibi(); c_konu_ilerleme(); c_kumbara()
    with t3: c_yapay_zeka()
    with t4: c_eglence()
    with t5: c_muzik()
    with t6: c_panel()
else:
    if st.session_state['aktif_uygulama'] is None:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🍅\nÇalışma\nMasası"): st.session_state['aktif_uygulama'] = 'masa'; st.rerun()
            if st.button("📈\nNet\nTakibi"): st.session_state['aktif_uygulama'] = 'net'; st.rerun()
            if st.button("🤖\nAsistan"): st.session_state['aktif_uygulama'] = 'ai'; st.rerun()
        with c2:
            if st.button("📝\nGörev\nListesi"): st.session_state['aktif_uygulama'] = 'todo'; st.rerun()
            if st.button("🎁\nÖdül\nSistemi"): st.session_state['aktif_uygulama'] = 'odul'; st.rerun()
            if st.button("🕹️\nEğlence\n& Mola"): st.session_state['aktif_uygulama'] = 'eglence'; st.rerun()
        with c3:
            if st.button("🌙\nGünlük\n& Su"): st.session_state['aktif_uygulama'] = 'gunluk'; st.rerun()
            if st.button("🎧\nOdak\nMüzik"): st.session_state['aktif_uygulama'] = 'muzik'; st.rerun()
            if st.button("⚙️\nAyarlar"): st.session_state['aktif_uygulama'] = 'panel'; st.rerun()
    else:
        st.write("---")
        if st.button("⬅️ Ana Ekrana Dön"): st.session_state['aktif_uygulama'] = None; st.rerun()
        aktif = st.session_state['aktif_uygulama']
        if aktif == 'masa': c_pomodoro()
        elif aktif == 'todo': c_todo(); c_kumbara()
        elif aktif == 'gunluk': c_su(); c_gunluk()
        elif aktif == 'net': c_net_takibi(); c_konu_ilerleme()
        elif aktif == 'odul': c_oduller()
        elif aktif == 'ai': c_yapay_zeka()
        elif aktif == 'eglence': c_eglence()
        elif aktif == 'muzik': c_muzik()
        elif aktif == 'panel': c_panel()