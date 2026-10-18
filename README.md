# Akademik Başarısızlık Riskinin Açıklanabilir Yapay Zekâ ile Erken Tahmini

Birinci dönem başında bilinen bilgilerle öğrencilerin **dönem sonunda en az bir dersten kalma riskini** tahmin eden ve tahminleri SHAP ile açıklayan makine öğrenmesi araştırma prototipi.

[Canlı Streamlit demosu](https://basari-riski-hyy5vq8hxkvtaryukvztbv.streamlit.app/) · [Model kartı](docs/MODEL_CARD.md) · [Nested CV sonuç raporu](experiments/results/NESTED_CV_REPORT.md)

## Yeni web arayüzü (React + FastAPI MVP)

Kurumsal görünümlü, açık/koyu tema destekli yeni uygulamanın ilk sürümü `frontend/` ve `backend/` klasörlerinde geliştiriliyor. Mevcut canlı Streamlit sürümü etkilenmez.

- **FastAPI:** Kaydedilmiş Gradient Boosting modeliyle gerçek tahminler, demo verisi, güvenli boyut/şema kontrollü CSV analizi.
- **React + TypeScript:** Genel bakış, risk sıralaması, bölüm grafikleri, öğrenci detayı, CSV çıktı.
- **Testler:** Backend için pytest, frontend için TypeScript/Vite derlemesi.
- **Henüz eklenmeyenler:** SHAP ayrıntı ekranı ve manuel öğrenci formu.

Yeni uygulama **henüz internette yayınlanmadı**. Yerel kurulum için [React + FastAPI geliştirme kılavuzu](docs/WEB_MVP.md) dosyasını inceleyin. Gerçek öğrenci bilgilerini herkese açık bir demoya yüklemeyin.

## Proje hakkında

Amaç, bir üniversitenin sınırlı öğrenci destek kaynaklarını hangi öğrencilere öncelikli ayırabileceğini araştırmaktır. **Hedef**, kaynak veri setindeki okuldan ayrılma/mezuniyet etiketi değildir. Birinci dönemde kayıtlı derslerin herhangi birinden kalındıysa `1`, tüm dersler geçildiyse `0` olarak belirlenir.

Kullanılan veri: UCI Machine Learning Repository – [Predict Students' Dropout and Academic Success](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success). Portekiz kaynaklı 4.424 kaydın 180'i ders almamıştır. Kalan 4.244 kayıtta 16 dönem başı özellik kullanılır.

**Teknolojiler:** Python, Pandas, NumPy, Scikit-learn, SHAP, Streamlit, Joblib, Pytest.

### Modelleme yöntemi

- Kategorik alanlarda OneHotEncoder, sayısal alanlarda StandardScaler, birlikte sklearn Pipeline.
- Birinci/ikinci dönem notları, `Target` ve dönem sonrasında öğrenilebilecek bilgiler tahmin girdilerinde yer almaz.
- Lojistik Regresyon, Karar Ağacı, Random Forest ve Gradient Boosting ile karşılaştırmalar; ilk deneylerde KNN ve SVM.
- ROC-AUC, Precision, Recall, F1, Brier, Precision@k, Recall@k ve Lift@k değerlendirmeleri.

### Geliştirme kümesinde iç doğrulama

Model geliştirme sırasında eski %20 test kümesine bakıldığı için artık bağımsız son test olarak kullanılamaz. Eski %80 geliştirme verisi üzerinde 5 dış ve 3 iç katlı nested çapraz doğrulama yapılmıştır.

| Metrik | Sonuç |
|---|---:|
| ROC-AUC | **0,7116** |
| Brier | **0,2092** |
| Recall (%50 eşik) | **%82,27** |
| Precision (%50 eşik) | **%68,35** |
| F1 | **0,7458** |
| En riskli %20'lik grupta başarısızlık oranı | **%81,76** |
| Toplam başarısızların bu grupta yakalanma oranı | **%27,62** |
| Lift@%20 | **1,379** |

Bu değerler keşifsel iç doğrulama sonuçlarıdır, dış doğrulama değildir. En riskli %20'lik grupta başarısızlık oranı genel ortalama olan yaklaşık %59,3'ün üzerindedir ancak başarısız öğrencilerin çoğu bu grubun dışında kalır. Bu nedenle model kesin karar değil **önceliklendirme** amacıyla düşünülmelidir.

[Ölçüm yöntemi ve kat bazındaki sonuçlar](experiments/results/NESTED_CV_REPORT.md).

## Kullanıcı arayüzü

Streamlit uygulaması öğrenci CSV'si veya örnek kayıtları üzerinden riskleri sıralar, risk seviyelerini özetler, öğrenci bazlı SHAP faktörleri sunar ve CSV raporu oluşturur. Mevcut uygulama Gradient Boosting kullanmaktadır. Aday Random Forest modeli otomatik olarak dağıtılmaz; SHAP uyumluluk güncellemesi gereklidir.

## Çalıştırma

Proje kökünde Python 3.11 önerilir.

~~~bash
python -m pip install -r requirements.txt
streamlit run app.py
~~~

Mevcut canlı modelin üzerine yazmadan yeni aday modeli üretmek için:

~~~bash
python -m experiments.train_candidate --algorithm gradient_boosting
python -m experiments.train_candidate --algorithm random_forest
~~~

Modeller ve sürüm/veri meta bilgisi `local_artifacts/` klasörüne kaydedilir; bu klasör Git tarafından takip edilmez.

Otomatik testler:

~~~bash
python -m pip install pytest
python -m pytest tests/ -q
~~~

Nested model seçimi/değerlendirmesi:

~~~bash
python experiments/run_nested_cv.py
~~~

## Dosyalar

| Dosya | Açıklama |
|---|---|
| `app.py` | Streamlit uygulaması |
| `basari_analizi.ipynb` | İlk keşifsel Notebook |
| `src/risk_model.py` | Sabit 16 özellik, hedef hazırlama, preprocessing ve modeller |
| `experiments/train_candidate.py` | Canlı uygulamadan ayrı yeniden üretilebilir model eğitimi |
| `experiments/run_nested_cv.py` | İç içe çapraz doğrulama |
| `experiments/results/NESTED_CV_REPORT.md` | İç değerlendirme sonuç raporu |
| `tests/test_risk_model.py` | Veri kalitesi ve model testleri |
| `docs/MODEL_CARD.md` | Kullanım amacı, yöntem, sınırlılıklar ve etik |
| `data_3.csv` | Kaynak veri |
| `model.joblib` | Şu anki uygulamada kullanılan model |

## Veri kaynağı, lisans ve sınırlılıklar

Realinho, V., Vieira Martins, M., Machado, J. ve Baptista, L. (2021). *Predict Students' Dropout and Academic Success*. UCI Machine Learning Repository. https://doi.org/10.24432/C5MC89. Veri **CC BY 4.0** lisanslıdır.

Tek ülkeden veri kullanılmıştır; Türkiye için genellenebilirlik doğrulanmamıştır. Demografik özelliklerde yanlılık, yanlış alarm, yanlış negatif ve özel öğrenci verisi riski vardır. SHAP nedensellik kanıtı değildir. Kurumsal değerlendirme olmadan kişisel öğrenci verileri herkese açık uygulamaya yüklenmemelidir.

**Durum:** Araştırma ve öğrenci desteği amaçlı prototip; öğrenciler hakkında otomatik karar vermek için uygun değildir.
