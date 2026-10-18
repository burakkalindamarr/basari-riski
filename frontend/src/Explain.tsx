import type { Explanation } from './api';

export default function Explain({ explanation }: { explanation: Explanation }) {
  const entries = [
    ...explanation.increases.map((entry) => ({ ...entry, sign: 'increase' as const })),
    ...explanation.decreases.map((entry) => ({ ...entry, sign: 'decrease' as const })),
  ];
  const maximum = Math.max(0.05, ...entries.map(e => Math.abs(e.contribution)));
  return <section aria-label="SHAP faktör açıklamaları" className="space-y-5">
    <div>
      <h3 className="font-semibold text-slate-900 dark:text-white">Tahmini etkileyen faktörler</h3>
      <p className="mt-1.5 text-xs leading-5 text-slate-500 dark:text-slate-400">
        SHAP, modelin bu öğrenci için yaptığı tahmini açıklıyor. Kırmızı risk artıran, yeşil risk azaltan etkileri gösterir.
      </p>
    </div>
    {entries.length ? <div className="space-y-3">
      {entries.map(item => {
        const positive = item.sign === 'increase';
        const width = Math.max(2, 100 * Math.abs(item.contribution) / maximum);
        return <div key={item.feature}>
          <div className="mb-1.5 flex items-center justify-between gap-4 text-xs">
            <span className="font-medium text-slate-700 dark:text-slate-200">{item.label}</span>
            <span className={'whitespace-nowrap font-semibold ' + (positive ? 'text-rose-700 dark:text-rose-300' : 'text-emerald-700 dark:text-emerald-300')}>
              {positive ? '+' : ''}{item.contribution.toFixed(3)}
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
            <div className={'h-full rounded-full ' + (positive ? 'bg-rose-500' : 'bg-emerald-500')} style={{ width: width + '%' }} />
          </div>
        </div>;
      })}
    </div> : <p className="text-sm text-slate-500">Belirgin bir faktör katkısı bulunamadı.</p>}
    <div className="rounded-xl border border-blue-100 bg-blue-50/50 p-3 text-xs leading-5 text-slate-600 dark:border-blue-800/40 dark:bg-blue-900/10 dark:text-slate-300">
      <strong className="text-slate-800 dark:text-white">Birim: log-odds.</strong> Bu sayılar yüzde puanı değildir ve faktörlerin neden-sonuç etkisini kanıtlamaz.
      Modelin tüm faktörleri birlikte değerlendirerek verdiği olasılık, üstte görülen risk yüzdesidir.
    </div>
  </section>;
}
