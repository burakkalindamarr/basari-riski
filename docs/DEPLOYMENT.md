# Yayına Alma | React + FastAPI

**Durum:** Canlı araştırma demosu 18.10.2026 tarihinde ücretsiz Render API ve Vercel Hobby frontend ile yayınlandı. **Frontend:** https://akademik-icgoru.vercel.app/ · **API:** https://akademik-icgoru-api.onrender.com/api/health. GitHub Actions canlı smoke testi `/api/health`, `/api/demo`, `/api/schema` ve CORS doğrulamasından başarıyla geçti. **Not:** Vercel GitHub repository entegrasyonu henüz etkin değil; ilk yayın kaynak dosyaları doğrudan Vercel'e gönderilerek yapıldı. GitHub'a yapılan yeni commit'ler otomatik olarak Vercel frontend'ine yansımaz. Aşağıdaki adımlar temiz kurulum veya otomatik güncelleme içindir.

## 1. API: Render

1. GitHub deposunu Render hesabına bağlayın.
2. **Blueprints** üzerinden repo kökündeki `render.yaml` dosyasını seçin.
3. Bir Python web servisi oluşturulacak. Dosya `backend/requirements.txt` bağımlılıklarını kurar ve `backend.main:app` uygulamasını başlatır.
4. `FRONTEND_ORIGINS` ortam değişkenini gerçek Vercel arayüzünün tam HTTPS adresi yapın. Birden çok izinli origin için virgülle ayırın. Yıldız (`*`) kullanmayın.
5. `/api/health` adresinden modelin başarıyla yüklendiğini doğrulayın.
6. Render planının CPU/bellek kapasitesi, SHAP ve Scikit-learn bağımlılıkları için yeterli olmalı. Free plan uykuya geçebilir veya kaynak sınırlarına takılabilir; gerektiğinde servis planını yükseltin.

**Mevcut canlı API:** `https://akademik-icgoru-api.onrender.com/api/health`

## 2. Arayüz: Vercel

1. Vercel'e GitHub hesabınızla giriş yapın ve `burakkalindamarr/basari-riski` deposunu içe aktarın.
2. Projenin **Root Directory** alanını `frontend` yapın.
3. Framework: **Vite**. Build komutu: `npm run build`. Output Directory: `dist`.
4. Vercel Environment Variables içine `VITE_API_URL` ekleyin. Değer: Render API HTTPS adresi ve `/api` soneki.
5. Dağıtımdan sonra Vercel'in gerçek proje URL'sini Render'daki `FRONTEND_ORIGINS` alanına kaydedin. Render servisini yeniden başlatın.
6. Hem frontend hem backend'in HTTPS kullandığını doğrulayın.

**Mevcut frontend ayarı:** `VITE_API_URL=https://akademik-icgoru-api.onrender.com/api`

**Not:** Vite env değişkenleri build sırasında paketlenir. URL değişirse Vercel'i yeniden derleyin.

## 3. Yayın kontrol listesi

- [ ] `GET /api/health` yanıtı `200` ve `model: loaded`.
- [ ] `GET /api/demo` örnek öğrenci risklerini ve SHAP katkılarını döndürüyor.
- [ ] Kurumsal panel, risk grafikleri, filtreler ve açık/koyu tema çalışıyor.
- [ ] Manuel tek öğrenci tahmini çalışıyor, yanlış kategori kodu reddediliyor.
- [ ] CSV (anonim/sentetik veriyle) yükleme, hatalı sütun, bozuk sayı ve çift ID testleri geçiyor.
- [ ] Mobilde menü ve tablo kullanılabilir.
- [ ] `/api/health`, `/api/schema` ve `/api/demo` üzerinde önbelleğe almama başlığı bulunuyor.
- [ ] Yükleme limiti 2 MB / 2000 öğrenci.
- [ ] Frontend ve API yalnızca izin verilen origin ile iletişim kuruyor.
- [ ] GitHub Actions: backend testleri + frontend build başarılı.
- [ ] README'ye **yalnızca gerçek çalışan yeni URL** eklendi.

## 4. Kişisel veri ve güvenlik uyarısı

Bu uygulama henüz kurumsal üretim sistemi değildir. Anonim bir demo hesabında kimlik doğrulama, yetkilendirme, merkezi denetim, talep/CPU sınırlaması, veri saklama sözleşmeleri ve KVKK süreçleri kurulmadı.

- **Gerçek öğrencilerin kimlik/iletişim/akademik bilgilerini internet üzerinden yüklemeyin.**
- Kod, CSV içeriğini kendi isteğiyle diske kaydetmez; bu barındırma sağlayıcısının ağ günlüklerini, izlemesini veya yedekleme politikalarını kapsayan bir garanti değildir.
- Gerçek kullanım için kimlik doğrulama, kurumsal onay, veri işleme koşulları, role dayalı erişim, log maskeleme, erişim sınırları ve bağımsız model doğrulaması gerekir.
- Risk kategorilerindeki %50/%75 eşikleri örnektir; öğrenciler hakkında otomatik karar vermek için onaylı değildir.

## 5. Hata ayıklama

**CORS hatası:** `FRONTEND_ORIGINS` değerinde Vercel sayfasının eksiksiz `https://...` adresini (sonunda / olmadan) kullanın.

**API bağlantı hatası:** Vercel'de `VITE_API_URL` ayarının Render'ın gerçek HTTPS adresini içerdiğini, sonunun `/api` olduğunu ve Render'ın ayakta olduğunu doğrulayın.

**500 model hatası:** Render loglarını ve `model.joblib` dosyasını kontrol edin. Üçüncü kişilerden gelen joblib dosyalarını **asla** yüklemeyin.

**Backend RAM:** Büyük CSV/SHAP açıklama hesapları bellek kullanır. Demo amaçlı veri büyüklüğünü sınırlayın; geniş ölçek için kuyruk ve kota gerekir.

**Eski Streamlit:** Yeni servis URL'si doğrulanana kadar eski siteyi koruyun.
