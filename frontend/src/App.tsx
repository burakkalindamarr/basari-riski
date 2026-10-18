import { useEffect, useMemo, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import {
  Activity, AlertTriangle, ArrowRight, BarChart3, BookOpen, CheckCircle2,
  ChevronLeft, ChevronRight, Database, Download, FileSpreadsheet, GraduationCap,
  LayoutDashboard, Loader2, Menu, Moon, RotateCcw, Search, ShieldCheck,
  Sun, Upload, Users, X,
} from 'lucide-react';
import {
  Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts';
import { analyzeCsv, downloadCsv, getDemo, REQUIRED_COLUMNS } from './api';
import type { PredictionResult, RiskLevel, Student } from './api';
import Explain from './Explain';
import ManualPrediction from './ManualPrediction';
import Performance from './Performance';

type Page = 'dashboard' | 'students' | 'manual' | 'performance' | 'method';
type RiskFilter = 'all' | RiskLevel;
type Theme = 'light' | 'dark';
const navItems: { id: Page; title: string; icon: typeof LayoutDashboard }[] = [
  { id: 'dashboard', title: 'Genel Bakış', icon: LayoutDashboard },
  { id: 'students', title: 'Öğrenci Analizi', icon: Users },
  { id: 'manual', title: 'Tek Öğrenci Tahmini', icon: FileSpreadsheet },
  { id: 'performance', title: 'Model Performansı', icon: BarChart3 },
  { id: 'method', title: 'Model ve Yöntem', icon: BookOpen },
];
const category = {
  low: { label: 'Düşük', text: 'text-emerald-700 dark:text-emerald-300', bg: 'bg-emerald-50 dark:bg-emerald-500/10' },
  medium: { label: 'Orta', text: 'text-amber-700 dark:text-amber-300', bg: 'bg-amber-50 dark:bg-amber-500/10' },
  high: { label: 'Yüksek', text: 'text-rose-700 dark:text-rose-300', bg: 'bg-rose-50 dark:bg-rose-500/10' },
};
const colors = { low: '#10B981', medium: '#F59E0B', high: '#F87171' };
const number = new Intl.NumberFormat('tr-TR');
const pct = (value: number) => '%' + new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 1, minimumFractionDigits: 1 }).format(value);

function RiskBadge({ level }: { level: RiskLevel }) {
  const style = category[level];
  return <span className={'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ' + style.text + ' ' + style.bg}>
    <span className="h-1.5 w-1.5 rounded-full bg-current" />{style.label}
  </span>;
}

function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <section className={'card-surface ' + className}>{children}</section>;
}

function MetricCard({ label, value, info, icon }: { label: string; value: string; info: string; icon: ReactNode }) {
  return <Card className="p-5 sm:p-6">
    <div className="mb-5 flex items-center justify-between">
      <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</span>
      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-700 dark:bg-blue-400/10 dark:text-blue-300">{icon}</span>
    </div>
    <div className="text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">{value}</div>
    <p className="mt-2 text-xs leading-5 text-slate-500 dark:text-slate-400">{info}</p>
  </Card>;
}

function PageTitle({ label, title, subtitle }: { label: string; title: string; subtitle: string }) {
  return <div className="mb-7">
    <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-700 dark:text-sky-400">{label}</p>
    <h1 className="text-2xl font-semibold tracking-tight text-slate-900 dark:text-white sm:text-3xl">{title}</h1>
    <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500 dark:text-slate-400">{subtitle}</p>
  </div>;
}

