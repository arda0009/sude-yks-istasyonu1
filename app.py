import streamlit as st
import pandas as pd
import datetime
import random
import gspread

# ----------------- SAYFA AYARLARI -----------------
st.set_page_config(page_title="Sude YKS İstasyonu", page_icon="💖", layout="wide")

# ----------------- GOOGLE DRIVE BAĞLANTISI -----------------
@st.cache_resource
def get_gspread_client():
    try:
        # Doğrudan Streamlit formatını kullanıyoruz (JSON hatalarını çöpe attık)
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            return gspread.service_account_from_dict(creds_dict)
        else:
            st.error("🚨 HATA: Secrets içinde 'gcp_service_account' bulunamadı!")
            return None
    except Exception as e:
        st.error(f"🚨 Bağlantı Hatası: {e}")
        return None

def load_df(filename, ws_name, default_dict):
    gc = get_gspread_client()
    if gc:
        try:
            sh = gc.open("Sude_Veriler")
            try:
                ws = sh.worksheet(ws_name)
            except:
                ws = sh.add_worksheet(title=ws_name, rows="1000", cols="20")
            
            data = ws.get_all_records()
            if data:
                return pd.DataFrame(data)
        except Exception as e:
            st.error(f"🚨 Okuma Hatası ({ws_name}): {e}")
            
    # Hata olursa veya tablo boşsa varsayılanı döndür
    return pd.DataFrame(default_dict)

def save_df(df, filename, ws_name):
    df.to_csv(filename, index=False) # Lokale de yedek kaydet
    gc = get_gspread_client()
    if gc:
        try:
            sh = gc.open("Sude_Veriler")
            try:
                ws = sh.worksheet(ws_name)
            except:
                ws = sh.add_worksheet(title=ws_name, rows="1000", cols="20")
            
            # KRİTİK NOKTA: Google hata vermesin diye tüm verileri zorla String (Metin) yapıyoruz
            df_cloud = df.copy().astype(str)
            df_cloud.replace("nan", "", inplace=True)
            
            veri_listesi = [df_cloud.columns.tolist()] + df_cloud.values.tolist()
            ws.clear()
            ws.update(values=veri_listesi) 
            st.toast(f"✅ {ws_name} buluta başarıyla yazıldı!") 
        except Exception as e:
            st.error(f"🚨 Yazma Hatası: {e}")
    else:
        st.error("🚨 Bağlantı Hatası: Sunucu Google'a bağlanamadı.")

# ----------------- MODÜLLER (FONKSİYONLAR) -----------------

def c_karsilama():
    st.header(f"Merhaba Sude! 💖")
    st.write("Bugün hayallerine bir adım daha yaklaşmak için harika bir gün. Sen harikasın, unutma!")
    st.divider()

def c_su():
    st.subheader("💧 Su İçmeyi Unutma!")
    bugun_str = datetime.date.today().strftime("%d.%m.%Y")
    df_su = load_df("su_takip.csv", "Su", {"Tarih": [bugun_str], "Bardak": [0]})
    
    if df_su.empty or df_su.iloc[-1]["Tarih"] != bugun_str: 
        df_su = pd.DataFrame([{"Tarih": bugun_str, "Bardak": 0}])
        save_df(df_su, "su_takip.csv", "Su")
        
    mevcut_su = int(df_su.iloc[-1]["Bardak"])
    s1, s2 = st.columns([2, 1])
    
    with s1:
        bardaklar = "💧" * mevcut_su + "🧊" * (8 - mevcut_su) if mevcut_su <= 8 else "💧" * 8 + f" (+{mevcut_su-8})"
        st.markdown(f"<h3 style='margin:0; padding:0; font-size: 24px;'>{bardaklar}</h3>", unsafe_allow_html=True)
        st.caption(f"Hedef: 8 Bardak | İçilen: {mevcut_su}")
        
    with s2:
        if st.button("İçtim 🚰", use_container_width=True):
            df_su.at[df_su.index[-1], "Bardak"] = mevcut_su + 1
            save_df(df_su, "su_takip.csv", "Su")
            if mevcut_su + 1 == 8: 
                st.success("Su hedefini tamamladın!")
                st.balloons()
            st.rerun()

