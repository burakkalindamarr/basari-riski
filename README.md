# Akademik İçgörü

**Üniversite öğrencilerinde akademik başarısızlık riskinin erken tahmini**

Öğrencinin dönem başında bilinen bilgilerini kullanarak ilk dönem sonunda en az bir dersten kalma olasılığını tahmin eden bir makine öğrenmesi projesi. Tahminin hangi özelliklerden etkilendiği SHAP ile açıklanır.

**[Canlı uygulamayı aç](https://akademik-icgoru.vercel.app/)**

## Özellikler

- Tek öğrenci için risk tahmini ve SHAP açıklaması
- CSV ile toplu analiz, filtreleme ve sonuç indirme
- Risk dağılımı, bölüm karşılaştırması ve model performansı
- Açık/koyu tema destekli web arayüzü

## Veri ve model

[UCI öğrenci başarı verisi](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success) kullanıldı. İlk dönemde ders almayanlar çıkarıldıktan sonra **4.244 öğrenci** ve dönem başında bilinebilen **16 özellik** değerlendirildi. Hedef, ilk dönem sonunda **en az bir dersten kalma** durumudur.

Geliştirme verisinde iç içe çapraz doğrulama ile elde edilen sonuçlar:

| Metrik | Sonuç |
|---|---:|
| ROC-AUC | 0,712 |
| Recall (%50 eşik) | %82,3 |
| En riskli %20'de isabet | %81,8 |

Bunlar **iç doğrulama** sonuçlarıdır; farklı bir üniversitede bağımsız test yapılmadı. Canlı tahminlerde Gradient Boosting modeli kullanılıyor. Ayrıntılar: [model kartı](docs/MODEL_CARD.md) ve [deney raporu](experiments/results/NESTED_CV_REPORT.md).

## Teknolojiler

**Python, Scikit-learn, SHAP, FastAPI, React, TypeScript**

- `backend/`: Tahmin ve açıklama API'si
- `frontend/`: Web arayüzü
- `src/`, `experiments/`: Veri hazırlama ve model deneyleri
- `docs/`: Teknik raporlar ve kurulum

Yerel kurulum: [Geliştirme notları](docs/LOCAL_DEVELOPMENT.md).

> Bu proje bir araştırma prototipidir. Gerçek öğrenci verileri herkese açık demoya yüklenmemeli; tahminler otomatik akademik karar amacıyla kullanılmamalıdır.

Veri: Realinho vd., UCI Machine Learning Repository, [DOI: 10.24432/C5MC89](https://doi.org/10.24432/C5MC89), CC BY 4.0.
