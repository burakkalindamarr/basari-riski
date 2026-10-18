# Keşifsel Grup Bazlı Hata ve Adillik Denetimi

**Durum:** Tamamlanan ilk grup karşılaştırması. Bu sonuçlar yalnızca geliştirme verisindeki çapraz doğrulama tahminlerinden elde edildi; **bağımsız test değildir**.

## Yöntem

- 4.244 öğrenciden sabit `random_state=42` ile ayrılmış 3.395 geliştirme öğrencisi.
- 16 dönem başı değişkeniyle Gradient Boosting modeli; 5 katlı kat-dışı (out-of-fold) tahmin.
- Karar eşiği: %50 (mevcut uygulamanın örnek eşiği, bilimsel karar sınırı değildir).
- Değerlendirilen alt gruplar: veri setindeki koduyla Gender, Scholarship holder, Displaced.
- ROC-AUC, Recall (TPR), False Positive Rate (FPR), Precision, Brier ve örneklem büyüklüğü.
- UCI kaynak gruplar gerçek Türk öğrencilerini veya diğer kurumları temsil etmek zorunda değildir.

## Gözlemlenen sonuçlar

| Grup | Kod | N | Gerçek başarısızlık % | Recall | FPR | Precision | Brier | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Gender | 0 | 2255 | 54,9 | 0,754 | 0,474 | 0,659 | 0,217 | 0,702 |
| Gender | 1 | 1140 | 68,1 | 0,894 | 0,701 | 0,731 | 0,194 | 0,697 |
| Scholarship holder | 0 | 2552 | 65,8 | **0,878** | 0,731 | 0,698 | 0,208 | 0,669 |
| Scholarship holder | 1 | 843 | 39,6 | **0,458** | 0,196 | 0,605 | 0,213 | 0,698 |
| Displaced | 0 | 1590 | 63,9 | 0,863 | 0,594 | 0,720 | 0,200 | 0,713 |
| Displaced | 1 | 1805 | 55,2 | 0,752 | 0,491 | 0,654 | 0,218 | 0,696 |

Bütün ölçümler aynı %50 kararı ve aynı kat-dışı tahmin yöntemiyle elde edilmiştir.

## Dikkat çeken fark

- Bursluluk kodu 0 grubunda başarısızları yakalama: yaklaşık **%87,8**.
- Bursluluk kodu 1 grubunda başarısızları yakalama: yaklaşık **%45,8**.
- Fark yaklaşık **42 yüzde puanı**; ancak gruplardaki başarısızlık temel oranları (65,8 / 39,6) da çok farklı. Bu nedenle tek başına adaletsiz karar verme veya doğrudan nedensellik kanıtı değildir.
- Gruplar arasında farklı yanlış alarm oranları da görülmektedir.

## Yorum ve yapılması gerekenler

Bu sonuçları bir "adil" etiketiyle sunmak doğru değildir. Takip araştırmasında:

1. Kategorik kod açıklamalarını veri sözlüğüyle doğrulamak.
2. Her grubun güven aralıklarını ve örneklem yeterliliğini raporlamak.
3. Grup bazlı kalibrasyonu ve birden çok eşikte TPR/FPR farkını incelemek.
4. Cinsiyet, burs gibi değişkenler çıkarıldığında model performansı ve grup farkları nasıl değişiyor görmek (sadece çıkarma, yanlılığı otomatik kaldırmaz).
5. Müdahale kapasitesi ve öğrenci destek hedeflerine göre etik bir eşik politikası belirlemek.
6. Türkiye'deki yeni ve bağımsız veriyle tekrar test etmek.

**Önemli:** Bu sistem cezalandırıcı veya otomatik akademik kararlar için uygun değildir. Risk skoru yalnızca araştırma prototipi olarak sunulmaktadır.

## Yeniden üretim

`python experiments/audit_groups.py`

Kaynak: [UCI Predict Students' Dropout and Academic Success](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success).

Çalıştırmada Python 3.13, sklearn 1.8.0, pandas 2.2.3 kullanıldı. API dağıtımı farklı sabitlenmiş sürümle çalışır; küçük sayısal farklar yeniden çalıştırmada raporlanmalıdır.