def c_todo():
    st.subheader("📝 Günlük Görevler")
    df_todo = load_df("todo_listesi.csv", "Todo", {"Gorev": [], "Durum": []})
    
    yeni_gorev = st.text_input("Yeni Görev Ekle:", key="yeni_gorev")
    if st.button("Ekle ➕") and yeni_gorev:
        yeni_kayit = pd.DataFrame([{"Gorev": yeni_gorev, "Durum": "Bekliyor"}])
        df_todo = pd.concat([df_todo, yeni_kayit], ignore_index=True)
        save_df(df_todo, "todo_listesi.csv", "Todo")
        st.rerun()

    if not df_todo.empty:
        for i, row in df_todo.iterrows():
            col1, col2 = st.columns([4, 1])
            is_done = True if row["Durum"] == "Bitti" else False
            with col1:
                checked = st.checkbox(row["Gorev"], value=is_done, key=f"todo_{i}")
                if checked != is_done:
                    df_todo.at[i, "Durum"] = "Bitti" if checked else "Bekliyor"
                    save_df(df_todo, "todo_listesi.csv", "Todo")
                    st.rerun()
            with col2:
                if st.button("Sil 🗑️", key=f"del_todo_{i}"):
                    df_todo = df_todo.drop(i).reset_index(drop=True)
                    save_df(df_todo, "todo_listesi.csv", "Todo")
                    st.rerun()

def c_gun_sonu():
    st.divider()
    st.subheader("🌙 Gün Sonu Değerlendirmesi")
    bugun_str = datetime.date.today().strftime("%d.%m.%Y")
    
    col1, col2 = st.columns(2)
    with col1:
        baslama = st.time_input("🌅 Derse Başlama Saati", value=datetime.time(9, 0))
    with col2:
        bitis = st.time_input("🌃 Dersi Bırakma Saati", value=datetime.time(18, 0))
        
    kac_saat = st.number_input("Bugün Toplam Kaç Saat Çalıştın?", min_value=0.0, max_value=24.0, step=0.5)
    gunluk = st.text_area("Gizli Günlüğün (Bugün nasıl hissettin?):")
    
    if st.button("Günü Kaydet ve Uyumaya Git 💤", use_container_width=True):
        df_gunluk = load_df("gunluk_ozet.csv", "Gunluk_Ozet", {"Tarih": [], "Baslama": [], "Bitis": [], "Saat": [], "Gunluk": []})
        yeni_kayit = pd.DataFrame([{
            "Tarih": bugun_str, 
            "Baslama": baslama.strftime("%H:%M"), 
            "Bitis": bitis.strftime("%H:%M"), 
            "Saat": kac_saat, 
            "Gunluk": gunluk
        }])
        df_gunluk = pd.concat([df_gunluk, yeni_kayit], ignore_index=True)
        save_df(df_gunluk, "gunluk_ozet.csv", "Gunluk_Ozet")
        st.success("Harika bir iş çıkardın! Tüm bilgilerin buluta otomatik kaydedildi. İyi uykular! 💖")
        st.balloons()

def c_konu_ilerleme():
    st.subheader("📚 Konu İlerleme Durumu")
    df_konu = load_df("konu_ilerleme.csv", "Konular", {"Ders": [], "Konu": [], "Bitti": []})
    
    with st.expander("Yeni Konu Ekle"):
        ders = st.selectbox("Ders:", ["Türkçe", "Matematik", "Geometri", "Tarih", "Coğrafya", "Fizik", "Kimya", "Biyoloji"])
        konu = st.text_input("Konu Adı:")
        if st.button("Konu Ekle"):
            if konu:
                yeni_kayit = pd.DataFrame([{"Ders": ders, "Konu": konu, "Bitti": "False"}])
                df_konu = pd.concat([df_konu, yeni_kayit], ignore_index=True)
                save_df(df_konu, "konu_ilerleme.csv", "Konular")
                st.rerun()

    if not df_konu.empty:
        # STRING ÇÖZÜMÜ BURADA:
        toplam = len(df_konu)
        biten = int(df_konu["Bitti"].astype(str).str.lower().isin(["true", "1", "1.0", "yes", "evet"]).sum()) if "Bitti" in df_konu.columns else 0
        
        st.progress(biten / toplam if toplam > 0 else 0)
        st.caption(f"Toplam {toplam} konunun {biten} tanesi bitti! Yola devam! 🚀")
        
        for i, row in df_konu.iterrows():
            col1, col2 = st.columns([5, 1])
            is_checked = str(row["Bitti"]).lower() in ["true", "1", "yes", "evet"]
            with col1:
                checked = st.checkbox(f"**{row['Ders']}**: {row['Konu']}", value=is_checked, key=f"konu_{i}")
                if checked != is_checked:
                    df_konu.at[i, "Bitti"] = str(checked)
                    save_df(df_konu, "konu_ilerleme.csv", "Konular")
                    st.rerun()
            with col2:
                if st.button("Sil", key=f"del_konu_{i}"):
                    df_konu = df_konu.drop(i).reset_index(drop=True)
                    save_df(df_konu, "konu_ilerleme.csv", "Konular")
                    st.rerun()

