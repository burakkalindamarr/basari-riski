# CV ve Portföyde Projenin Sunumu

## Türkçe CV (kısa)

**Üniversite Öğrencilerinde Akademik Başarısızlık Riskinin Açıklanabilir Yapay Zekâ ile Erken Tahmini**
Python · Scikit-learn · SHAP · FastAPI · React · TypeScript · Tailwind CSS

16 dönem başı değişkeniyle öğrencilerin birinci dönem sonunda en az bir dersten kalma riskini öngören, SHAP ile tahminlerini açıklayan makine öğrenmesi araştırma prototipi geliştirdim. Modelleri iç içe çapraz doğrulama (5 dış/3 iç kat), olasılık kalibrasyonu ve grup bazlı hata analizleriyle değerlendirdim. Geliştirme verisinde ROC-AUC ~0,712; en riskli %20 grupta başarısızlık oranı ~%81,8. Gerçek modeli kullanan FastAPI servisi üzerine açık/koyu tema destekli React dashboard, CSV analizi ve manuel öğrenci tahmin ekranı oluşturdum.

## English CV (short)

**Explainable AI for Early Academic Failure Risk Prediction**
Python · Scikit-learn · SHAP · FastAPI · React · TypeScript · Tailwind CSS

Built a research prototype that predicts first-semester course failure risk from 16 pre-semester features. Evaluated ML pipelines using nested cross-validation (5 outer/3 inner folds), probability calibration checks, and subgroup error analysis (development-set ROC-AUC ≈0.712; precision within the highest-risk 20% ≈81.8%). Developed an explainability-enabled FastAPI backend and a responsive React dashboard featuring individual predictions, CSV analysis, and light/dark themes.

## Mülakat sırasında açıklanması gerekenler

- **Hedef ne?** Birinci dönemde alınan derslerden en az birinden kalmak; mezuniyet veya okuldan ayrılma değil.
- **Neden 16 değişken?** Dönem başlangıcında bilinebilen girdilerle veri sızıntısını azaltmak için.
- **Neden nested CV?** Algoritma ve hiperparametre seçimiyle performans değerlendirmesini ayırmak için.
- **AUC neden 0,71?** Orta düzey ayrım gücü. Kesin karar yerine önceliklendirme için aday kullanım.
- **Precision@20 neden önemli?** Kurum yalnızca en riskli %20'lik gruba destek ayırabiliyorsa hedefleme kalitesini anlatır.
- **SHAP neyi açıklıyor?** Tahmine yapılan model katkısını, log-odds biriminde. Nedensellik değil.
- **Adillik sorunu?** Bazı alt gruplarda recall ve FPR farklı. Bu yüzden dış doğrulama ve adillik değerlendirmesi gerekli.
- **Gerçek kurumda kullanılabilir mi?** Henüz hayır: Portekiz verisiyle çalışma, dış doğrulama yok, KVKK/kimlik doğrulama/kurumsal güvenlik eksik.

## Portföy sunum ilkeleri

CV'de gerçek ölçümler ve doğrulanmış teknoloji kullanımı anlatılmalı. Bağımsız test başarıları icat edilmemeli; bir teknolojiyi yalnızca planladığınız için kullanılmış olarak yazmayın. Projenin GitHub README'sinde çalışma yöntemi, kaynak, sonuç, sınırlılıklar ve kurulum görünür olmalıdır.
