export type RiskLevel = 'low' | 'medium' | 'high';
export interface FeatureContribution {
  feature: string;
  label: string;
  contribution: number;
}
export interface Explanation {
  unit: 'log_odds';
  base_value: number;
  predicted_log_odds: number;
  increases: FeatureContribution[];
  decreases: FeatureContribution[];
}
export interface Student {
  id: string;
  course: string;
  risk: number;
  level: RiskLevel;
  rank: number;
  explanation: Explanation;
}
export interface CourseStat {
  course: string;
  count: number;
  average_risk: number;
}
export interface PredictionResult {
  source: 'demo' | 'upload' | 'manual';
  summary: {
    count: number;
    low: number;
    medium: number;
    high: number;
    average_risk: number;
  };
  students: Student[];
  courses: CourseStat[];
  algorithm: string;
  features: number;
  disclaimer: string;
}

const API_BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(API_BASE + path, options);
  } catch {
    throw new Error('API sunucusuna bağlanılamadı. FastAPI servisinin çalıştığını kontrol edin.');
  }

  if (!response.ok) {
    let message = 'İstek tamamlanamadı.';
    try {
      const result = await response.json() as { detail?: string | { msg?: string }[] };
      if (typeof result.detail === 'string') message = result.detail;
      else if (Array.isArray(result.detail)) message = result.detail.map(d => d.msg).filter(Boolean).join('; ');
    } catch {
      // Avoid exposing raw response bodies.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export interface SchemaOption { value: number; label: string }
export interface SchemaField {
  name: string;
  label: string;
  kind: 'select' | 'number';
  default: number;
  min?: number;
  max?: number;
  step?: number;
  options?: SchemaOption[];
}
export interface FormSchema { fields: SchemaField[]; notes: string; source: string }
export const getSchema = () => request<FormSchema>('/schema');
export const predictOne = (student: Record<string, number>, id: string) =>
  request<PredictionResult>('/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ student, id }) });

export const getDemo = (signal?: AbortSignal) => request<PredictionResult>('/demo', { signal });

export function analyzeCsv(file: File): Promise<PredictionResult> {
  const data = new FormData();
  data.append('file', file);
  return request<PredictionResult>('/analyze', { method: 'POST', body: data });
}

export const REQUIRED_COLUMNS = [
  'ogrenci_no', 'Marital status', 'Application mode', 'Application order',
  'Course', 'Daytime/evening attendance', 'Previous qualification',
  'Previous qualification (grade)', "Mother's qualification",
  "Father's qualification", "Mother's occupation", "Father's occupation",
  'Admission grade', 'Displaced', 'Gender', 'Scholarship holder',
  'Age at enrollment',
];

export function downloadCsv(filename: string, rows: (string | number)[][]) {
  const escape = (value: string | number) => {
    const string = String(value);
    // Excel spreadsheet formula safety, including leading whitespace.
    const safe = /^[\s]*[=+\-@]/.test(string) ? "'" + string : string;
    return '"' + safe.replace(/"/g, '""') + '"';
  };
  const csv = '\uFEFF' + rows.map(row => row.map(escape).join(',')).join('\r\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
