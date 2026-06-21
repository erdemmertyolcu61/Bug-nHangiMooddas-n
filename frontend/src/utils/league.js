export function getLeague(elo) {
  if (elo >= 1800) return { tier: 'sine-guru', label: 'Sine-Guru', emoji: '💎' };
  if (elo >= 1500) return { tier: 'altin', label: 'Altın', emoji: '🥇' };
  if (elo >= 1200) return { tier: 'gumus', label: 'Gümüş', emoji: '🥈' };
  return { tier: 'bronz', label: 'Bronz', emoji: '🥉' };
}

export const LEAGUE_TIERS = [
  { tier: 'bronz', label: 'Bronz', emoji: '🥉', min: 0, max: 1199 },
  { tier: 'gumus', label: 'Gümüş', emoji: '🥈', min: 1200, max: 1499 },
  { tier: 'altin', label: 'Altın', emoji: '🥇', min: 1500, max: 1799 },
  { tier: 'sine-guru', label: 'Sine-Guru', emoji: '💎', min: 1800, max: Infinity },
];
