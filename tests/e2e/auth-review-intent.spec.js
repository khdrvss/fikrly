const { test, expect } = require('@playwright/test');

test.describe('Auth redirect intent', () => {
  test('preserves next target when redirected to login from review page', async ({ page }) => {
    await page.goto('/sharh-yozish/?company=57');

    await expect(page).toHaveURL(/\/accounts\/login\/\?next=\/sharh-yozish\/%3Fcompany%3D57/);

    const nextInput = page.locator('input[name="next"]');
    await expect(nextInput).toHaveValue('/sharh-yozish/?company=57');
  });

  test('signup returns user to intended review page', async ({ page }) => {
    test.skip(process.env.RUN_DESTRUCTIVE_E2E !== '1', 'Set RUN_DESTRUCTIVE_E2E=1 to run signup flow.');

    await page.goto('/sharh-yozish/?company=57');
    await expect(page).toHaveURL(/\/accounts\/login\//);

    await page.getByRole('link', { name: /Ro'yxatdan o'tish/i }).click();
    await expect(page).toHaveURL(/\/accounts\/signup\//);

    const suffix = Date.now();
    await page.locator('input[name="email"]').fill(`e2e${suffix}@gmail.com`);
    await page.locator('input[name="username"]').fill(`e2e_user_${suffix}`);
    await page.locator('input[name="password1"]').fill('StrongPass!234');
    await page.locator('input[name="password2"]').fill('StrongPass!234');

    await page.getByRole('button', { name: /Ro'yxatdan o'tish/i }).click();

    await expect(page).toHaveURL(/\/sharh-yozish\/\?company=57/);
    await expect(page.getByRole('heading', { name: /Tajribangizni baholang/i })).toBeVisible();
  });
});
