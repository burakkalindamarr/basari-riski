import { ArrowUpRight, BarChart3, CircleAlert, Target, TrendingUp } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const FOLDS = [
  { fold: 'Kat 1', auc: 0.6979, precision20: 0.8309, model: 'Lojistik Regresyon' },
  { fold: 'Kat 2', auc: 0.7249, precision20: 0.8235, model: 'Gradient Boosting' },
  { fold: 'Kat 3', auc: 0.7048, precision20: 0.7794, model: 'Gradient Boosting' },
  { fold: 'Kat 4', auc: 0.7293, precision20: 0.8382, model: 'Random Forest' },
  { fold: 'Kat 5', auc: 0.7011, precision20: 0.8162, model: 'Random Forest' },
];
const INDIVIDUAL = [
  { model: 'Random Forest', auc: 0.713 },
  { model: 'Gradient Boosting', auc: 0.711 },
  { model: 'Lojistik Regresyon', auc: 0.706 },
];
const stats = [
  { label: 'ROC-AUC', value: '0,7116', note: 'Katlar arası standart sapma: 0,0145', icon: BarChart3 },
  { label: 'Recall (%50)', value: '%82,27', note: 'Başarısızların yakalanma oranı', icon: Target },
  { label: 'Precision@%20', value: '%81,76', note: 'En riskli %20 grubun gerçek oranı', icon: TrendingUp },
];

export default function Performance({ theme }: { theme: 'light' | 'dark' }) {
  const dark = theme === 'dark';
  const gridColor = dark ? '#283a51' : '#e9eef5';
  const labelColor = dark ? '#b4c4db' : '#64748b';
  const tooltipStyle = {
    borderRadius: 12,
    background: dark ? '#152740' : '#fff',
    border: '1px solid ' + gridColor,
    color: dark ? '#f8fafc' : '#0f172a',
  };
  return <div>
    <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-700 dark:text-sky-400">MODEL DOĞRULAMASI</p>
    <h1 className="text-2xl font-semibold text-slate-900 dark:text-white sm:text-3xl">Model Performansı</h1>
    <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500 dark:text-slate-400">
      Modellerin eğitim verisindeki iç içe çapraz doğrulama sonuçları. Bunlar geçmişte değerlendirilmiş aynı
      veri setinin keşifsel sonuçlarıdır, bağımsız harici test değildir.
    </p>

    <div className="mt-7 grid gap-4 md:grid-cols-3">
      {stats.map(item => {
        const Icon = item.icon;
        return <section className="card-surface p-5" key={item.label}>
          <div className="flex items-center justify-between"><p className="text-sm text-slate-500 dark:text-slate-400">{item.label}</p>
            <Icon size={19} className="text-blue-700 dark:text-sky-400" /></div>
          <p className="mt-5 text-3xl font-semibold text-slate-900 dark:text-white">{item.value}</p>
          <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{item.note}</p>
        </section>;
      })}
    </div>

    <div className="mt-5 grid gap-5 xl:grid-cols-2">
      <section className="card-surface p-5 sm:p-6">
        <h2 className="font-semibold text-slate-900 dark:text-white">Dış değerlendirme katlarında AUC</h2>
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Her katta algoritma iç CV ile yeniden seçildi</p>
        <div className="mt-6 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={FOLDS}>
              <CartesianGrid stroke={gridColor} strokeDasharray="3 4" vertical={false} />
              <XAxis dataKey="fold" tick={{ fontSize: 11, fill: labelColor }} />
              <YAxis type="number" domain={[0, 1]} tick={{ fontSize: 11, fill: labelColor }} />
              <Tooltip contentStyle={tooltipStyle} formatter={(value: number) => [Number(value).toFixed(4), 'ROC-AUC']} />
              <Bar dataKey="auc" name="ROC-AUC" fill="#4283bd" radius={[6, 6, 0, 0]} maxBarSize={46} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
      <section className="card-surface p-5 sm:p-6">
        <h2 className="font-semibold text-slate-900 dark:text-white">En riskli %20 grubun isabeti</h2>
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Precision@20 · genel başarısızlık oranı ≈ %59,3</p>
        <div className="mt-6 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={FOLDS}>
              <CartesianGrid stroke={gridColor} strokeDasharray="3 4" vertical={false} />
              <XAxis dataKey="fold" tick={{ fontSize: 11, fill: labelColor }} />
              <YAxis type="number" domain={[0, 1]} tick={{ fontSize: 11, fill: labelColor }} />
              <Tooltip contentStyle={tooltipStyle} formatter={(value: number) => [String((Number(value) * 100).toFixed(1)) + '%', 'Precision@20']} />
              <Bar dataKey="precision20" name="Precision@20" fill="#18a48b" radius={[6, 6, 0, 0]} maxBarSize={46} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>

    <section className="card-surface mt-5 p-5 sm:p-6">
      <h2 className="font-semibold text-slate-900 dark:text-white">Sabit aday algoritmaların CV karşılaştırması</h2>
      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
        Eğitim kümesinde 5 katlı CV. Bu ayrı deneyin skorlarını yukarıdaki nested CV sonucuyla karıştırmayın.
      </p>
      <div className="mt-5 space-y-4">
        {INDIVIDUAL.map(item => <div key={item.model} className="flex items-center gap-4">
          <span className="w-36 shrink-0 text-xs font-medium text-slate-600 dark:text-slate-300">{item.model}</span>
          <div className="h-3 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
            <div className="h-full rounded-full bg-blue-600 dark:bg-sky-500" style={{ width: (item.auc * 100) + '%' }} />
          </div>
          <strong className="w-16 text-right text-sm font-semibold text-slate-900 dark:text-white">{item.auc.toFixed(3)}</strong>
        </div>)}
      </div>
      <p className="mt-5 text-xs text-slate-500 dark:text-slate-400">
        Bu modellerin arasındaki fark çok küçüktür; Random Forest'ın kesin üstünlüğü gösterilmemiştir.
      </p>
    </section>

    <section className="mt-5 flex gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-5 dark:border-amber-500/20 dark:bg-amber-500/10">
      <CircleAlert size={21} className="mt-0.5 shrink-0 text-amber-700 dark:text-amber-300" />
      <div className="text-sm leading-6 text-amber-900 dark:text-amber-200">
        <strong>Metodoloji sınırı:</strong> Geçmişte aynı veri setinde özellik/algoritma seçimleri yapıldı. İç içe CV
        bu geçmiş etkileri tamamen ortadan kaldırmaz. Gerçek kurumsal kullanımdan önce yeni dönem veya farklı
        üniversite verisinde bağımsız doğrulama gereklidir.
        <a className="ml-1 inline-flex items-center gap-1 font-semibold underline"
          href="https://github.com/burakkalindamarr/basari-riski/blob/main/experiments/results/NESTED_CV_REPORT.md"
          target="_blank" rel="noreferrer">Ayrıntılı rapor <ArrowUpRight size={14}/></a>
      </div>
    </section>
  </div>;
}
