import joblib
import pandas as pd
import shap
import streamlit as st

st.set_page_config(page_title="Öğrenci Başarı Erken Uyarı Sistemi", page_icon="🎓", layout="wide")

# ====================== GÖRÜNÜM (CSS) ======================
st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 1.5rem; max-width: 1250px;}
.banner {background: linear-gradient(120deg, #12395F 0%, #1F6FB2 100%); color: #fff;
         padding: 26px 32px; border-radius: 14px; margin-bottom: 18px;}
.banner .b1 {font-size: 13px; letter-spacing: 2px; text-transform: uppercase; opacity: .85;}
.banner .b2 {font-size: 30px; font-weight: 700; margin: 4px 0;}
.banner .b3 {font-size: 15px; opacity: .92;}
.kpi {background: #fff; padding: 14px 18px; border-radius: 10px; box-shadow: 0 1px 5px rgba(20,40,70,.12);}
.kpi .kb {font-size: 13px; color: #5B6B7B; font-weight: 600;}
.kpi .kd {font-size: 30px; font-weight: 700; color: #12395F; line-height: 1.2;}
.kpi .ka {font-size: 12px; color: #7B8A99;}
.kutu {background: #fff; padding: 16px 20px; border-radius: 10px; box-shadow: 0 1px 5px rgba(20,40,70,.10);}
.etiket {display: inline-block; padding: 3px 10px; border-radius: 12px; background: #E8F0F8;
         color: #12395F; font-size: 13px; margin: 2px 4px 2px 0;}
</style>
""", unsafe_allow_html=True)

# Özet kartı çizen küçük yardımcı fonksiyon
def kpi(baslik, deger, alt="", renk="#1F4E79"):
    st.markdown(f'<div class="kpi" style="border-left:6px solid {renk}"><div class="kb">{baslik}</div>'
                f'<div class="kd">{deger}</div><div class="ka">{alt}</div></div>', unsafe_allow_html=True)

# ====================== MODEL VE SABİTLER ======================
@st.cache_resource
def modeli_yukle():
    paket = joblib.load("model.joblib")
    return paket["model"], paket["sutunlar"]

model, sutunlar = modeli_yukle()

KATEGORIK = ["Marital status", "Application mode", "Course", "Previous qualification",
             "Mother's qualification", "Father's qualification",
             "Mother's occupation", "Father's occupation"]

BOLUMLER = {33: "Biyoyakıt Üretim Teknolojileri", 171: "Animasyon ve Multimedya Tasarımı", 8014: "Sosyal Hizmet (akşam)",
            9003: "Ziraat Mühendisliği", 9070: "İletişim Tasarımı",
            9085: "Veteriner Hemşireliği", 9119: "Bilişim Mühendisliği",
            9130: "At Yetiştiriciliği", 9147: "İşletme", 9238: "Sosyal Hizmet",
            9254: "Turizm", 9500: "Hemşirelik", 9556: "Ağız ve Diş Sağlığı",
            9670: "Reklamcılık ve Pazarlama", 9773: "Gazetecilik ve İletişim",
            9853: "Temel Eğitim", 9991: "İşletme (akşam)"}

SUTUN_TR = {"Marital status": "Medeni durum (kod)", "Application mode": "Başvuru türü (kod)",
            "Application order": "Tercih sırası", "Course": "Bölüm",
            "Daytime/evening attendance": "Gündüz/akşam eğitimi",
            "Previous qualification": "Önceki eğitim türü (kod)",
            "Previous qualification (grade)": "Önceki eğitim notu",
            "Mother's qualification": "Anne eğitimi (kod)", "Father's qualification": "Baba eğitimi (kod)",
            "Mother's occupation": "Anne mesleği (kod)", "Father's occupation": "Baba mesleği (kod)",
            "Admission grade": "Giriş notu", "Displaced": "Yerinden edilmiş",
            "Debtor": "Borç durumu", "Tuition fees up to date": "Harç durumu",
            "Gender": "Cinsiyet", "Scholarship holder": "Burs durumu",
            "Age at enrollment": "Kayıt yaşı"}

# Risk faktörüne göre önerilen destek adımı (kural tabanlı, karar değil)
ONERI = {"Tuition fees up to date": "Mali işlerle harç yapılandırma / mali destek görüşmesi",
         "Debtor": "Mali işlerle borç yapılandırma görüşmesi",
         "Scholarship holder": "Burs ve destek programları hakkında bilgilendirme",
         "Age at enrollment": "Çalışan/yetişkin öğrenciler için esnek program ve danışmanlık",
         "Admission grade": "Akademik hazırlık programı, mentörlük ve ders desteği",
         "Previous qualification (grade)": "Akademik hazırlık programı ve ders desteği",
         "Course": "Bölüm danışmanıyla erken dönem görüşmesi",
         "Application mode": "Oryantasyon ve uyum programına yönlendirme",
         "Application order": "Bölüm tercihi/uyum görüşmesi (kariyer danışmanlığı)",
         "Displaced": "Barınma ve uyum destek birimine yönlendirme",
         "Daytime/evening attendance": "Akşam programı öğrencileri için esnek ders ve danışmanlık"}

def neden_metni(sutun, deger):
    if float(deger).is_integer():
        deger = int(deger)
    if sutun == "Scholarship holder":         return "Burslu değil" if deger == 0 else "Burslu"
    if sutun == "Tuition fees up to date":    return "Harcı ödenmemiş" if deger == 0 else "Harcı ödenmiş"
    if sutun == "Debtor":                     return "Borçlu" if deger == 1 else "Borcu yok"
    if sutun == "Gender":                     return "Erkek" if deger == 1 else "Kadın"
    if sutun == "Daytime/evening attendance": return "Gündüz eğitimi" if deger == 1 else "Akşam eğitimi"
    if sutun == "Displaced":                  return "Yerinden edilmiş" if deger == 1 else "Yerinden edilmemiş"
    if sutun == "Course":                     return "Bölüm: " + BOLUMLER.get(deger, str(deger))
    return f"{SUTUN_TR.get(sutun, sutun)}: {deger}"

def asil_sutun(ad):
    ad = ad.split("__", 1)[1]
    for k in sorted(KATEGORIK, key=len, reverse=True):
        if ad.startswith(k + "_"):
            return k
    return ad

@st.cache_data
def risk_hesapla(df, top=3):
    X_ogr = df[sutunlar]
    on = model.named_steps["on"]
    gb = model.named_steps["model"]
    Xt = on.transform(X_ogr)
    Xt = Xt.toarray() if hasattr(Xt, "toarray") else Xt
    shap_vals = shap.TreeExplainer(gb).shap_values(Xt)
    eslesme = [asil_sutun(n) for n in on.get_feature_names_out()]
    shap_df = pd.DataFrame(shap_vals).T.groupby(eslesme).sum().T
    risk = model.predict_proba(X_ogr)[:, 1]
    nedenler, anahtarlar = [], []
    for i in range(len(X_ogr)):
        en_buyuk = shap_df.iloc[i].sort_values(ascending=False).head(top)
        en_buyuk = en_buyuk[en_buyuk > 0]
        nedenler.append([neden_metni(s, X_ogr.iloc[i][s]) for s in en_buyuk.index])
        anahtarlar.append(list(en_buyuk.index))
    sonuc = pd.DataFrame({
        "Öğrenci No": df["ogrenci_no"].values,
        "Bölüm": df["Course"].map(lambda k: BOLUMLER.get(int(k), str(int(k)))).values,
        "Risk (%)": (risk * 100).round(1)})
    for k in range(top):
        sonuc[f"Neden {k+1}"] = [n[k] if len(n) > k else "" for n in nedenler]
    shap_df.index = sonuc["Öğrenci No"]
    return sonuc, shap_df, dict(zip(sonuc["Öğrenci No"], anahtarlar))

# ====================== YAN PANEL ======================
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar")
    kurum = st.text_input("Kurum adı", "Örnek Üniversitesi")
    st.markdown("**Veri kaynağı**")
    yuklenen = st.file_uploader("Öğrenci CSV dosyası", type="csv", label_visibility="collapsed")
    ornek_kullan = st.checkbox("Örnek veriyi kullan", value=yuklenen is None)
    st.markdown("**Risk seviyeleri**")
    orta_esik, yuksek_esik = st.slider("Orta ve yüksek risk eşikleri (%)", 30, 95, (50, 75), 5,
        help="Altı: Düşük  |  Aradaki: Orta  |  Üstü: Yüksek")
    st.caption("Şablon CSV'yi 'Model ve Yöntem' sekmesinden indirebilirsiniz.")

st.markdown(f'<div class="banner"><div class="b1">{kurum}</div>'
            '<div class="b2">🎓 Öğrenci Başarı Erken Uyarı Sistemi</div>'
            '<div class="b3">Dönem başı kayıt bilgilerinden, 1. dönemde en az bir dersten kalma riskini '
            'önceden tahmin eder ve destek verilecek öğrencileri önceliklendirir.</div></div>',
            unsafe_allow_html=True)

if yuklenen is not None:
    ogrenciler = pd.read_csv(yuklenen)
elif ornek_kullan:
    ogrenciler = pd.read_csv("ornek_ogrenciler.csv")
else:
    st.info("Soldaki panelden bir CSV dosyası yükleyin veya örnek veriyi seçin.")
    st.stop()

eksik = [c for c in ["ogrenci_no"] + sutunlar if c not in ogrenciler.columns]
if eksik:
    st.error("CSV dosyasında şu sütunlar eksik: " + ", ".join(eksik))
    st.stop()
if ogrenciler["ogrenci_no"].duplicated().any():
    st.error("CSV dosyasında tekrar eden öğrenci numaraları var. Her öğrenci bir kez yer almalı.")
    st.stop()

sonuc, shap_df, anahtarlar = risk_hesapla(ogrenciler)
sonuc["Seviye"] = pd.cut(sonuc["Risk (%)"], [-1, orta_esik - 1e-9, yuksek_esik - 1e-9, 101],
                         labels=["🟢 Düşük", "🟠 Orta", "🔴 Yüksek"])

# Bölüm filtresi (veri yüklendikten sonra kurulur)
with st.sidebar:
    tum_bolumler = sorted(sonuc["Bölüm"].unique())
    secili = st.multiselect("Bölüm filtresi", tum_bolumler, default=tum_bolumler)
gorunen = sonuc[sonuc["Bölüm"].isin(secili)]
if gorunen.empty:
    st.warning("Seçili bölümlerde öğrenci yok.")
    st.stop()

sekme1, sekme2, sekme3, sekme4 = st.tabs(["📊 Genel Bakış", "🚨 Riskli Öğrenciler",
                                           "👤 Öğrenci Detayı", "ℹ️ Model ve Yöntem"])

# ====================== SEKME 1: GENEL BAKIŞ ======================
with sekme1:
    n = len(gorunen)
    yuksek_n = (gorunen["Seviye"] == "🔴 Yüksek").sum()
    orta_n = (gorunen["Seviye"] == "🟠 Orta").sum()
    dusuk_n = (gorunen["Seviye"] == "🟢 Düşük").sum()
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Toplam öğrenci", f"{n:,}".replace(",", "."), "Analiz edilen kayıt")
    with c2: kpi("Yüksek risk", yuksek_n, f"%{100*yuksek_n/n:.1f} · öncelikli destek", "#C0392B")
    with c3: kpi("Orta risk", orta_n, f"%{100*orta_n/n:.1f} · izlenmeli", "#E67E22")
    with c4: kpi("Ortalama risk", f"%{gorunen['Risk (%)'].mean():.1f}", f"Düşük risk: {dusuk_n} öğrenci", "#27AE60")
    st.write("")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Risk seviyesi dağılımı**")
        dagilim = gorunen["Seviye"].value_counts().reindex(["🟢 Düşük", "🟠 Orta", "🔴 Yüksek"]).fillna(0)
        st.bar_chart(dagilim)
    with g2:
        st.markdown("**Bölüme göre ortalama risk (%)**")
        bolum_risk = gorunen.groupby("Bölüm")["Risk (%)"].mean().sort_values().round(1)
        st.bar_chart(bolum_risk, horizontal=True)
    st.markdown("**Yüksek riskli öğrencilerde en sık görülen risk faktörleri**")
    sayac = {}
    for no in gorunen.loc[gorunen["Seviye"] == "🔴 Yüksek", "Öğrenci No"]:
        for s in anahtarlar[no]:
            sayac[SUTUN_TR.get(s, s)] = sayac.get(SUTUN_TR.get(s, s), 0) + 1
    if sayac:
        st.bar_chart(pd.Series(sayac).sort_values(), horizontal=True)
    else:
        st.caption("Bu eşikte yüksek riskli öğrenci yok.")

# ====================== SEKME 2: RİSKLİ ÖĞRENCİLER ======================
with sekme2:
    f1, f2 = st.columns([2, 1])
    seviyeler = f1.multiselect("Risk seviyesi", ["🔴 Yüksek", "🟠 Orta", "🟢 Düşük"],
                               default=["🔴 Yüksek"])
    aranan = f2.text_input("Öğrenci no ara")
    liste = gorunen[gorunen["Seviye"].isin(seviyeler)]
    if aranan.strip():
        liste = liste[liste["Öğrenci No"].astype(str).str.contains(aranan.strip())]
    liste = liste.sort_values("Risk (%)", ascending=False)[
        ["Öğrenci No", "Bölüm", "Risk (%)", "Seviye", "Neden 1", "Neden 2", "Neden 3"]]
    st.caption(f"{len(liste)} öğrenci listeleniyor")
    st.dataframe(liste, width="stretch", hide_index=True, height=520,
                 column_config={"Risk (%)": st.column_config.ProgressColumn(
                     "Risk (%)", min_value=0, max_value=100, format="%.1f")})
    st.download_button("⬇️ Listeyi CSV olarak indir", liste.to_csv(index=False).encode("utf-8-sig"),
                       file_name="riskli_ogrenciler.csv", mime="text/csv")

# ====================== SEKME 3: ÖĞRENCİ DETAYI ======================
with sekme3:
    sirali = gorunen.sort_values("Risk (%)", ascending=False)
    risk_sozluk = dict(zip(sirali["Öğrenci No"], sirali["Risk (%)"]))
    secilen = st.selectbox("Öğrenci seçin (riskten düşüğe sıralı)", list(risk_sozluk),
                           format_func=lambda no: f"{no}  —  %{risk_sozluk[no]:.1f}")
    satir = sonuc[sonuc["Öğrenci No"] == secilen].iloc[0]
    d1, d2, d3 = st.columns(3)
    with d1: kpi("Öğrenci no", satir["Öğrenci No"])
    with d2: kpi("Risk", f"%{satir['Risk (%)']:.1f}", str(satir["Seviye"]))
    with d3: kpi("Bölüm", "", satir["Bölüm"])
    st.write("")
    sol, sag = st.columns(2)
    with sol:
        st.markdown("**Başlıca risk faktörleri**")
        nedenler = [v for v in [satir["Neden 1"], satir["Neden 2"], satir["Neden 3"]] if v]
        if nedenler:
            st.markdown("".join(f'<span class="etiket">{v}</span>' for v in nedenler), unsafe_allow_html=True)
        else:
            st.caption("Riski belirgin şekilde artıran bir faktör bulunmuyor.")
        st.markdown("**Önerilen destek adımları**")
        oneriler = [ONERI.get(s, "Akademik danışman görüşmesi") for s in anahtarlar[secilen]]
        for o in dict.fromkeys(oneriler):
            st.markdown(f"- {o}")
        if not oneriler:
            st.markdown("- Rutin izleme yeterli")
        st.caption("Öneriler kural tabanlıdır; nihai karar ilgili birimlere aittir.")
    with sag:
        st.markdown("**Faktör etkileri** (pozitif: riski artırır, negatif: azaltır)")
        etki = shap_df.loc[secilen].rename(index=SUTUN_TR).sort_values().tail(8)
        st.bar_chart(etki, horizontal=True)

# ====================== SEKME 4: MODEL VE YÖNTEM ======================
with sekme4:
    m1, m2, m3 = st.columns(3)
    with m1: kpi("Algoritma", "", "Gradient Boosting + SHAP açıklamaları")
    with m2: kpi("Test başarımı (ROC-AUC)", "0,70", "Çapraz doğrulama: 0,71")
    with m3: kpi("Kullanılan özellik", len(sutunlar), "Yalnızca dönem başı kayıt bilgileri")
    st.write("")
    st.markdown("""
**Amaç:** Öğrencinin 1. dönemde aldığı derslerden en az birinden kalma olasılığını, dönem başında
bilinen bilgilerle tahmin etmek.

**Hedef tanımı:** 1. dönemde alınan ders sayısı geçilen ders sayısından fazlaysa öğrenci "başarısız" sayılır.

**Modele giren bilgiler:** Bölüm, giriş ve önceki eğitim notu, kayıt yaşı, burs durumu, başvuru türü,
aile bilgileri vb. Dönem içi notlar ve makroekonomik göstergeler **kullanılmaz**.

**Açıklanabilirlik:** Her öğrenci için SHAP yöntemiyle riski artıran başlıca faktörler gösterilir.
""")
    k1, k2 = st.columns(2)
    with k1:
        st.markdown('<div class="kutu"><b>⚠️ Sınırlılıklar</b><ul>'
                    '<li>Model orta düzeyde ayırt edicidir (AUC ≈ 0,70); kesin hüküm değil, öncelik sıralaması üretir.</li>'
                    '<li>Eğitim verisi tek bir ülkedeki açık bir araştırma veri setidir; kendi kurumunuzun verisiyle yeniden eğitilmeli ve doğrulanmalıdır.</li>'
                    '<li>Faktörler ilişkiyi gösterir, nedensellik kanıtı değildir.</li>'
                    '<li>"Başarısız" tanımı sıkıdır (1 dersten kalmak); öğrencilerin yarıdan fazlası bu gruba girebilir.</li>'
                    '</ul></div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="kutu"><b>🔒 Veri gizliliği ve etik</b><ul>'
                    '<li>Bu uygulama yüklenen veriyi diske kaydetmez; yalnızca oturum süresince bellekte işler.</li>'
                    '<li>Gerçek öğrenci verisi için kurum içi sunucu ve KVKK uyumu gerekir; herkese açık bir bağlantıya yüklenmemelidir.</li>'
                    '<li>Cinsiyet ve yaş gibi kişisel özelliklerin kullanımı adalet açısından ayrıca değerlendirilmelidir.</li>'
                    '<li>Sonuçlar cezalandırma için değil, destek sunmak için kullanılmalıdır.</li>'
                    '</ul></div>', unsafe_allow_html=True)
    st.write("")
    sablon = pd.DataFrame(columns=["ogrenci_no"] + sutunlar)
    st.download_button("⬇️ Şablon CSV'yi indir (gerekli sütunlar)",
                       sablon.to_csv(index=False).encode("utf-8-sig"),
                       file_name="sablon_ogrenci_verisi.csv", mime="text/csv")