function Dashboard({ data, theme, showStudents }: { data: PredictionResult; theme: Theme; showStudents: () => void }) {
  const distribution = [
    { name: 'Düşük', value: data.summary.low, key: 'low' },
    { name: 'Orta', value: data.summary.medium, key: 'medium' },
    { name: 'Yüksek', value: data.summary.high, key: 'high' },
  ];
  const top = data.students.slice(0, Math.ceil(data.students.length * 0.2));
  const departments = [...data.courses].sort((a, b) => b.count - a.count).slice(0, 7);
  const gridColor = theme === 'dark' ? '#263650' : '#e9edf4';
  const axisColor = theme === 'dark' ? '#99abc2' : '#64748b';
  return <>
    <PageTitle label="ANALİTİK PANEL" title="Genel Bakış"
      subtitle="Dönem başında bilinen verilerle tahmin edilen başarısızlık risklerinin kurumsal özeti." />

    <div className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard label="Analiz edilen" value={number.format(data.summary.count)} info="Toplam öğrenci kaydı" icon={<Users size={18} />} />
      <MetricCard label="Yüksek risk" value={number.format(data.summary.high)} info="Örnek eşik: %75 ve üzeri" icon={<AlertTriangle size={18} />} />
      <MetricCard label="Ortalama tahmin" value={pct(data.summary.average_risk)} info="Modelin ortalama risk tahmini" icon={<Activity size={18} />} />
      <MetricCard label="Öncelikli %20" value={number.format(top.length)} info="Risk skoruna göre ilk sıradakiler" icon={<BarChart3 size={18} />} />
    </div>

    <div className="grid gap-5 xl:grid-cols-[0.92fr_1.08fr]">
      <Card className="p-5 sm:p-6">
        <div className="mb-6">
          <h2 className="font-semibold text-slate-900 dark:text-white">Risk dağılımı</h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Gösterim amaçlı %50 / %75 eşikleri</p>
        </div>
        <div className="flex flex-col items-center gap-4 sm:flex-row">
          <div className="relative h-56 w-full sm:w-3/5">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={distribution} dataKey="value" nameKey="name" innerRadius={67} outerRadius={96} paddingAngle={3} stroke="none">
                  {distribution.map(item => <Cell key={item.key} fill={colors[item.key as RiskLevel]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: theme === 'dark' ? '#182740' : '#fff', borderColor: gridColor, color: theme === 'dark' ? '#f8fafc' : '#0f172a', borderRadius: 10 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-2xl font-bold text-slate-900 dark:text-white">{number.format(data.summary.count)}</span>
              <span className="text-xs text-slate-500 dark:text-slate-400">öğrenci</span>
            </div>
          </div>
          <div className="w-full space-y-3 sm:w-2/5">
            {distribution.map(item => <div key={item.key} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full" style={{ background: colors[item.key as RiskLevel] }} />
                <span className="text-slate-600 dark:text-slate-300">{item.name}</span></div>
              <strong className="font-semibold text-slate-900 dark:text-white">{number.format(item.value)}</strong>
            </div>)}
          </div>
        </div>
      </Card>
      <Card className="p-5 sm:p-6">
        <div className="mb-5">
          <h2 className="font-semibold text-slate-900 dark:text-white">Bölümlere göre ortalama risk</h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">En çok öğrencisi olan 7 bölüm · tahmini risk (%)</p>
        </div>
        <div className="h-[276px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={departments} margin={{ top: 0, right: 18, bottom: 0, left: 16 }}>
              <CartesianGrid stroke={gridColor} strokeDasharray="3 4" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: axisColor }} unit="%" />
              <YAxis type="category" dataKey="course" width={105} tick={{ fontSize: 11, fill: axisColor }} tickFormatter={v => v.length > 17 ? v.slice(0, 17) + '…' : v} />
              <Tooltip formatter={(value: number) => [pct(value), 'Ortalama risk']} contentStyle={{ background: theme === 'dark' ? '#182740' : '#fff', borderColor: gridColor, color: theme === 'dark' ? '#fff' : '#0f172a', borderRadius: 10 }} />
              <Bar dataKey="average_risk" fill="#367bbb" radius={[0, 5, 5, 0]} maxBarSize={22} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>

    <Card className="mt-5 overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 p-5 dark:border-slate-800 sm:px-6">
        <div><h2 className="font-semibold text-slate-900 dark:text-white">Öncelikli öğrenciler</h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Tahmin edilen risk skoruna göre ilk 5 kayıt</p></div>
        <button type="button" className="inline-flex items-center gap-1.5 text-sm font-semibold text-blue-700 hover:text-blue-900 dark:text-sky-400 dark:hover:text-sky-300" onClick={showStudents}>
          Tümünü görüntüle <ArrowRight size={15} />
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="table-base">
          <thead><tr><th>Sıra</th><th>Öğrenci</th><th>Bölüm</th><th>Tahmini risk</th><th>Risk seviyesi</th></tr></thead>
          <tbody>{data.students.slice(0, 5).map(s => <tr key={s.id}>
            <td>#{s.rank}</td><td className="font-semibold">{s.id}</td><td>{s.course}</td>
            <td className="font-semibold">{pct(s.risk)}</td><td><RiskBadge level={s.level} /></td>
          </tr>)}</tbody>
        </table>
      </div>
    </Card>
  </>;
}

function Students({ data }: { data: PredictionResult }) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<RiskFilter>('all');
  const [page, setPage] = useState(0);
  const [selected, setSelected] = useState<Student | null>(null);
  const filtered = useMemo(() => data.students.filter(s =>
    (filter === 'all' || s.level === filter) &&
    (s.id.toLocaleLowerCase('tr-TR').includes(search.toLocaleLowerCase('tr-TR')) ||
      s.course.toLocaleLowerCase('tr-TR').includes(search.toLocaleLowerCase('tr-TR')))
  ), [data, filter, search]);
  const totalPages = Math.max(1, Math.ceil(filtered.length / 20));
  const visible = filtered.slice(page * 20, page * 20 + 20);

  function exportRows() {
    downloadCsv('akademik-risk-analizi.csv', [
      ['Ogrenci No', 'Bolum', 'Tahmini Risk (%)', 'Seviye'],
      ...filtered.map(s => [s.id, s.course, s.risk, category[s.level].label]),
    ]);
  }
  return <>
    <PageTitle label="ÖĞRENCİ YÖNETİMİ" title="Öğrenci Analizi"
      subtitle="Öğrencileri tahmini risk sırasına göre inceleyin. Bu liste kesin sonuç değil, destek planlamasına yardımcı bir önceliklendirme aracıdır." />
    <Card className="overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-slate-100 p-5 dark:border-slate-800 md:flex-row md:items-center md:justify-between sm:px-6">
        <div className="relative w-full md:max-w-sm">
          <Search size={17} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input aria-label="Öğrenci veya bölüm ara" placeholder="Öğrenci no veya bölüm ara..."
            value={search} onChange={e => { setSearch(e.target.value); setPage(0); }} className="input-field pl-10" />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select aria-label="Risk filtresi" className="input-field w-auto min-w-36" value={filter}
            onChange={e => { setFilter(e.target.value as RiskFilter); setPage(0); }}>
            <option value="all">Tüm riskler</option><option value="high">Yüksek risk</option>
            <option value="medium">Orta risk</option><option value="low">Düşük risk</option>
          </select>
          <button className="btn-secondary" type="button" onClick={exportRows}>
            <Download size={16} /> CSV indir
          </button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="table-base"><thead><tr><th>Sıra</th><th>Öğrenci</th><th>Bölüm</th><th>Risk (%)</th><th>Seviye</th><th></th></tr></thead>
          <tbody>{visible.map(s => <tr key={s.id}>
            <td>#{s.rank}</td><td className="font-semibold">{s.id}</td><td>{s.course}</td>
            <td className="min-w-40"><div className="flex items-center gap-3">
              <span className="w-14 font-semibold">{pct(s.risk)}</span>
              <div className="h-1.5 w-20 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                <div className="h-full rounded-full" style={{ width: String(s.risk) + '%', backgroundColor: colors[s.level] }} />
              </div></div></td>
            <td><RiskBadge level={s.level} /></td>
            <td><button className="rounded-lg p-2 text-blue-700 hover:bg-blue-50 dark:text-sky-400 dark:hover:bg-slate-800"
              aria-label={s.id + ' kaydının detayını göster'} type="button" onClick={() => setSelected(s)}><ArrowRight size={16} /></button></td>
          </tr>)}</tbody>
        </table>
        {visible.length === 0 && <div className="p-10 text-center text-sm text-slate-500">Bu filtreyle eşleşen öğrenci bulunamadı.</div>}
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 px-5 py-4 text-xs text-slate-500 dark:border-slate-800 sm:px-6">
        <span>{number.format(filtered.length)} sonuç · Sayfa {page + 1}/{totalPages}</span>
        <div className="flex gap-2">
          <button type="button" aria-label="Önceki sayfa" disabled={page === 0} className="page-button" onClick={() => setPage(p => Math.max(0, p - 1))}><ChevronLeft size={18} /></button>
          <button type="button" aria-label="Sonraki sayfa" disabled={page + 1 >= totalPages} className="page-button" onClick={() => setPage(p => p + 1)}><ChevronRight size={18} /></button>
        </div>
      </div>
    </Card>
    {selected && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4" role="presentation" onMouseDown={e => { if (e.target === e.currentTarget) setSelected(null); }}>
      <div role="dialog" aria-modal="true" aria-labelledby="student-detail-title" className="card-surface w-full max-w-md p-6 shadow-2xl">
        <div className="flex items-start justify-between">
          <div><p className="text-xs font-semibold uppercase tracking-widest text-blue-700 dark:text-sky-400">Öğrenci Detayı</p>
            <h2 id="student-detail-title" className="mt-2 text-xl font-semibold text-slate-900 dark:text-white">{selected.id}</h2></div>
          <button type="button" aria-label="Detayı kapat" onClick={() => setSelected(null)} className="page-button"><X size={18} /></button>
        </div>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{selected.course}</p>
        <div className="my-6 rounded-xl bg-slate-50 p-6 text-center dark:bg-slate-800/60">
          <div className="text-4xl font-semibold text-slate-900 dark:text-white">{pct(selected.risk)}</div>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Tahmini başarısızlık olasılığı</p>
          <div className="mt-4"><RiskBadge level={selected.level} /></div>
        </div>
        <Explain explanation={selected.explanation} />
      </div>
    </div>}
  </>;
}