def c_net_takibi():
    st.subheader("📈 Deneme Netleri")
    df_net = load_df("deneme_netleri.csv", "Netler", {"Tarih": [], "Deneme Adı": [], "TYT Net": []})
    
    with st.form("net_ekle", clear_on_submit=True):
        col1, col2 = st.columns(2)
        deneme_adi = col1.text_input("Deneme Yayını/Adı:")
        net = col2.number_input("TYT Netin:", min_value=0.0, max_value=120.0, step=0.25)
        if st.form_submit_button("Neti Kaydet"):
            yeni_kayit = pd.DataFrame([{"Tarih": datetime.date.today().strftime("%d.%m.%Y"), "Deneme Adı": deneme_adi, "TYT Net": net}])
            df_net = pd.concat([df_net, yeni_kayit], ignore_index=True)
            save_df(df_net, "deneme_netleri.csv", "Netler")
            st.success("Net eklendi!")
            st.rerun()
            
    if not df_net.empty:
        df_grafik = df_net.copy()
        df_grafik["TYT Net"] = pd.to_numeric(df_grafik["TYT Net"], errors='coerce').fillna(0)
        st.line_chart(df_grafik.set_index("Deneme Adı")["TYT Net"])
        st.dataframe(df_net)

def c_hayal_kumbarasi():
    st.subheader("☁️ Sınav Sonrası Hayal Kumbarası")
    st.caption("YKS bittiğinde, üniversiteye geçtiğinde veya hemen yarın... Gerçekleştirmek istediğin her şeyi buraya at!")
    df_hayal = load_df("hayal_kumbarasi.csv", "Hayaller", {"Tarih": [], "Hayal": []})
    
    with st.form("hayal_form", clear_on_submit=True):
        yeni_hayal = st.text_input("Ne yapmak istiyorsun?")
        ekle = st.form_submit_button("Kumbaraya At 🌟")
        if ekle and yeni_hayal:
            yeni_kayit = pd.DataFrame([{"Tarih": datetime.date.today().strftime("%d.%m.%Y"), "Hayal": yeni_hayal}])
            df_hayal = pd.concat([df_hayal, yeni_kayit], ignore_index=True)
            save_df(df_hayal, "hayal_kumbarasi.csv", "Hayaller")
            st.success("Hayalin kumbaraya eklendi!")
            st.rerun()
            
    st.divider()
    if not df_hayal.empty:
        for index, row in df_hayal.iloc[::-1].iterrows(): 
            st.info(f"✨ {row['Hayal']}")

