# Nested Cross-Validation Sonuç Raporu

> **Durum:** Model geliştirme doğrulaması. Bağımsız dış doğrulama değildir.

## Amaç

Üniversite öğrencilerinde dönem başı 16 değişkenden, birinci dönem sonunda en az bir dersten kalma riskini değerlendirmek. Hedef: `Curricular units 1st sem (enrolled) > Curricular units 1st sem (approved)`.

## Deney tasarımı

- Veri: GitHub'daki `data_3.csv` dosyasıyla birebir aynı baytları içeren CSV. Git blob SHA-1: `7b4fccbaccf8fd2427f4d4bd12d78caca0b4dcbf`.
- 4.244 öğrenci; 3.395'i geliştirme kümesinde, geçmişte kullanılmış 849'u değerlendirme dışında.
- Dış döngü: 5-katlı StratifiedKFold (random_state=2026).
- İç döngü: 3-katlı StratifiedKFold (random_state=2027).
- Model seçimi: GridSearchCV ile iç katlarda ROC-AUC.
- Modeller: Lojistik regresyon (C=0.3/1.0), Random Forest (120 ağaç, min_samples_leaf=3/6), Gradient Boosting (100 ağaç, learning_rate=0.05/0.1).
- Her dış katta sadece ilgili eğitim bölümünde OneHotEncoder ve StandardScaler öğrenildi.
- Çalıştırma ortamı: Python/scikit-learn 1.8.0, pandas 2.2.3, NumPy 2.3.5. GitHub Actions betiği farklı sabitlenmiş sürümlerde yeniden çalıştırılabilir.

## Dış katların sonuçları

| Dış kat | İç döngüde seçilen model | ROC-AUC | Brier | Precision@%20 | Lift@%20 |
|---|---|---:|---:|---:|---:|
| 1 | Logistic Regression | 0.6979 | 0.2144 | 0.8309 | 1.40 |
| 2 | Gradient Boosting | 0.7249 | 0.2046 | 0.8235 | 1.39 |
| 3 | Gradient Boosting | 0.7048 | 0.2109 | 0.7794 | 1.31 |
| 4 | Random Forest | 0.7293 | 0.2047 | 0.8382 | 1.42 |
| 5 | Random Forest | 0.7011 | 0.2114 | 0.8162 | 1.38 |

## Ortalama ± katlar arası standart sapma

| Metrik | Sonuç |
|---|---:|
| ROC-AUC | **0.7116 ± 0.0145** |
| Brier | **0.2092 ± 0.0044** |
| Recall (%50 eşik) | 0.8227 ± 0.0564 |
| Precision (%50 eşik) | 0.6835 ± 0.0099 |
| F1 (%50 eşik) | 0.7458 ± 0.0226 |
| Precision@%20 | **0.8176 ± 0.0229** |
| Recall@%20 | 0.2762 ± 0.0079 |
| Lift@%20 | **1.3790 ± 0.0394** |

Seçilen algoritmalar: Gradient Boosting 2 kat, Random Forest 2 kat, Logistic Regression 1 kat.

## Yorum

Modelin sıralama başarısı, en riskli %20'lik grupta yaklaşık %81,8 gerçek başarısızlık oranı ve genel başarısızlık oranına kıyasla yaklaşık 1,38 kat yoğunlaşma sunuyor. Buna rağmen başarısız öğrencilerin yaklaşık %72,4'ü bu küçük öncelikli grubun dışında kalıyor. Sonuç, kesin karar aracı değil, sınırlı öğrenci destek kaynaklarının önceliklendirilmesine yönelik bir **aday model** olduğunu gösteriyor.

Model seçimi katlar arasında değişiyor; tek algoritmayı baskın üstün ilan etmek için kanıt yetersiz.

## Geçerlilik sınırlamaları

1. Eski %20 test kümesinin sonuçları daha önce model/özellik geliştirme sürecinde görüldü. Bu küme artık bağımsız final test olarak sunulmamalı.
2. Aynı veri seti üzerinde daha önce yapılan özellik seçimi ve analizler nedeniyle Nested CV sonuçları da tam anlamıyla dış geçerlik kanıtı değildir.
3. Katlar arası standart sapma istatistiksel güven aralığı değildir.
4. Tek kuruma/ülkeye ait veri için kurumlar arası genellenebilirlik gösterilmedi.
5. Risk tahmini ile destek müdahalesinin etkisi farklı kavramlardır; bu deney destek verilince başarının artacağını kanıtlamaz.

**Takip çalışmaları:** Geliştirme verisinde [grup bazlı hata analizi](../../docs/FAIRNESS_AUDIT.md) yapıldı. Bağımsız yeni dönem/üniversite verisi, olasılık kalibrasyonu, adillik metriklerinin güven aralıkları ve destek kapasitesine göre eşik seçimi hâlâ açık konulardır.

## Tekrar üretim

```bash
python -m pip install numpy pandas scikit-learn
python experiments/run_nested_cv.py
```

GitHub çalışma akışı: `.github/workflows/nested-cv.yml`. Bu rapordaki sonuçlar GitHub Actions üzerinden değil, dosyası doğrulanmış yerel analizden üretildi.
