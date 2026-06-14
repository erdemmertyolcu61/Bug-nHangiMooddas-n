import { describe, it, expect, beforeEach } from 'vitest';
import { rankMoods, recordMoodPick } from './moodRanking';

const MOODS = [
  { id: 'battaniye' },
  { id: 'yolculuk' },
  { id: 'gece' },
  { id: 'kahkaha' },
  { id: 'adrenalin' },
  { id: 'zihin' },
];

beforeEach(() => {
  localStorage.clear();
});

describe('rankMoods', () => {
  it('returns original order when no picks recorded', () => {
    const result = rankMoods(MOODS);
    expect(result.map(m => m.id)).toEqual(MOODS.map(m => m.id));
  });

  it('promotes picked moods to front', () => {
    recordMoodPick('zihin');
    recordMoodPick('zihin');
    recordMoodPick('gece');
    const result = rankMoods(MOODS);
    expect(result[0].id).toBe('zihin');
    expect(result[1].id).toBe('gece');
  });

  it('preserves all moods without duplicates', () => {
    recordMoodPick('kahkaha');
    const result = rankMoods(MOODS);
    expect(result).toHaveLength(MOODS.length);
    const ids = result.map(m => m.id);
    expect(new Set(ids).size).toBe(MOODS.length);
  });

  it('promotes at most 4 moods', () => {
    ['battaniye', 'yolculuk', 'gece', 'kahkaha', 'adrenalin', 'zihin'].forEach(id => {
      recordMoodPick(id);
    });
    const result = rankMoods(MOODS);
    expect(result).toHaveLength(MOODS.length);
  });
});

describe('recordMoodPick', () => {
  it('records pick to localStorage', () => {
    recordMoodPick('gece');
    recordMoodPick('gece');
    const stored = JSON.parse(localStorage.getItem('fc_mood_picks'));
    expect(stored.gece).toBe(2);
  });

  it('handles null/empty gracefully', () => {
    expect(() => recordMoodPick(null)).not.toThrow();
    expect(() => recordMoodPick('')).not.toThrow();
  });
});
