import streamlit as st
import random
import datetime
import streamlit.components.v1 as components
import pandas as pd
import os
import google.generativeai as genai

# --- YAPAY ZEKA (GEMINI) BAĞLANTISI ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    pass

# Tarayıcı sekmesinde görünecek başlık
st.set_page_config(page_title="Sude'nin Çalışma Alanı", page_icon="🌻", layout="wide")

# --- SİSTEM DEĞİŞKENLERİ (TEMA VE ARAYÜZ YÖNETİMİ) ---
if 'tema' not in st.session_state: st.session_state['tema'] = 'gunduz'
if 'arayuz' not in st.session_state: st.session_state['arayuz'] = 'sekmeler'
if 'aktif_uygulama' not in st.session_state: st.session_state['aktif_uygulama'] = None

# --- DİNAMİK RENK PALETİ (GECE / GÜNDÜZ MODU) ---
if st.session_state['tema'] == 'gece':
    bg = "#1E1E24"; card = "#2B2B36"; hdr = "#C084FC"; txt = "#E2E8F0"
    btn = "#3B2859"; btn_hover = "#503080"; btn_txt = "#E9D5FF"; border = "#7E22CE"
    guller_filter = "grayscale(100%) brightness(40%) sepia(100%) hue-rotate(250deg) saturate(300%)" 
else:
    bg = "#FFF5F5"; card = "#FFFFFF"; hdr = "#D6336C"; txt = "#495057"
    btn = "#FFB3C6"; btn_hover = "#FF8FAB"; btn_txt = "#590D22"; border = "#D6336C"
    guller_filter = "grayscale(100%) brightness(0%) opacity(25%)"

# --- DİNAMİK CSS (MAKYAJ) YÜKLEMESİ ---
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg} !important; transition: background-color 0.5s; }}
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

k_sol, k_sag = st.columns(2)
with k_sol:
    gece_modu = st.toggle("🌙 Gece Modu", value=(st.session_state['tema'] == 'gece'))
    if gece_modu and st.session_state['tema'] == 'gunduz': st.session_state['tema'] = 'gece'; st.rerun()
    elif not gece_modu and st.session_state['tema'] == 'gece': st.session_state['tema'] = 'gunduz'; st.rerun()
with k_sag:
    hizli_menu = st.toggle("📱 Hızlı Menü (Telefon)", value=(st.session_state['arayuz'] == 'mobil'))
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
    st.subheader("Biraz Mola ☕")
    if st.button("Günün Sürpriz Notunu Oku 💌", key="not_btn"):
        msj = random.choice(["Bütün emeklerinin karşılığını alacaksın, sana inanıyorum!", "Şu an yorulduğunu biliyorum ama hayallerine bir adım daha yaklaştın. ❤️", "Seninle gurur duyuyorum Sude!"])
        st.markdown(f"""<div style="background-color: {card}; padding: 25px; border-left: 5px solid {border}; border-radius: 8px; box-shadow: 2px 2px 15px rgba(0,0,0,0.1); margin-top: 15px; font-style: italic; color: {txt}; text-align: center;">"{msj}"<span style="font-weight: bold; color: {hdr}; margin-top: 15px; display: block;">— Arda</span></div>""", unsafe_allow_html=True)
        st.balloons()
    st.write("---")

