# Akademik İçgörü

**Üniversite öğrencilerinde birinci dönem başarısızlık riskinin erken tahmini ve açıklanması**

Öğrencilerin kayıt sırasında bilinen özelliklerinden yararlanarak ilk dönem sonunda en az bir dersten kalma olasılığını tahmin eden bir makine öğrenmesi çalışması. Sonuçlar, öğrenci desteğine ihtiyaç duyabilecek kişileri sıralamak amacıyla hazırlanan bir web arayüzünde gösteriliyor.

**[Canlı uygulama](https://akademik-icgoru.vercel.app/)** · [Model ve sınırlılıklar](docs/MODEL_CARD.md) · [Deney sonuçları](experiments/results/NESTED_CV_REPORT.md)

## Proje ne yapıyor?

- Dönem başında bilinebilen **16 değişken** kullanarak başarısızlık olasılığı hesaplıyor.
- **SHAP** ile tahmini artıran ve azaltan özellik katkılarını gösteriyor. Katkılar log-odds ölçeğindedir, yüzde puanı veya nedensellik değildir.
- Tek öğrenci için form üzerinden, çok sayıda öğrenci için CSV yükleyerek tahmin üretiyor.
- Bölüm bazında özetler, risk sıralaması, filtreler ve indirilebilir rapor sunuyor.
- Model deneylerini ve grup bazındaki hata farklılıklarını ayrı bir performans ekranında raporluyor.

**Kapsam:** Başarısızlık, öğrencinin birinci dönemde aldığı derslerden **en az birinden kalması** olarak tanımlanıyor. Veri setinin orijinal `Target` sütunundaki okuldan ayrılma / mezun olma durumu tahmin edilmiyor.

## Yaklaşım ve sonuçlar

Kaynak: [UCI – Predict Students' Dropout and Academic Success](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success). Toplam 4.424 kayıttan ilk dönem ders almayan 180 kayıt çıkarıldı; **4.244 öğrenci** analizde kaldı.

Girdi sütunları yalnızca dönem başında bilinebilen başvuru, önceki eğitim, burs ve demografik bilgilerden seçildi. Notlar, ders başarıları ve dönem sonundan öğrenilebilecek diğer alanlar modele verilmedi.

Modeller, bir **scikit-learn Pipeline** içinde kodlama ve ölçekleme yapılarak karşılaştırıldı. Geliştirme kümesinde 5 dış / 3 iç katlı çapraz doğrulama kullanıldı.

| Metrik | İç doğrulama sonucu |
|---|---:|
| ROC-AUC | **0,7116** |
| Recall (%50 eşik) | %82,27 |
| Precision (%50 eşik) | %68,35 |
| Brier skoru | 0,2092 |
| En riskli %20'de precision | **%81,76** |

Bu metrikler **keşifsel iç doğrulama** sonuçlarıdır. Daha önce incelenen %20'lik ayrım artık bağımsız test kümesi sayılamaz. Farklı üniversite veya dönemde bağımsız doğrulama yapılmadı. Canlı API, kayıtlı **Gradient Boosting** modelini çalıştırır; tablodaki sonuçlar algoritma seçimini de içeren değerlendirme prosedürüne aittir, tek bir canlı model için bağımsız test iddiası değildir.

Ayrıntılar: [Nested CV raporu](experiments/results/NESTED_CV_REPORT.md) · [Grup bazında hata analizi](docs/FAIRNESS_AUDIT.md).

## Uygulama mimarisi

| Katman | Kullanılan araçlar |
|---|---|
| Web arayüzü | React, TypeScript, Tailwind CSS, Recharts |
| API | FastAPI, Pydantic |
| Model | Python, pandas, NumPy, scikit-learn, SHAP |
| Test | pytest, Playwright, GitHub Actions |
| Yayın | Vercel (arayüz), Render (API) |

API, `model.joblib` dosyasındaki eğitilmiş modeli kullanır. Kodun yerel sürümü ile yayınlanan sürüm arasındaki veri akışı aynıdır:

`CSV / manuel giriş → özellik kontrolü → model tahmini → SHAP açıklaması → API → web arayüzü`

Önceki denemelerde kullanılan [Streamlit arayüzü](https://basari-riski-hyy5vq8hxkvtaryukvztbv.streamlit.app/) de erişilebilir durumdadır.

## Yerel çalıştırma

**Gereksinimler:** Python 3.11 ve Node.js 20+.

Depoyu klonladıktan sonra proje kökünde:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload
```

İkinci terminalde:

```bash
cd frontend
npm install
npm run dev
```

Web arayüzü: **http://localhost:5173** · API dokümantasyonu: **http://127.0.0.1:8000/docs**

Geliştirme komutları, testler ve ortam değişkenleri için [yerel geliştirme notlarına](docs/LOCAL_DEVELOPMENT.md) bakılabilir.

## Depo yapısı

```text
backend/           FastAPI, model açıklamaları ve API testleri
frontend/          React uygulaması ve tarayıcı testleri
src/               Veri hazırlama ve model pipeline'ı
experiments/       Model karşılaştırmaları ve yeniden üretim betikleri
tests/             Model/veri testleri
docs/              Model kartı, adillik analizi ve dağıtım bilgileri
app.py             İlk Streamlit arayüzü
model.joblib       Canlı tahminlerde kullanılan eğitilmiş model
data_3.csv         Araştırmada kullanılan kaynak veri
```

## Sınırlar ve veri kullanımı

Bu proje **araştırma prototipidir**; öğrenciler hakkında otomatik akademik karar vermek için uygun değildir. Çalışma Portekiz kaynaklı bir veri setine dayanır. Grup bazında hata oranlarında farklar gözlendiğinden gerçek kullanım öncesinde adillik, kalibrasyon ve dış doğrulama çalışmaları gerekir. Web demosunda kullanıcı yetkilendirmesi veya kurumsal veri işleme altyapısı bulunmuyor: **gerçek öğrencilere ait kişisel verileri yüklemeyin.**

Kaynak veri: Realinho, V., Vieira Martins, M., Machado, J. & Baptista, L. (2021), *Predict Students' Dropout and Academic Success*, UCI Machine Learning Repository, [DOI: 10.24432/C5MC89](https://doi.org/10.24432/C5MC89), **CC BY 4.0**. Bu lisans bilgisi kaynak veri setine aittir.