def c_eglence_ve_meditasyon():
    st.header("🎮 Mola & Meditasyon Merkezi")
    tab1, tab2, tab3, tab4 = st.tabs(["❌⭕ XOX Oyunu", "🫧 Sanal Baloncuk", "🧘‍♀️ Renk Terapisi", "🎯 Sayı Tahmini"])
    
    with tab1:
        st.subheader("Klasik XOX")
        if 'xox_board' not in st.session_state:
            st.session_state.xox_board = [""] * 9
            st.session_state.xox_turn = "X"
            
        col1, col2, col3 = st.columns([1,1,1])
        for i in range(9):
            with [col1, col2, col3][i % 3]:
                if st.button(st.session_state.xox_board[i] if st.session_state.xox_board[i] else "⬜", key=f"xox_{i}", use_container_width=True):
                    if st.session_state.xox_board[i] == "":
                        st.session_state.xox_board[i] = st.session_state.xox_turn
                        st.session_state.xox_turn = "O" if st.session_state.xox_turn == "X" else "X"
                        st.rerun()
        if st.button("Sıfırla 🔄"):
            st.session_state.xox_board = [""] * 9
            st.session_state.xox_turn = "X"
            st.rerun()

    with tab2:
        st.subheader("🫧 Sınırsız Baloncuk Patlat")
        cols = st.columns(6)
        for i in range(30):
            with cols[i % 6]:
                st.checkbox("Pop!", key=f"bubble_{i}")
                
    with tab3:
        st.subheader("🧘‍♀️ Zihinsel Molan")
        if st.button("Bana Bir Renk ve Motivasyon Ver 🎨"):
            renkler = ["#A2D2FF", "#BDE0FE", "#FFAFCC", "#FFC8DD", "#CDB4DB", "#8ECAE6", "#219EBC", "#84A59D"]
            sozler = [
                "Sen sandığından çok daha güçlüsün.",
                "Şu an elinden gelenin en iyisini yapıyorsun, bu kadarı yeterli.",
                "Bugün çözdüğün her zor soru, seni hedefine yaklaştırdı.",
                "Zorlanman pes etmen gerektiği anlamına gelmez, geliştiğin anlamına gelir."
            ]
            st.markdown(f"""
            <div style="background-color: {random.choice(renkler)}; padding: 50px; border-radius: 20px; text-align: center; color: #333;">
                <h3 style="margin:0;">{random.choice(sozler)}</h3>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.subheader("🎯 Aklımdaki Sayıyı Bul")
        if 'gizli_sayi' not in st.session_state:
            st.session_state.gizli_sayi = random.randint(1, 50)
            
        tahmin = st.number_input("1 ile 50 arasında bir sayı tuttum. Sence kaç?", min_value=1, max_value=50)
        if st.button("Tahmin Et"):
            if tahmin < st.session_state.gizli_sayi:
                st.warning("Yukarı! ⬆️")
            elif tahmin > st.session_state.gizli_sayi:
                st.warning("Aşağı! ⬇️")
            else:
                st.success("Tebrikler! 🎉 Doğru bildin!")
                st.balloons()
                st.session_state.gizli_sayi = random.randint(1, 50)

def c_muzik():
    st.subheader("🎧 Odaklanma Müzikleri")
    st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk") # Lofi Girl

def c_panel_grafikler():
    st.header("📊 Yönetici Paneli: Sude'nin Performans Analizi")
    sifre = st.text_input("Yönetici Şifresi (Arda):", type="password")
    
    if sifre == "arda123": # Kendi şifreni buraya yazabilirsin
        df_gunluk = load_df("gunluk_ozet.csv", "Gunluk_Ozet", {"Tarih": [], "Baslama": [], "Bitis": [], "Saat": [], "Gunluk": []})
        if not df_gunluk.empty:
            df_grafik = df_gunluk.copy()
            df_grafik["Saat"] = pd.to_numeric(df_grafik["Saat"], errors='coerce').fillna(0)
            
            s1, s2 = st.columns(2)
            with s1:
                st.subheader("📈 Günlük Çalışma Süreleri")
                st.bar_chart(data=df_grafik.set_index("Tarih")["Saat"], color="#ff4b4b")
            with s2:
                st.subheader("⏰ Başlama ve Bitiş Raporu")
                st.dataframe(df_grafik[["Tarih", "Baslama", "Bitis", "Saat"]], use_container_width=True)
                
            st.subheader("📓 Sude'nin Gizli Günlüğü")
            st.dataframe(df_grafik[["Tarih", "Gunluk"]], use_container_width=True)
        else:
            st.info("Henüz grafik oluşturacak gün sonu verisi girilmemiş.")

# ----------------- ANA GÖVDE VE SEKMELER -----------------

st.title("💖 Sude YKS İstasyonu 💖")
st.caption("Geleceğine giden yolda en güzel durak...")

t1, t2, t3, t4, t5, t6 = st.tabs(["🏠 Ana Sayfa", "📈 Net & Eksikler", "🤖 Asistan", "🎮 Eğlence", "🎧 Müzik", "⚙️ Panel"])

with t1:
    c_karsilama()
    c_su()
    c_todo()
    c_gun_sonu()
    
with t2:
    c_net_takibi()
    c_konu_ilerleme()
    
with t3:
    c_hayal_kumbarasi()

with t4:
    c_eglence_ve_meditasyon()
    
with t5:
    c_muzik()
    
with t6:
    c_panel_grafikler()