function Method({ algorithm, features }: { algorithm: string; features: number }) {
  return <>
    <PageTitle label="ŞEFFAFLIK VE BİLİMSEL YÖNTEM" title="Model ve Yöntem"
      subtitle="Modelin neyi tahmin ettiğini, hangi varsayımlara dayandığını ve henüz neleri kanıtlamadığını açıkça gösteriyoruz." />
    <div className="grid gap-5 lg:grid-cols-3">
      <MetricCard label="Canlı algoritma" value="GB" info={algorithm + ' · mevcut dağıtım'} icon={<Activity size={18} />} />
      <MetricCard label="Girdi değişkeni" value={String(features)} info="Dönem başı kayıt özellikleri" icon={<FileSpreadsheet size={18} />} />
      <MetricCard label="Nested CV AUC" value="0,712" info="Geliştirme süreci · tüm adayların seçimi" icon={<BarChart3 size={18} />} />
    </div>
    <div className="mt-5 grid gap-5 lg:grid-cols-2">
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Tahminin kapsamı</h2>
        <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
          Model, birinci dönemde kayıt olunan derslerden <strong>en az birinden kalma olasılığını</strong> tahmin eder.
          Mezuniyeti, okuldan ayrılmayı veya öğrencinin yeteneğini ölçmez. Ders sonuçları ve dönem sonu notları girdi olarak kullanılmaz.
        </p>
        <div className="mt-5 space-y-3 text-sm text-slate-600 dark:text-slate-300">
          <div className="flex items-center gap-2"><CheckCircle2 size={16} className="text-emerald-600" /> Kategorik değişkenlere OneHotEncoder</div>
          <div className="flex items-center gap-2"><CheckCircle2 size={16} className="text-emerald-600" /> Sayısal değişkenlere StandardScaler</div>
          <div className="flex items-center gap-2"><CheckCircle2 size={16} className="text-emerald-600" /> Pipeline içinde eğitim ve dönüşüm</div>
        </div>
      </Card>
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Doğrulama sonuçları</h2>
        <p className="mt-2 text-xs leading-5 text-slate-500 dark:text-slate-400">
          Aşağıdaki metrikler algoritma seçimini içeren nested çapraz doğrulamaya aittir; canlı modelin bağımsız test performansı değildir.
        </p>
        <div className="mt-5 space-y-4">
          {[['ROC-AUC', '0,7116'], ['Recall · %50 eşik', '%82,27'], ['Precision@en riskli %20', '%81,76'], ['Brier skoru', '0,2092']].map(([key, value]) =>
            <div key={key} className="flex items-center justify-between border-b border-slate-100 pb-3 text-sm last:border-b-0 dark:border-slate-800">
              <span className="text-slate-500 dark:text-slate-400">{key}</span>
              <strong className="font-semibold text-slate-900 dark:text-white">{value}</strong>
            </div>)}
        </div>
      </Card>
    </div>
    <Card className="mt-5 p-6">
      <div className="flex gap-3"><ShieldCheck className="mt-0.5 shrink-0 text-blue-700 dark:text-sky-400" size={22} />
        <div><h2 className="font-semibold text-slate-900 dark:text-white">Araştırma prototipi · kullanım sınırları</h2>
          <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
            Veri Portekiz kaynaklıdır. Türkiye'deki üniversitelerde bağımsız doğrulama yapılmadı. Eski test kümesi geçmişte model geliştirmede kullanıldığı için bağımsız son test değildir.
            Modelin sonuçları öğrenci hakkında otomatik akademik karar vermek için kullanılmamalı.
            Yanlış alarm, demografik yanlılık ve kişisel verilerin korunması konularında kurum onayı ve ek çalışma gereklidir.
          </p>
          <a className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-blue-700 hover:underline dark:text-sky-400"
            href="https://github.com/burakkalindamarr/basari-riski/blob/main/docs/MODEL_CARD.md" target="_blank" rel="noreferrer">Model kartını GitHub'da incele <ArrowRight size={15} /></a>
        </div>
      </div>
    </Card>
  </>;
}

