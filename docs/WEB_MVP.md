# Yeni Web Uygulaması: React + FastAPI (MVP)

Mevcut Streamlit dağıtımı korunur. Bu klasörlerdeki kodlar onun yerine geçecek ayrı bir araştırma prototipinin **ilk sürümünü** oluşturur.

## Neler çalışıyor?

- **FastAPI:** Güvenilir yerel `model.joblib` dosyasını yükler, kaydedilmiş Gradient Boosting ile risk tahminleri döndürür.
- **GET /api/demo:** `ornek_ogrenciler.csv` içindeki anonimleştirilmiş örnek kayıtları gerçek modelle analiz eder.
- **POST /api/analyze:** Şablona uygun CSV'yi geçici olarak bellekte işler; sütun, sayı, öğrenci numarası, satır ve dosya boyutu kontrolleri yapar.
- **React + TypeScript:** Kurumsal panel, risk dağılımı/bölüm grafikleri, risk sıralaması, filtreleme, öğrenci detayı, CSV çıktı ve açık/koyu tema.
- **Kaynak açıklığı:** %50 ve %75 kategorileri örnek eşikler olarak açıkça belirtilmiştir.

**İlk sürüme sonradan eklenenler:** log-odds biriminde SHAP faktör açıklamaları, gerçek model tahmini yapan tek öğrenci formu, 16 değişken için şema/seçenek API'si ve nested CV sonuçlarını görselleştiren performans ekranı.

**Hâlâ kapsam dışında:** Kullanıcı yönetimi, kimlik doğrulama, kurum içi üretim dağıtımı, yeni bağımsız model doğrulaması ve hesaplar üzerinden canlı yayın. Yayın prosedürü: [DEPLOYMENT.md](DEPLOYMENT.md).

## Yerel kurulum

Ana repo klasöründeyken iki terminal açın.

Terminal 1 (API, Python 3.11):

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
~~~

API test: http://127.0.0.1:8000/api/health
API belgeleri: http://127.0.0.1:8000/docs

Terminal 2 (React, Node.js 20+):

~~~bash
cd frontend
npm install
npm run dev
~~~

Tarayıcı: http://localhost:5173

Vite geliştirme proxy'si `/api` yollarını `http://127.0.0.1:8000` adresine yönlendirir.

Testler:

~~~bash
python -m pytest backend/tests -q
cd frontend && npm run build
~~~

## Ortam yapılandırması

Frontend canlı yayımlanırken `VITE_API_URL` backend adresi + `/api` olarak ayarlanmalı.

Örnek: `https://my-backend.example.com/api`

Backend'de izin verilen frontend kökenlerini virgülle ayırın:
`FRONTEND_ORIGINS=https://my-app.example.com`

Frontend HTTPS üzerinden yayınlanıyorsa backend de HTTPS olmalıdır. Değerler gerçek dağıtım alan adlarını temsil etmiyor, örnektir.

**Dağıtım henüz yapılmadı.** Vercel, Render veya başka bir sunucu kurmadan önce güvenlik ve veri işleme süreçlerini doğrulamak gerekir.

## API sonuç örneği (şema)

~~~json
{
  "source": "demo",
  "summary": {"count": 849, "low": 0, "medium": 0, "high": 0, "average_risk": 0.0},
  "students": [
    {"id": "1001", "course": "İşletme", "risk": 0.0, "level": "low", "rank": 1}
  ],
  "courses": [{"course": "İşletme", "count": 1, "average_risk": 0.0}],
  "algorithm": "GradientBoostingClassifier",
  "features": 16,
  "disclaimer": "..."
}
~~~

Bu kod bloğu yalnızca **yapıyı göstermektedir**: metrikler, riskler ve bölüm değerleri örnek amaçlıdır, gerçek tahminler değildir.

## CSV dosya yapısı

Uygulamadaki "CSV sütun şablonunu indir" özelliği boş başlık dosyası verir. `ogrenci_no` isteğe bağlıdır (yoksa sistem sentetik sıra numarası oluşturur). Diğer 16 model özelliği zorunludur. Sayısal özelliklerde boş ve geçersiz değer reddedilir. CSV UTF-8 ve virgülle ayrılmış olmalıdır.

Dosya 2 MB ve 2.000 satırı geçemez. API kendi kodunda yüklemeleri kaydetmez, ancak barındırma sağlayıcısının ağ/log altyapısı ayrıca değerlendirilmelidir. **Gerçek kimlik bilgileri veya öğrenci dosyalarını herkese açık demoya yüklemeyin.**

## Modelin geçerliliği

Yeni arayüz mevcut `model.joblib` içindeki Gradient Boosting'i kullanır. GitHub'daki nested CV metrikleri algoritma seçimi prosedürünün geliştirme sonuçlarıdır; bu bireysel dosyanın bağımsız test kanıtı değildir.

Eklenen arayüzün model doğruluğunu artırdığı iddia edilmez.

## Sonraki geliştirme

1. SHAP açıklamalarını güvenilir şekilde API'ye eklemek (log-odds birimi ve işaretleri açıklanacak).
2. Manuel öğrenci veri giriş formu, değişken sözlüğü, hata mesajları.
3. Filtreleme, CSV güvenliği, erişilebilirlik ve mobil düzen testleri.
4. Eşik kalibrasyonu, alt grup adillik değerlendirmesi ve yeni kurum verisiyle harici doğrulama.
