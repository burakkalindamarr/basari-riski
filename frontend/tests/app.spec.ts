import { expect, test } from '@playwright/test';
import path from 'node:path';

test('sample dashboard loads from the real API and toggles dark mode', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Genel Bakış' })).toBeVisible();
  await expect(page.getByText('Model tahminleri yükleniyor...')).toHaveCount(0);
  await expect(page.getByText('Risk dağılımı')).toBeVisible();
  await page.getByRole('button', { name: 'Koyu temayı aç' }).click();
  await expect(page.locator('html')).toHaveClass(/dark/);
});

test('student details contain real SHAP explanation and performance audit', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Risk dağılımı')).toBeVisible();
  await page.getByRole('button', { name: 'Öğrenci Analizi' }).click();
  await expect(page.getByRole('heading', { name: 'Öğrenci Analizi' })).toBeVisible();
  await page.getByRole('button', { name: /kaydının detayını göster/ }).first().click();
  await expect(page.getByText('Tahmini etkileyen faktörler')).toBeVisible();
  await expect(page.getByText('Birim: log-odds.')).toBeVisible();
  await page.getByRole('button', { name: 'Detayı kapat' }).click();
  await page.getByRole('button', { name: 'Model Performansı' }).click();
  await expect(page.getByRole('heading', { name: 'Model Performansı' })).toBeVisible();
  await expect(page.getByText('Gruplar arası hata farkları')).toBeVisible();
});

test('manual single-student form predicts and explains with the trained model', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Risk dağılımı')).toBeVisible();
  await page.getByRole('button', { name: 'Tek Öğrenci Tahmini' }).click();
  await expect(page.getByRole('heading', { name: 'Tek Öğrenci Analizi' })).toBeVisible();
  await page.getByRole('button', { name: 'Riski hesapla' }).click();
  await expect(page.getByText('Gerçek model tahmini')).toBeVisible();
  await expect(page.getByText('Tahmini etkileyen faktörler')).toBeVisible();
});

test('anonymous example CSV upload returns a working data table', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Risk dağılımı')).toBeVisible();
  await page.locator('input[type="file"]').setInputFiles(
    path.resolve(process.cwd(), '../ornek_ogrenciler.csv'),
  );
  await expect(page.getByText('CSV analizi')).toBeVisible();
  await page.getByRole('button', { name: 'Öğrenci Analizi' }).click();
  await expect(page.getByRole('heading', { name: 'Öğrenci Analizi' })).toBeVisible();
});
