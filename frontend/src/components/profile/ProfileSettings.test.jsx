import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';

// ProfileSettings API ve push yardımcılarını modül düzeyinde çağırır — ikisini de mock'la.
vi.mock('../../services/api', () => ({
  exportMyData: vi.fn(),
  getNotifyTime: vi.fn().mockResolvedValue({ hour: 18 }),
  setNotifyTime: vi.fn().mockResolvedValue({ ok: true }),
  getNotifyPreferences: vi.fn(),
  setNotifyPreference: vi.fn(),
  setActivityVisibility: vi.fn(),
  getBlockedUsers: vi.fn().mockResolvedValue({ blocked: [] }),
  unblockUser: vi.fn(),
}));
vi.mock('../../utils/push', () => ({ isPushSubscribed: vi.fn() }));
vi.mock('../../utils/native', () => ({ isNative: false }));

import ProfileSettings from './ProfileSettings';
import { getNotifyPreferences, setNotifyPreference } from '../../services/api';
import { isPushSubscribed } from '../../utils/push';

/** Tıklama + ardındaki async state güncellemesini birlikte akıt. */
async function click(el) {
  await act(async () => { fireEvent.click(el); });
}

const ALL_ON = { social: true, daily: true, game: true, digest: true };

function renderSettings() {
  return render(
    <ProfileSettings theme="dark" toggleTheme={() => {}} logout={() => {}} navigate={() => {}} />
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  isPushSubscribed.mockResolvedValue(true);
  getNotifyPreferences.mockResolvedValue({ preferences: { ...ALL_ON } });
});

describe('Bildirim türleri', () => {
  it('abone olmayan cihazda hiç gösterilmez', async () => {
    isPushSubscribed.mockResolvedValue(false);
    renderSettings();
    await waitFor(() => expect(isPushSubscribed).toHaveBeenCalled());
    expect(screen.queryByText('Bildirim Türleri')).toBeNull();
  });

  it('abone cihazda dört kategoriyi de listeler', async () => {
    renderSettings();
    await click(await screen.findByText('Bildirim Türleri'));
    for (const label of ['Sosyal', 'Günün Filmi', 'Oyun & Etkinlik', 'Özet & Hatırlatma']) {
      expect(await screen.findByRole('switch', { name: label })).toBeTruthy();
    }
  });

  it('kapatılan kategoriyi sunucuya yalnız o anahtarla gönderir', async () => {
    setNotifyPreference.mockResolvedValue({
      ok: true, preferences: { ...ALL_ON, game: false },
    });
    renderSettings();
    await click(await screen.findByText('Bildirim Türleri'));
    await click(await screen.findByRole('switch', { name: 'Oyun & Etkinlik' }));

    // Kısmi güncelleme: diğer kategoriler gönderilmemeli.
    expect(setNotifyPreference).toHaveBeenCalledWith('game', false);
    await waitFor(() =>
      expect(screen.getByRole('switch', { name: 'Oyun & Etkinlik' }).getAttribute('aria-checked'))
        .toBe('false')
    );
    expect(screen.getByRole('switch', { name: 'Sosyal' }).getAttribute('aria-checked')).toBe('true');
  });

  it('sunucu kaydedemezse anahtarı geri alır', async () => {
    // Aksi halde kullanıcı bildirimi kapattığını sanır ama almaya devam eder.
    setNotifyPreference.mockResolvedValue({ ok: false });
    renderSettings();
    await click(await screen.findByText('Bildirim Türleri'));
    const toggle = await screen.findByRole('switch', { name: 'Özet & Hatırlatma' });
    await click(toggle);

    await waitFor(() =>
      expect(screen.getByRole('switch', { name: 'Özet & Hatırlatma' }).getAttribute('aria-checked'))
        .toBe('true')
    );
  });

  it('kaç türün kapalı olduğunu özet satırında gösterir', async () => {
    getNotifyPreferences.mockResolvedValue({
      preferences: { ...ALL_ON, game: false, digest: false },
    });
    renderSettings();
    expect(await screen.findByText('2 tür kapalı')).toBeTruthy();
  });
});
