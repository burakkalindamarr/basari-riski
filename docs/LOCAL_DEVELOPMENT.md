# Yerel geliştirme

Projenin API ve arayüzü ayrı süreçlerde çalışır. Python 3.11 ve Node.js 20+ gereklidir.

## Backend

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload
```

API belgeleri: http://127.0.0.1:8000/docs

## Frontend

İkinci terminalde:

```bash
cd frontend
npm install
npm run dev
```

Uygulama: http://localhost:5173. Vite, yerelde /api isteklerini FastAPI'ye yönlendirir.

## Testler

```bash
python -m pytest tests backend/tests -q
cd frontend
npm run build
npx playwright install chromium
npm run test:e2e
```

Playwright için API ayakta olmalıdır. GitHub Actions tam yığın kontrollerini otomatik çalıştırır.

## API uçları

| Yöntem | Adres | Açıklama |
|---|---|---|
| GET | `/api/health` | Eğitilmiş modelin durumu |
| GET | `/api/schema` | Form alanları ve geçerli kodlar |
| GET | `/api/demo` | Örnek öğrenci tahminleri |
| POST | `/api/predict` | Tek öğrenci için JSON tahmini |
| POST | `/api/analyze` | CSV ile toplu tahmin |

Yüklemede 16 dönem başı sütunu gereklidir. `ogrenci_no` isteğe bağlıdır. CSV UTF-8, virgülle ayrılmış ve en fazla 2 MB / 2.000 kayıt olabilir. Yanıttaki SHAP katkıları log-odds birimindedir.

## Model deneyleri

```bash
python -m experiments.train_candidate --algorithm gradient_boosting
python -m experiments.train_candidate --algorithm random_forest
python experiments/run_nested_cv.py
python experiments/audit_groups.py
```

Aday model dosyaları `local_artifacts/` altına yazılır; yayınlanan `model.joblib` dosyası değişmez.

## Ortam değişkenleri

- `FRONTEND_ORIGINS`: API'nin kabul ettiği frontend adresleri (virgülle ayrılmış).
- `VITE_API_URL`: Yayınlanan backend HTTPS adresi, sonunda `/api` olmalı. Yerelde ayarlanması gerekmez.

Yayın ayrıntıları: [DEPLOYMENT.md](DEPLOYMENT.md). Gerçek kişisel öğrenci verilerini bu açık demoya yüklemeyin.
