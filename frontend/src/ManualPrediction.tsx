import { useEffect, useState } from 'react';
import { AlertTriangle, ArrowRight, CheckCircle2, Loader2, RotateCcw, Save } from 'lucide-react';
import { getSchema, predictOne } from './api';
import type { FormSchema, PredictionResult } from './api';
import Explain from './Explain';

const formatted = (v: number) => '%' + new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(v);
const groups = [
  { title: 'Kayıt ve başvuru', cols: ['Application mode', 'Application order', 'Course', 'Daytime/evening attendance', 'Admission grade'] },
  { title: 'Akademik geçmiş', cols: ['Previous qualification', 'Previous qualification (grade)'] },
  { title: 'Öğrenci ve aile bilgileri', cols: ['Age at enrollment', 'Gender', 'Marital status', 'Displaced', 'Scholarship holder',
    "Mother's qualification", "Father's qualification", "Mother's occupation", "Father's occupation"] },
];

export default function ManualPrediction() {
  const [schema, setSchema] = useState<FormSchema | null>(null);
  const [values, setValues] = useState<Record<string, number>>({});
  const [studentId, setStudentId] = useState('MANUEL-001');
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    let cancelled = false;
    getSchema()
      .then(data => {
        if (cancelled) return;
        setSchema(data);
        setValues(Object.fromEntries(data.fields.map(field => [field.name, field.default])));
      })
      .catch(e => { if (!cancelled) setError(e instanceof Error ? e.message : 'Giriş şeması yüklenemedi.'); });
    return () => { cancelled = true; };
  }, []);

  function reset() {
    if (!schema) return;
    setValues(Object.fromEntries(schema.fields.map(field => [field.name, field.default])));
    setStudentId('MANUEL-001'); setResult(null); setError('');
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!schema || pending) return;
    setPending(true); setError(''); setResult(null);
    try {
      const response = await predictOne(values, studentId.trim() || 'MANUEL-001');
      setResult(response);
    } catch (e) { setError(e instanceof Error ? e.message : 'Tahmin hesaplanamadı.'); }
    finally { setPending(false); }
  }

  return <div>
    <div className="mb-7">
      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-700 dark:text-sky-400">ETKİLEŞİMLİ TAHMİN</p>
      <h1 className="text-2xl font-semibold tracking-tight text-slate-900 dark:text-white sm:text-3xl">Tek Öğrenci Analizi</h1>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500 dark:text-slate-400">
        Dönem başındaki 16 bilgiyi değiştirerek gerçek modelden tahmini risk ve SHAP açıklamalarını alın.
        Başlangıç alanları veri setinden alınmış bir örnek öğrenci ile doldurulur.
      </p>
    </div>
    {error && <div role="alert" className="mb-5 flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950/30 dark:text-rose-200"><AlertTriangle size={18}/>{error}</div>}
    {!schema ? <div className="card-surface flex min-h-56 items-center justify-center gap-3 text-sm text-slate-500">
      <Loader2 size={19} className="animate-spin" /> Giriş seçenekleri yükleniyor...
    </div> : <div className="grid gap-5 xl:grid-cols-[1.35fr_0.85fr]">
      <form onSubmit={submit} className="space-y-5">
        <section className="card-surface p-5 sm:p-6">
          <label className="mb-2 block text-sm font-semibold text-slate-800 dark:text-white" htmlFor="manual-id">Öğrenci kodu</label>
          <input className="input-field max-w-xs" maxLength={64} id="manual-id" value={studentId} onChange={e => setStudentId(e.target.value)} />
          <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">Gerçek öğrenci numarası yerine örnek kod kullanın.</p>
        </section>
        {groups.map(group => <section className="card-surface p-5 sm:p-6" key={group.title}>
          <h2 className="mb-5 font-semibold text-slate-900 dark:text-white">{group.title}</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {group.cols.map(name => {
              const field = schema.fields.find(f => f.name === name);
              if (!field) return null;
              return <label key={name} className="block">
                <span className="mb-1.5 block text-xs font-semibold text-slate-600 dark:text-slate-300">{field.label}</span>
                {field.kind === 'select' ? <select className="input-field" value={values[name] ?? field.default} required
                  onChange={e => { setValues(v => ({ ...v, [name]: Number(e.target.value) })); setResult(null); }}>
                  {(field.options ?? []).map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select> : <input type="number" className="input-field" value={values[name] ?? field.default} step="any"
                  min={field.min} max={field.max} required
                  onChange={e => { setValues(v => ({ ...v, [name]: Number(e.target.value) })); setResult(null); }} />}
              </label>;
            })}
          </div>
        </section>)}
        <div className="flex flex-wrap items-center gap-3">
          <button type="submit" disabled={pending} className="btn-primary min-w-40">
            {pending ? <Loader2 size={16} className="animate-spin" /> : <ArrowRight size={16} />}
            {pending ? 'Hesaplanıyor...' : 'Riski hesapla'}
          </button>
          <button type="button" onClick={reset} className="btn-secondary"><RotateCcw size={16} /> Örnek değerlere dön</button>
        </div>
      </form>

      <div className="space-y-5 xl:sticky xl:top-24 xl:self-start">
        {result ? <section className="card-surface p-5 sm:p-6" aria-live="polite">
          <div className="flex items-center gap-2 text-sm font-semibold text-emerald-700 dark:text-emerald-300">
            <CheckCircle2 size={18} /> Gerçek model tahmini
          </div>
          <div className="my-6 rounded-2xl bg-slate-50 px-5 py-8 text-center dark:bg-slate-800/70">
            <p className="text-xs uppercase tracking-wide text-slate-500">Tahmini başarısızlık riski</p>
            <div className="mt-2 text-5xl font-semibold tracking-tight text-slate-900 dark:text-white">{formatted(result.students[0].risk)}</div>
            <div className="mt-4 text-sm text-slate-500 dark:text-slate-400">Model: {result.algorithm}</div>
          </div>
          <Explain explanation={result.students[0].explanation} />
        </section> : <section className="card-surface p-6">
          <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-sky-400"><Save size={20} /></div>
          <h2 className="font-semibold text-slate-900 dark:text-white">Analiz için hazır</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">
            Alanları değiştirip "Riski hesapla" dediğinizde sistem tahmini ve hangi değişkenlerin riski artırıp azalttığını gösterecek.
          </p>
        </section>}
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5 text-xs leading-6 text-amber-900 dark:border-amber-500/20 dark:bg-amber-500/10 dark:text-amber-200">
          <div className="mb-2 flex items-center gap-2 font-semibold"><AlertTriangle size={17} /> Bilimsel sınırlılık</div>
          Bu değerler yalnızca araştırma amaçlıdır. Her öğrenci profili eğitim dağılımını temsil etmeyebilir.
          Kategorik değerler kaynak veri setinin kod sistemini kullanır, yüzde değerleri karar garantisi değildir.
          Gerçek kişisel öğrenci bilgileri girmeyin.
        </div>
      </div>
    </div>}
  </div>;
}
