# Dağıtım

**Frontend:** https://akademik-icgoru.vercel.app/
**API:** https://akademik-icgoru-api.onrender.com

Arayüz Vercel üzerinde Vite/React, API ise Render üzerinde FastAPI/Scikit-learn ile çalışır. Render servisi Frankfurt bölgesinde ücretsiz planla kurulmuştur. Ücretsiz sunucu kullanılmadığında uykuya geçebilir; ilk istek gecikebilir.

## Geçerli yapılandırma

| Servis | Ayar | Değer |
|---|---|---|
| Render | Branch | `main` |
| Render | Build | `pip install -r backend/requirements.txt` |
| Render | Start | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| Render | `FRONTEND_ORIGINS` | `https://akademik-icgoru.vercel.app` |
| Vercel | Framework / build | Vite / `npm run build` |
| Vercel | Output | `dist` |
| Vercel | `VITE_API_URL` | `https://akademik-icgoru-api.onrender.com/api` |

## Güncelleme ve yeniden dağıtım

Render GitHub deposundaki `main` dalını izliyor. Backend değişikliklerinde otomatik dağıtım yapılıyor.

**Vercel'in GitHub repository entegrasyonu henüz kurulmadı.** İlk frontend dağıtımı repodaki `frontend/` dosyalarının doğrudan Vercel'e aktarılmasıyla yapıldı. Bu nedenle GitHub'a yapılan yeni frontend commit'leri Vercel'deki siteyi **kendiliğinden güncellemez**. Otomatik dağıtım için Vercel panelinde projeye GitHub entegrasyonu ve `burakkalindamarr/basari-riski` deposu bağlanmalı. Bağlantı kurulurken proje kökü `frontend` olmalı; mevcut `VITE_API_URL` korunmalı.

Yeni frontend dağıtımı yapıldığında Vercel ortam değişkenlerinin build sırasında kullanıldığını unutmayın. API veya alan adı değişirse `FRONTEND_ORIGINS` ve `VITE_API_URL` birlikte güncellenmeli.

## Canlı kontroller

GitHub Actions'taki [canlı smoke testi](https://github.com/burakkalindamarr/basari-riski/actions/workflows/live-smoke.yml) şu kontrolleri yapıyor:

- Frontend sayfasının HTTP 200 ile açılması.
- API'nin kaydedilmiş modeli yüklemesi ve doğru CORS başlığı dönmesi.
- Demo verisindeki 849 kayıt için tahmin ve SHAP açıklamalarının bulunması.
- Tek öğrenci formunun 16 alanını sunan şemanın çalışması.

Bu testler yayının çalıştığını gösterir, modelin farklı üniversitelerde geçerli olduğunu **göstermez**.

## Gizlilik ve operasyon notları

Uygulama anonim/sentetik araştırma demosu olarak yayımlanmıştır. Kurum içi kimlik doğrulama, rol bazlı yetkilendirme, KVKK süreçleri, hız sınırı ve gerçek öğrenci verisi için veri işleme sözleşmeleri yoktur. **Kişisel öğrenci verileri yüklenmemelidir.**

API yüklenen CSV'yi kendi kodunda kalıcı dosyaya yazmaz; barındırma sağlayıcısının altyapı günlükleri ayrı değerlendirilmelidir. Gerçek kurum dağıtımından önce güvenlik, erişim kontrolü, kapasite ve bağımsız model doğrulaması gerekir.

**API bağlantı sorunu:** Render servisinin durumunu ve Vercel'deki `VITE_API_URL` değerini kontrol edin. **CORS sorunu:** Render'daki `FRONTEND_ORIGINS` değeri ziyaret edilen sitenin tam HTTPS adresiyle aynı olmalı.
