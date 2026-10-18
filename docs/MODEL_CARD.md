# Model Card | Akademik Başarısızlık Riski

## Amaç
Bir öğrencinin **birinci dönemde en az bir dersten kalma** riskini dönem başındaki bilgilerle tahmin etmek. Kullanım hedefi, öğrenci destek hizmetlerinde önceliklendirmedir. Öğrencinin mezuniyeti veya okuldan ayrılması tahmin edilmez.

## Veri
[UCI Machine Learning Repository – Predict Students' Dropout and Academic Success, ID 697](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success). Orijinal veri Portekiz'deki bir kurumdan toplanmıştır. Kaynak: Realinho, V., Vieira Martins, M., Machado, J. ve Baptista, L. (2021), DOI: https://doi.org/10.24432/C5MC89. Veri lisansı: **CC BY 4.0**.

Toplam 4.424 öğrencinin 180'i ilk dönem ders almamış olduğundan çıkarılır. Kalan 4.244 kayıtta 2.516 öğrenci en az bir dersten kalmıştır.

## Hedef ve özellikler
- Hedef: birinci dönem kayıtlı ders sayısı > geçilen ders sayısı ise `1`; bütün dersleri geçtiyse `0`.
- Özellikler: dönem başından bilinen 16 başvuru, akademik geçmiş, burs, aile ve demografik değişken.
- Birinci ve ikinci dönem notları, `Target`, makroekonomik veriler ve harç/borç durumu modele alınmaz.
- OneHotEncoder ve StandardScaler işlemleri Pipeline içinde, eğitim katı dışındaki kayıtları görmeden uygulanır.

## Geçerlilik sonuçları

Eski %20 test kümesi geçmişte özellik/model kararlarını etkilemiştir. O küme artık bağımsız final test değildir. Yeni değerlendirmede eski %80 geliştirme kümesi üzerinde **5 dış × 3 iç katlı Nested CV** kullanılmıştır.

| Metrik | İç doğrulama ortalaması |
|---|---:|
| ROC-AUC | **0,7116** |
| Brier | **0,2092** |
| Recall, %50 eşik | **0,8227** |
| Precision, %50 eşik | **0,6835** |
| F1, %50 eşik | **0,7458** |
| Precision@en riskli %20 | **0,8176** |
| Recall@en riskli %20 | **0,2762** |
| Lift@en riskli %20 | **1,379** |

Gradient Boosting 2, Random Forest 2 ve Lojistik Regresyon 1 dış katta seçildi. Bir algoritmanın baskın üstünlüğü yoktur. Önceden aynı veri setinde yapılan özellik seçimleri nedeniyle nested sonuçlar da tamamen bağımsız doğrulama yerine *keşifsel iç doğrulama* olarak değerlendirilmelidir.

Rapor: [Nested CV sonuçları](../experiments/results/NESTED_CV_REPORT.md).

## Dağıtım durumu
- Canlı Streamlit uygulaması **Gradient Boosting** içeren mevcut `model.joblib` dosyasını kullanmaktadır.
- `python -m experiments.train_candidate` yeni adayları `local_artifacts/` dizinine yazar, canlı dosyanın üzerine yazmaz.
- Random Forest'ın SHAP çıktısı mevcut Streamlit açıklama koduna doğrudan uyumlu değildir. Arayüz değiştirilmeden canlıya alınmamalıdır.
- Arayüzdeki %50 / %75 risk sınıfı eşikleri kurumsal olarak doğrulanmış karar eşikleri değildir.

## Etik / sınırlar
Bu veri Türkiye'deki üniversitelere otomatik olarak genellenemez. Yaş, cinsiyet ve sosyoekonomik değişkenler adillik sorunları doğurabilir; farklı gruplarda hata oranları ayrıca değerlendirilmelidir. SHAP nedensellik kanıtı değildir. Yanlış uyarılar öğrencileri damgalama riski taşır. Gerçek öğrenci verileri herkese açık Streamlit sunucusuna yüklenmemelidir; KVKK ve kurumsal güvenlik süreçleri gereklidir.

**Bağımsız dış doğrulama yapılmamıştır.** Bu sistem akademik destek amaçlı bir araştırma prototipidir, otomatik idari/akademik karar mekanizması değildir.