export default function App() {
  const [theme, setTheme] = useState<Theme>(() => {
    const previous = localStorage.getItem('risk-theme');
    return previous === 'dark' || previous === 'light'
      ? previous : window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });
  const [page, setPage] = useState<Page>('dashboard');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [data, setData] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('risk-theme', theme);
  }, [theme]);

  useEffect(() => {
    const controller = new AbortController();
    getDemo(controller.signal).then(result => { setData(result); setError(null); })
      .catch(err => { if (!controller.signal.aborted) setError(err instanceof Error ? err.message : 'Örnek veri yüklenemedi.'); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, []);

  async function loadDemo() {
    setLoading(true);
    setError(null);
    try { setData(await getDemo()); setPage('dashboard'); }
    catch (err) { setError(err instanceof Error ? err.message : 'Örnek veri alınamadı.'); }
    finally { setLoading(false); }
  }

  async function upload(file?: File) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.csv')) { setError('Yalnızca .csv dosyası yükleyebilirsiniz.'); return; }
    if (file.size > 2 * 1024 * 1024) { setError('CSV dosyası en fazla 2 MB olabilir.'); return; }
    setUploading(true); setError(null);
    try { const result = await analyzeCsv(file); setData(result); setPage('dashboard'); }
    catch (err) { setError(err instanceof Error ? err.message : 'CSV işlenemedi.'); }
    finally { setUploading(false); if (fileRef.current) fileRef.current.value = ''; }
  }

  const activeName = navItems.find(x => x.id === page)?.title ?? 'Genel Bakış';
  return <div className="min-h-screen bg-[#f5f7fb] text-slate-800 transition-colors duration-200 dark:bg-[#0a1220] dark:text-slate-200">
    {mobileOpen && <button type="button" aria-label="Menüyü kapat" className="fixed inset-0 z-30 bg-slate-950/60 lg:hidden" onClick={() => setMobileOpen(false)} />}
    <aside className={'sidebar fixed inset-y-0 left-0 z-40 flex w-[256px] flex-col px-4 py-6 text-white transition-transform duration-200 lg:translate-x-0 ' + (mobileOpen ? 'translate-x-0' : '-translate-x-full')}>
      <div className="flex items-center gap-3 px-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-white/15 bg-white/10"><GraduationCap size={24} strokeWidth={1.8} /></div>
        <div><p className="text-base font-semibold leading-5 tracking-tight">Akademik İçgörü</p><span className="text-[11px] tracking-wide text-blue-200/70">ERKEN UYARI SİSTEMİ</span></div>
      </div>
      <div className="mt-12 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-blue-200/55">Çalışma Alanı</div>
      <nav className="mt-4 space-y-1" aria-label="Ana menü">
        {navItems.map(item => {
          const Icon = item.icon;
          return <button key={item.id} type="button" onClick={() => { setPage(item.id); setMobileOpen(false); }}
            className={'sidebar-link ' + (page === item.id ? 'sidebar-link-active' : '')}>
            <Icon size={18} strokeWidth={1.8} />{item.title}
          </button>;
        })}
      </nav>
      <div className="mt-auto rounded-2xl border border-white/10 bg-white/5 p-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-sky-200"><ShieldCheck size={16} /> Araştırma modu</div>
        <p className="mt-2 text-xs leading-5 text-blue-100/65">Kararlar için değil, öğrenci destek önceliklendirmesini araştırmak için.</p>
      </div>
      <div className="mt-5 px-3 text-[11px] text-blue-200/50">Prototip sürüm 0.1</div>
    </aside>
    <div className="min-h-screen lg:pl-[256px]">
      <header className="sticky top-0 z-20 flex h-[76px] items-center justify-between border-b border-slate-200/70 bg-white/90 px-5 backdrop-blur-lg dark:border-slate-800 dark:bg-[#101a2c]/90 sm:px-8">
        <div className="flex items-center gap-3">
          <button className="page-button lg:hidden" aria-label="Menüyü aç" type="button" onClick={() => setMobileOpen(true)}><Menu size={21} /></button>
          <div className="hidden items-center gap-2 text-sm sm:flex"><span className="text-slate-400">Platform</span><span className="text-slate-300 dark:text-slate-700">/</span><span className="font-semibold text-slate-700 dark:text-slate-200">{activeName}</span></div>
          <span className="font-semibold text-slate-800 dark:text-white sm:hidden">{activeName}</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-[11px] font-semibold text-emerald-800 dark:border-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-300 sm:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Gerçek ML modeli
          </div>
          <button className="page-button" type="button" aria-label={theme === 'light' ? 'Koyu temayı aç' : 'Açık temayı aç'}
            onClick={() => setTheme(t => t === 'light' ? 'dark' : 'light')}>{theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}</button>
        </div>
      </header>
      <main className="mx-auto w-full max-w-[1480px] px-4 pb-12 pt-8 sm:px-8 sm:pt-10">
        <div className="mb-7 flex flex-col gap-4 rounded-2xl border border-[#dbe8f7] bg-gradient-to-r from-[#eaf2fb] to-[#f9fbff] p-4 dark:border-blue-800/30 dark:from-[#142844] dark:to-[#102036] sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white text-blue-700 shadow-sm dark:bg-blue-400/10 dark:text-blue-300"><Database size={18} /></div>
            <div>
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{data?.source === 'upload' ? 'CSV analizi' : 'Örnek veriyle keşfet'}</p>
              <p className="mt-1 text-xs leading-5 text-slate-600 dark:text-slate-400">
                {data?.source === 'upload' ? 'Yüklediğiniz dosya bu oturumda analiz edildi.' : 'Demo verileri eski çalışma kümesinden alınmıştır; bağımsız test değildir.'}
                {' '}Gerçek kişisel öğrenci bilgileri yüklemeyin.
              </p>
            </div>
          </div>
          <div className="flex shrink-0 flex-wrap items-center gap-2">
            <button type="button" className="btn-secondary" onClick={loadDemo} disabled={loading || uploading}><RotateCcw size={15} /> Örnek veri</button>
            <button type="button" className="btn-primary" disabled={uploading || loading} onClick={() => fileRef.current?.click()}>
              {uploading ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />} CSV yükle
            </button>
            <input ref={fileRef} type="file" accept=".csv,text/csv" className="hidden" onChange={event => upload(event.target.files?.[0])} aria-label="Öğrenci CSV dosyası" />
          </div>
        </div>
        {error && <div role="alert" className="mb-6 flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200">
          <AlertTriangle size={19} className="shrink-0" /><div className="flex-1">{error}</div>
          <button type="button" aria-label="Uyarıyı kapat" onClick={() => setError(null)}><X size={17} /></button>
        </div>}
        {loading ? <div className="card-surface flex min-h-[360px] flex-col items-center justify-center gap-4">
          <Loader2 className="animate-spin text-blue-700 dark:text-sky-400" size={30} />
          <p className="text-sm text-slate-500 dark:text-slate-400">Model tahminleri yükleniyor...</p>
        </div> : data ? <>
          {page === 'dashboard' && <Dashboard data={data} theme={theme} showStudents={() => setPage('students')} />}
          {page === 'students' && <Students key={data.source + ':' + data.summary.count} data={data} />}
          {page === 'manual' && <ManualPrediction />}
          {page === 'performance' && <Performance theme={theme} />}
          {page === 'method' && <Method algorithm={data.algorithm} features={data.features} />}
        </> : <Card className="py-20 text-center">
          <AlertTriangle className="mx-auto text-amber-500" size={30} />
          <h2 className="mt-4 font-semibold">Veriler yüklenemedi</h2>
          <p className="mt-2 text-sm text-slate-500">API bağlantısını kontrol ederek yeniden deneyin.</p>
          <button type="button" className="btn-primary mt-5" onClick={loadDemo}>Tekrar dene</button>
        </Card>}
        <footer className="mt-10 flex flex-col gap-3 border-t border-slate-200 py-6 text-xs text-slate-400 dark:border-slate-800 sm:flex-row sm:justify-between">
          <span>Akademik İçgörü · Açıklanabilir yapay zekâ araştırma prototipi</span>
          <button type="button" className="text-left text-blue-700 hover:underline dark:text-sky-400" onClick={() => { downloadCsv('ogrenci-sablon.csv', [REQUIRED_COLUMNS]); }}>
            <span className="inline-flex items-center gap-1"><Download size={13} /> CSV sütun şablonunu indir</span>
          </button>
        </footer>
      </main>
    </div>
  </div>;
}
