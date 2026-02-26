const { test, expect } = require('@playwright/test');

test.describe('Full smoke logic', () => {
  test('core pages load and language switch works', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/\/$/);
    await expect(page.locator('main')).toBeVisible();

    const langToggle = page.locator('.lang-wrapper > button');
    await expect(langToggle).toBeVisible();
    await langToggle.click();

    const ruLink = page.locator('.lang-dropdown a', { hasText: 'Русский' });
    await expect(ruLink).toBeVisible();
    await ruLink.click();
    await expect(page).toHaveURL(/\/ru\/$/);

    const uzToggle = page.locator('.lang-wrapper > button');
    await uzToggle.click();
    const uzLink = page.locator('.lang-dropdown a', { hasText: "O'zbek tili" });
    await expect(uzLink).toBeVisible();
    await uzLink.click();
    await expect(page).toHaveURL(/\/$/);

    await page.goto('/bizneslar/');
    await expect(page.locator('main')).toBeVisible();

    await page.goto('/kategoriyalar/');
    await expect(page.locator('main')).toBeVisible();

    await page.goto('/accounts/login/');
    await expect(page).toHaveURL(/\/accounts\/login\//);
    await expect(page.locator('form')).toBeVisible();
  });

  test('search suggestions show businesses directly', async ({ page }) => {
    await page.goto('/');

    const searchInput = page.locator('#searchInput');
    await expect(searchInput).toBeVisible();

    await searchInput.fill('Click');
    const suggestions = page.locator('#searchSuggestions');
    await expect(suggestions).toBeVisible();

    const firstSuggestion = suggestions.locator('a').first();
    await expect(firstSuggestion).toBeVisible();
    await expect(suggestions).not.toContainText('Natijalar');
    await expect(suggestions).not.toContainText('Результаты');
    await expect(suggestions).not.toContainText('ta kompaniya');
  });
});