def c_todo():
    st.subheader("📝 Yapılacaklar Listesi")
    todo_dosya = "todo_listesi.csv"
    df_todo = pd.read_csv(todo_dosya) if os.path.exists(todo_dosya) else pd.DataFrame(columns=["Görev", "Tamamlandi"])
    with st.form("todo_form", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        with c1: yeni_gorev = st.text_input("Yeni görev:", placeholder="Soru çözümü vb...", label_visibility="collapsed")
        with c2: ekle_btn = st.form_submit_button("Ekle ➕")
        if ekle_btn and yeni_gorev.strip():
            df_todo = pd.concat([df_todo, pd.DataFrame([{"Görev": yeni_gorev.strip(), "Tamamlandi": False}])], ignore_index=True); df_todo.to_csv(todo_dosya, index=False); st.rerun()
    if len(df_todo) > 0:
        st.write("")
        for idx, row in df_todo.iterrows():
            if not row["Tamamlandi"]:
                if st.checkbox(row["Görev"], key=f"aktif_{idx}"):
                    df_todo.at[idx, "Tamamlandi"] = True; df_todo.to_csv(todo_dosya, index=False); st.balloons(); st.rerun()
            else: st.checkbox(f"~~{row['Görev']}~~", value=True, disabled=True, key=f"pasif_{idx}")
        if df_todo["Tamamlandi"].any() and st.button("🧹 Temizle"):
            df_todo = df_todo[df_todo["Tamamlandi"] == False]; df_todo.to_csv(todo_dosya, index=False); st.rerun()
    else: st.info("Listen şu an boş."); st.write("---")

def c_su():
    st.subheader("💧 Su İçmeyi Unutma!")
    su_dosya = "su_takip.csv"; bugun_str = datetime.date.today().strftime("%d.%m.%Y")
    if os.path.exists(su_dosya):
        df_su = pd.read_csv(su_dosya)
        if df_su.iloc[0]["Tarih"] != bugun_str: df_su = pd.DataFrame([{"Tarih": bugun_str, "Bardak": 0}]); df_su.to_csv(su_dosya, index=False)
    else: df_su = pd.DataFrame([{"Tarih": bugun_str, "Bardak": 0}]); df_su.to_csv(su_dosya, index=False)
    mevcut_su = int(df_su.iloc[0]["Bardak"])
    s1, s2 = st.columns([2, 1])
    with s1:
        bardaklar = "💧" * mevcut_su + "🧊" * (8 - mevcut_su) if mevcut_su <= 8 else "💧" * 8 + f" (+{mevcut_su-8})"
        st.markdown(f"<h3 style='margin:0; padding:0; font-size: 24px;'>{bardaklar}</h3>", unsafe_allow_html=True); st.caption(f"Hedef: 8 Bardak | İçilen: {mevcut_su}")
    with s2:
        if st.button("İçtim 🚰", use_container_width=True):
            df_su.at[0, "Bardak"] = mevcut_su + 1; df_su.to_csv(su_dosya, index=False)
            if mevcut_su + 1 == 8: st.success("Hedef tamam!"); st.balloons()
            st.rerun()
    st.write("---")

def c_oduller():
    st.subheader("🎁 Arda'nın Ödül Sistemi")
    max_tyt = 0.0; max_saat = 0.0; kayitli_gun_sayisi = 0
    if os.path.exists("deneme_netleri.csv"):
        tdf = pd.read_csv("deneme_netleri.csv"); tdf = tdf[tdf["Sınav"] == "TYT"]
        if len(tdf) > 0: max_tyt = tdf["Toplam Net"].max()
    if os.path.exists("gunluk_ozet.csv"):
        gdf = pd.read_csv("gunluk_ozet.csv"); kayitli_gun_sayisi = len(gdf)
        if kayitli_gun_sayisi > 0: max_saat = gdf["CalismaSaati"].max()
    with st.expander("Kilitli Başarılar ve Ödülleri Gör 👀"):
        if max_saat >= 8.0: st.success("🔓 **Demir İrade (8 Saat!)** \n\nÖdül: İlk fırsatta favori yemeğin benden!")
        else: st.warning(f"🔒 **Demir İrade:** Bir günde en az 8 saat çalış. (Rekorun: {max_saat}s)")
        if kayitli_gun_sayisi >= 5: st.success("🔓 **İstikrar Zinciri (5 Gün!)** \n\nÖdül: Ufak bir sürpriz hediye seni bekliyor!")
        else: st.info(f"🔒 **İstikrar Zinciri:** Sistemi pes etmeden 5 gün kullan. (Mevcut: {kayitli_gun_sayisi} gün)")
        if max_tyt >= 100.0: st.success("🔓 **Zirve Yürüyüşü (85 Net!)** \n\nÖdül: Birlikte geziyor ve tatlı yiyoruz! 🎉")
        else: st.error(f"🔒 **Zirve Yürüyüşü:** TYT'de 100 nete aş! (Rekorun: {max_tyt} net)")
        ozel_dosya = "ozel_gorevler.csv"
        if os.path.exists(ozel_dosya) and len(pd.read_csv(ozel_dosya)) > 0:
            st.write("---")
            for idx, row in pd.read_csv(ozel_dosya).iterrows(): st.info(f"🎯 **Özel Görev:** {row['Gorev']}\n\n🎁 **Ödül:** {row['Odul']}")

def c_pomodoro():
    sayac_js = """<script>var countDownDate = new Date("Jun 19, 2027 10:15:00").getTime(); setInterval(function() { var now = new Date().getTime(); var distance = countDownDate - now; document.getElementById("clock").innerHTML = Math.floor(distance / (1000 * 60 * 60 * 24)) + " Gün " + Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)) + " Saat " + Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)) + " Dk"; }, 1000);</script>"""
    saniyeli_sayac = f"""<style>body {{ background-color: {bg}; margin: 0; padding: 0; overflow: hidden; }}</style><div style="text-align: center; font-family: 'Arial', sans-serif; padding: 20px; background-color: {card}; border-radius: 10px; border: 2px solid {border}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;"><div id="clock" style="font-size: 24px; font-weight: bold; color: {hdr};">Yükleniyor...</div><p style="color: {txt}; font-size: 14px; margin-top: 10px;">YKS'ye Kalan Süre</p></div>""" + sayac_js
    components.html(saniyeli_sayac, height=130)
    pomodoro_js = """<script>let tl = 25*60; let tid = null; let r = false; const d = document.getElementById('p-time'); function ud() { let m = Math.floor(tl/60); let s = tl%60; d.textContent = (m<10?"0"+m:m)+":"+(s<10?"0"+s:s); } function startT() { if(r)return; r=true; tid=setInterval(()=>{tl--; ud(); if(tl<=0){clearInterval(tid); r=false; alert("Süre bitti!");}},1000); } function pauseT() { clearInterval(tid); r=false; } function resetT() { pauseT(); tl = (parseInt(document.getElementById('c-min').value)||25)*60; ud(); } function setC() { resetT(); } let sws = 0; let swid = null; let swr = false; const swd = document.getElementById('sw-time'); function uswd() { let h = Math.floor(sws/3600); let m = Math.floor((sws%3600)/60); let s = sws%60; swd.textContent = (h<10?"0"+h:h)+":"+(m<10?"0"+m:m)+":"+(s<10?"0"+s:s); } function startS() { if(swr)return; swr=true; swid=setInterval(()=>{sws++; uswd();},1000); } function pauseS() { clearInterval(swid); swr=false; } function resetS() { pauseS(); sws=0; uswd(); }</script>"""
    pomodoro_html = f"""<style>body {{ background-color: {bg}; margin: 0; padding: 0; overflow: hidden; }}</style><div style="font-family: 'Arial', sans-serif; padding: 15px; background-color: {card}; border-radius: 10px; border: 2px solid {border}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;"><h4 style="color: {hdr}; text-align: center; margin-top: 0;">Geri Sayım (Pomodoro)</h4><div style="text-align: center;"><div id="p-time" style="font-size: 36px; font-weight: bold; color: {txt}; margin-bottom: 10px;">25:00</div><button onclick="startT()" style="background-color: {btn}; border: none; padding: 5px 12px; border-radius: 5px; font-weight: bold; color: {btn_txt}; cursor: pointer;">Başlat</button> <button onclick="pauseT()" style="background-color: {btn}; border: none; padding: 5px 12px; border-radius: 5px; font-weight: bold; color: {btn_txt}; cursor: pointer;">Duraklat</button> <button onclick="resetT()" style="background-color: {btn}; border: none; padding: 5px 12px; border-radius: 5px; font-weight: bold; color: {btn_txt}; cursor: pointer;">Sıfırla</button><div style="margin-top: 10px;"><input type="number" id="c-min" value="25" min="1" style="width: 50px; text-align: center; background:{bg}; color:{txt}; border:1px solid {border};"> <button onclick="setC()" style="background: none; border: 1px solid {hdr}; color: {hdr}; border-radius: 5px; font-weight: bold; cursor: pointer;">Ayarla</button></div></div><hr style="border: 0; border-top: 1px solid {border}; margin: 15px 0;"><h4 style="color: {hdr}; text-align: center; margin-top: 0;">⏱ Toplam Çalışma Süresi</h4><div style="text-align: center;"><div id="sw-time" style="font-size: 32px; font-weight: bold; color: {txt}; margin-bottom: 10px;">00:00:00</div><button onclick="startS()" style="background-color: {btn}; border: none; padding: 5px 12px; border-radius: 5px; font-weight: bold; color: {btn_txt}; cursor: pointer;">Başlat</button> <button onclick="pauseS()" style="background-color: {btn}; border: none; padding: 5px 12px; border-radius: 5px; font-weight: bold; color: {btn_txt}; cursor: pointer;">Duraklat</button> <button onclick="resetS()" style="background-color: {btn}; border: none; padding: 5px 12px; border-radius: 5px; font-weight: bold; color: {btn_txt}; cursor: pointer;">Sıfırla</button></div></div>""" + pomodoro_js
    components.html(pomodoro_html, height=420)
    nefes_html = f"""<style>body {{ background-color: {bg}; margin: 0; padding: 0; overflow: hidden; }}</style><div style="text-align: center; padding: 15px; background-color: {card}; border-radius: 10px; border: 2px solid {border}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);"><p style="color: {txt}; font-size: 13px; margin-bottom: 25px; margin-top:0;"><b>Stres anında çemberi izle:</b><br><span style="color:{hdr};">4sn Al - 7sn Tut - 8sn Ver</span></p><div style="position: relative; width: 80px; height: 80px; margin: 0 auto;"><div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 20px; height: 20px; background-color: {btn}; border-radius: 50%; animation: breathe 19s infinite linear;"></div></div></div><style>@keyframes breathe {{ 0% {{ transform: translate(-50%, -50%) scale(1); background-color: {btn}; }} 21% {{ transform: translate(-50%, -50%) scale(3.5); background-color: {btn_hover}; }} 58% {{ transform: translate(-50%, -50%) scale(3.5); background-color: {border}; }} 100% {{ transform: translate(-50%, -50%) scale(1); background-color: {btn}; }} }}</style>"""
    components.html(nefes_html, height=200)

def c_gunluk():
    st.header("🌙 Günü Kapat & İç Dök")
    gunluk_dosya = "gunluk_ozet.csv"
    df_gunluk = pd.read_csv(gunluk_dosya) if os.path.exists(gunluk_dosya) else pd.DataFrame(columns=["Tarih", "CalismaSaati", "GunlukNotu"])
    with st.form("gunu_kapat_formu", clear_on_submit=True):
        bugun = datetime.date.today().strftime("%d.%m.%Y"); st.write(f"**Tarih:** {bugun}")
        calisma_saati = st.number_input("Kaç Saat Çalıştın?", min_value=0.0, max_value=24.0, step=0.5)
        gunluk_not = st.text_area("Gizli Günlüğün:", placeholder="Bugün çok yoruldum ama...")
        if st.form_submit_button("Günü Kaydet ve Uyumaya Git 💤"):
            df_gunluk = pd.concat([df_gunluk, pd.DataFrame([{"Tarih": bugun, "CalismaSaati": calisma_saati, "GunlukNotu": gunluk_not}])], ignore_index=True); df_gunluk.to_csv(gunluk_dosya, index=False)
            st.success("Kaydedildi! Harika bir iş çıkardın. 💖"); st.balloons()

def c_net_takibi():
    st.header("📈 Net Takibi ve Analiz")
    hedef_universite = "Güneş Üniversitesi Tıp fakultesi"; hedef_tyt_net = 105; rekor_net = 0.0
    dosya_adi = "deneme_netleri.csv"
    if os.path.exists(dosya_adi):
        df_netler = pd.read_csv(dosya_adi); tyt = df_netler[df_netler["Sınav"] == "TYT"]
        if len(tyt) > 0: rekor_net = tyt["Toplam Net"].max()
    else: df_netler = pd.DataFrame(columns=["Deneme Adı", "Sınav", "Türkçe/Edebiyat", "Matematik", "Sosyal", "Fen", "Toplam Net"])
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
            df_netler = pd.concat([df_netler, pd.DataFrame([{"Deneme Adı": deneme_adi, "Sınav": sinav_turu, "Türkçe/Edebiyat": turkce, "Matematik": mat, "Sosyal": sosyal, "Fen": fen, "Toplam Net": turkce+mat+sosyal+fen}])], ignore_index=True); df_netler.to_csv(dosya_adi, index=False); st.success(f"Eklendi!"); st.rerun()

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

def c_kumbara():
    st.divider(); st.subheader("🎯 Eksik Avcısı (Kumbara)")
    kumbara_dosya = "soru_kumbara.csv"
    df_kumbara = pd.read_csv(kumbara_dosya) if os.path.exists(kumbara_dosya) else pd.DataFrame(columns=["Eksik", "Durum"])
    with st.form("kumbara_form", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        with c1: yeni = st.text_input("Eksik konu/soru:", placeholder="Örn: Ses Bilgisi", label_visibility="collapsed")
        with c2: 
            if st.form_submit_button("Kumbaraya At") and yeni.strip():
                df_kumbara = pd.concat([df_kumbara, pd.DataFrame([{"Eksik": yeni.strip(), "Durum": False}])], ignore_index=True); df_kumbara.to_csv(kumbara_dosya, index=False); st.rerun()
    if len(df_kumbara) > 0:
        for idx, row in df_kumbara.iterrows():
            if not row["Durum"]:
                if st.checkbox(row["Eksik"], key=f"eksik_{idx}"): df_kumbara.at[idx, "Durum"] = True; df_kumbara.to_csv(kumbara_dosya, index=False); st.balloons(); st.rerun()
            else: st.checkbox(f"~~{row['Eksik']}~~ ✅", value=True, disabled=True, key=f"coz_{idx}")
        if df_kumbara["Durum"].any() and st.button("🧹 Halledilenleri Temizle"): df_kumbara = df_kumbara[df_kumbara["Durum"] == False]; df_kumbara.to_csv(kumbara_dosya, index=False); st.rerun()

def c_muzik():
    st.header("🎧 Ders Çalışma Ortamı")
    components.html(f"""<style>body {{ background-color: {bg}; margin: 0; padding: 0; overflow: hidden; }}</style><iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/0zHr4z4SfUeKZOXv3rxVIV?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>""", height=360)
    st.divider(); st.subheader("Hızlı Kısayollar 📌")
    st.markdown(f"""<style>.kkart {{ background-color: {card}; border: 2px solid {border}; border-radius: 12px; padding: 15px 10px; text-align: center; color: {hdr}; font-weight: bold; width: 140px; transition: 0.3s; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; text-decoration: none;}} .kkart:hover {{ background-color: {btn_hover}; color: {txt}; transform: translateY(-5px); border-color: {hdr}; }}</style><div style="display: flex; gap: 15px; flex-wrap: wrap; margin-top: 15px;">
        <a href="https://ais.osym.gov.tr/" target="_blank" style="text-decoration:none;"><div class="kkart"><span style="font-size: 28px;">📚</span><span>ÖSYM AİS</span></div></a>
        <a href="https://yokatlas.yok.gov.tr/" target="_blank" style="text-decoration:none;"><div class="kkart"><span style="font-size: 28px;">🗺️</span><span>YÖK Atlas</span></div></a>
        <a href="https://www.youtube.com/c/BenimHocam" target="_blank" style="text-decoration:none;"><div class="kkart"><span style="font-size: 28px;">▶️</span><span>Benim Hocam</span></div></a>
        <a href="https://www.youtube.com/c/MertHoca" target="_blank" style="text-decoration:none;"><div class="kkart"><span style="font-size: 28px;">📐</span><span>Mert Hoca</span></div></a></div>""", unsafe_allow_html=True)

def c_panel():
    st.header("⚙️ Arda'nın Gizli Paneli")
    sifre = st.text_input("Şifre:", type="password")
    if sifre == "1905":
        st.success("Giriş Başarılı!")
        ozel_dosya = "ozel_gorevler.csv"; df_ozel = pd.read_csv(ozel_dosya) if os.path.exists(ozel_dosya) else pd.DataFrame(columns=["Gorev", "Odul"])
        with st.form("ozel_form", clear_on_submit=True):
            yg = st.text_input("Yeni Görev:"); yo = st.text_input("Ödül:")
            if st.form_submit_button("Gönder") and yg and yo: df_ozel = pd.concat([df_ozel, pd.DataFrame([{"Gorev": yg, "Odul": yo}])], ignore_index=True); df_ozel.to_csv(ozel_dosya, index=False); st.rerun()
        if len(df_ozel) > 0:
            for idx, row in df_ozel.iterrows():
                st.info(f"**Görev:** {row['Gorev']} \n**Ödül:** {row['Odul']}")
                if st.button("🗑️ Sil", key=f"sil_{idx}"): df_ozel = df_ozel.drop(idx); df_ozel.to_csv(ozel_dosya, index=False); st.rerun()
    elif sifre: st.error("İzinsiz giriş!")

# --- BAĞIMSIZ YAPAY ZEKA ASİSTANI (Akıllı Kota Korumalı) ---
def c_yapay_zeka():
    st.header("🤖 YKS Motivasyon & Çalışma Asistanı")
    st.write("Sınav süreciyle ilgili takıldığın soruları sorabilir, çalışma taktikleri alabilirsin.")
    
    soru = st.text_input("Bugün hangi konuda yardıma ihtiyacın var?", placeholder="Örn: Paragraf netlerimi nasıl artırabilirim?")
    
    if st.button("✨ Asistana Sor", use_container_width=True):
        if soru.strip():
            cevap = None
            try:
                with st.spinner('Asistan yanıt hazırlıyor...'):
                    model = genai.GenerativeModel('gemini-3.8-flash')
                    prompt = f"Sen YKS hazırlanan bir öğrenciye destek olan profesyonel bir rehberlik asistanısın. Öğrenci sana şunu sordu: '{soru}'. Ona çok kibar, motive edici, eğitici ve net çalışma taktikleri veren kısa bir cevap ver. (Maksimum 3 cümle)."
                    response = model.generate_content(prompt)
                    cevap = response.text
            except Exception as e:
                yedek_sozler = [
                    "Bugün pes etmek yok, her çözülen soru seni hedefine bir adım daha yaklaştırır!",
                    "Küçük adımlar büyük başarılar getirir. Planlı çalışmaya devam!",
                    "Zorluklar seni durdurmasın, aksine daha çok hırslandırsın. Harika gidiyorsun!",
                    "Bugünkü çalışmaların gelecekteki özgürlüğünün teminatıdır. Kolay gelsin!"
                ]
                cevap = random.choice(yedek_sozler)
            
            st.info(f"💡 **Rehber Notu:** {cevap}")
        else:
            st.warning("Önce bir soru yazmalısın...")

# --- EĞLENCE & MOLA MERKEZİ ---
def c_eglence():
    st.header("🕹️ Eğlence & Mola Merkezi")
    st.write("Sınav senesinde beyni dinlendirmek de çalışmak kadar önemlidir. Kafanı dağıt!")
    
    # Gelişmiş Baloncuk Oyunu (Ses Efektli ve Geri Döndürülebilir)
    st.subheader("🫧 Stres Atıcı: Sanal Balon Patlatma")
    bubble_html = f"""
    <style>
        body {{ background-color: {bg}; margin: 0; padding: 0; overflow: hidden; }}
        .bubble {{ 
            width: 35px; height: 35px; background-color: {btn}; border-radius: 50%; 
            margin: 4px; display: inline-block; cursor: pointer; 
            box-shadow: inset -2px -2px 6px rgba(0,0,0,0.2); transition: 0.15s; 
        }}
        .bubble.popped {{ 
            background-color: {bg}; box-shadow: inset 2px 2px 5px rgba(0,0,0,0.1); 
            opacity: 0.3; transform: scale(0.85); 
        }}
    </style>
    <div id="bw" style="max-width: 320px; margin: 0 auto; text-align: center; padding: 15px; background-color: {card}; border-radius: 15px; border: 2px solid {border};"></div>
    <script>
        // Web Audio API ile hafif "pop" sesi üretici
        function playPopSound() {{
            try {{
                let audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                let osc = audioCtx.createOscillator();
                let gainNode = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(400, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(80, audioCtx.currentTime + 0.08);
                gainNode.gain.setValueAtTime(0.15, audioCtx.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
                osc.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.08);
            }} catch(e) {{}}
        }}

        const bw = document.getElementById('bw');
        for(let i=0; i<30; i++) {{
            let b = document.createElement('div');
            b.className = 'bubble';
            b.onclick = function() {{
                if(!this.classList.contains('popped')) {{
                    this.classList.add('popped');
                    playPopSound(); // Patlama sesi
                }} else {{
                    this.classList.remove('popped'); // Tekrar basınca eski haline döner
                }}
            }};
            bw.appendChild(b);
        }}
    </script>
    """
    components.html(bubble_html, height=260)
    
    st.divider()

    st.subheader("❌ Strateji & Zeka Oyunu (XOX)")
    if 'xox_board' not in st.session_state: st.session_state.xox_board = [''] * 9; st.session_state.xox_winner = None
    def check_winner(b):
        win_cond = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for x, y, z in win_cond:
            if b[x] == b[y] == b[z] != '': return b[x]
        if '' not in b: return 'Berabere'
        return None
    def handle_xox(idx):
        if st.session_state.xox_board[idx] == '' and st.session_state.xox_winner is None:
            st.session_state.xox_board[idx] = '❌'
            st.session_state.xox_winner = check_winner(st.session_state.xox_board)
            if st.session_state.xox_winner is None:
                empty = [i for i, v in enumerate(st.session_state.xox_board) if v == '']
                if empty:
                    st.session_state.xox_board[random.choice(empty)] = '⭕'
                    st.session_state.xox_winner = check_winner(st.session_state.xox_board)

    st.markdown("""<style>div[data-testid="column"] button {height: 80px; font-size: 32px !important;}</style>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for i in range(9):
        col = c1 if i%3 == 0 else c2 if i%3 == 1 else c3
        with col:
            etiket = st.session_state.xox_board[i] if st.session_state.xox_board[i] != '' else " "
            st.button(etiket, key=f"xox_{i}", on_click=handle_xox, args=(i,), use_container_width=True)
            
    if st.session_state.xox_winner:
        if st.session_state.xox_winner == '❌': st.success("🎉 Tebrikler! Oyunu kazandın!"); st.balloons()
        elif st.session_state.xox_winner == '⭕': st.info("Rakip kazandı! Bir dahaki sefere.")
        else: st.info("Berabere!")
        if st.button("🔄 Oyunu Sıfırla"): st.session_state.xox_board = [''] * 9; st.session_state.xox_winner = None; st.rerun()

    st.divider()
    st.subheader("🏖️ Sınav Sonrası Hedefler & Hayaller")
    hayal_dosya = "hayal_kumbarasi.csv"
    if not os.path.exists(hayal_dosya):
        df_hayal = pd.DataFrame([{"Hayal": "Sınav çıkışı uzun bir tatil yapmak 🌴"}, {"Hayal": "Favori dizilerin yeni sezonlarını izlemek 🍿"}, {"Hayal": "Bütün gün kesintisiz uyumak 😴"}, {"Hayal": "Güzel bir kutlama yemeğine gitmek 🍽️"}])
        df_hayal.to_csv(hayal_dosya, index=False)
    else: df_hayal = pd.read_csv(hayal_dosya)
        
    with st.form("hayal_form", clear_on_submit=True):
        c_h1, c_h2 = st.columns([3, 1])
        with c_h1: y_hayal = st.text_input("Yeni Hayal Ekle:", placeholder="Örn: Üniversite kampüs gezisi...", label_visibility="collapsed")
        with c_h2: 
            if st.form_submit_button("Ekle 💭") and y_hayal.strip(): df_hayal = pd.concat([df_hayal, pd.DataFrame([{"Hayal": y_hayal.strip()}])], ignore_index=True); df_hayal.to_csv(hayal_dosya, index=False); st.rerun()
                
    for idx, row in df_hayal.iterrows():
        c_i1, c_i2 = st.columns([8, 1])
        with c_i1: st.info(f"🌟 {row['Hayal']}")
        with c_i2:
            if st.button("🗑️", key=f"del_h_{idx}"): df_hayal = df_hayal.drop(idx); df_hayal.to_csv(hayal_dosya, index=False); st.rerun()

# =========================================================
# ARAYÜZ YÖNETİCİSİ (AİLE KONTROLÜNE UYGUN GİZLİ ALARM SİSTEMİ)
# =========================================================

if st.session_state['arayuz'] == 'sekmeler':
    t1, t2, t3, t4, t5, t6 = st.tabs(["🏠 Ana Sayfa", "📈 Net & Eksikler", "🤖 Asistan", "🕹️ Eğlence", "🎧 Müzik", "⚙️ Panel"])
    with t1:
        s1, s2 = st.columns(2)
        with s1: c_karsilama(); c_todo(); c_su(); c_oduller()
        with s2: c_pomodoro(); c_gunluk()
    with t2: c_net_takibi(); c_kumbara()
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
        c_geri, _ = st.columns([1, 4])
        with c_geri:
            if st.button("⬅️ Ana Ekrana Dön"): st.session_state['aktif_uygulama'] = None; st.rerun()
        aktif = st.session_state['aktif_uygulama']
        if aktif == 'masa': c_pomodoro()
        elif aktif == 'todo': c_todo(); c_kumbara()
        elif aktif == 'gunluk': c_su(); c_gunluk()
        elif aktif == 'net': c_net_takibi()
        elif aktif == 'odul': c_oduller()
        elif aktif == 'ai': c_yapay_zeka()
        elif aktif == 'eglence': c_eglence()
        elif aktif == 'muzik': c_muzik()
        elif aktif == 'panel': c_panel()

# --- AİLE DOSTU / GİZLİ MOTİVASYON BİLDİRİM SİSTEMİ ---
# Sayfa her yenilendiğinde arkada rastgele zamanlı/içerikli motive edici bildirim kutusu tetiklenir.
if random.random() < 0.35: # %35 ihtimalle ekranda belirir
    gizli_bildirimler = [
        "⏰ **Çalışma Hatırlatıcı:** Günlük soru hedefine ulaşmak için harika bir zaman!",
        "💡 **Günün Tavsiyesi:** Kısa bir mola verdikten sonra masaya dinamik bir dönüş yapabilirsin.",
        "📚 **Rehber Notu:** Bugün paragraf çözmeyi ihmal etme!",
        "🎯 **Hedef Kontrolü:** Eksik konularını kapatmak için iyi bir fırsat."
        "🌟 **Günlük Ödüllü:** Bugün başarıya ulaşmak için harika bir gün!"
        "📝 **Motivasyon:** Küçük adımlar büyük başarılar getirir, devam et!"
        "✅ **Başarı Hatırlatıcı:** Bugün ilerleme kaydettin, harika iş!"
        "💪 **Enerji Desteği:** Biraz su iç, derin bir nefes al ve tekrar odaklan!"
        "🎵 **Müzik Önerisi:** Odaklanmanı artıracak bir çalma listesi açabilirsin."
        "🧘 **Rahatlama:** 5 dakika meditasyon yaparak zihnini temizle."
        "📈 **İlerleme Takibi:** Günlük hedeflerini gözden geçir ve kendini ödüllendir."
        "🕹️ **Mola Zamanı:** Kısa bir oyun oyna ve zihnini tazele."
        "🎁 **Sürpriz Ödül:** Bugün kendine küçük bir ödül ver, bunu hak ettin!"
    ]
    st.toast(random.choice(gizli_bildirimler), icon="🔔")