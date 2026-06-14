import { describe, it, expect } from 'vitest';
import { calculateQuizResult, getResultMessage, QUESTIONS, MOOD_NAMES } from './moodQuiz';

describe('calculateQuizResult', () => {
  it('returns targets and topMoods for valid answers', () => {
    const result = calculateQuizResult([0, 0, 0, 0, 0, 0]);
    expect(result.targets.length).toBeGreaterThan(0);
    expect(result.topMoods.length).toBeGreaterThanOrEqual(1);
    expect(result.topMoods.length).toBeLessThanOrEqual(3);
  });

  it('topMoods percentages are valid numbers', () => {
    const result = calculateQuizResult([0, 1, 2, 3, 0, 1]);
    result.topMoods.forEach(m => {
      expect(m.percentage).toBeGreaterThan(0);
      expect(m.percentage).toBeLessThanOrEqual(100);
    });
  });

  it('handles empty/null answer indexes', () => {
    const result = calculateQuizResult([null, undefined, null, null, null, null]);
    expect(result.targets).toEqual([]);
    expect(result.topMoods).toEqual([]);
  });

  it('handles partial answers', () => {
    const result = calculateQuizResult([0, null, 2]);
    expect(result.targets.length).toBeGreaterThan(0);
  });

  it('all battaniye-leaning answers produce battaniye in top', () => {
    const result = calculateQuizResult([0, null, 1, 3, null, null]);
    const moodIds = result.topMoods.map(m => m.moodId);
    expect(moodIds).toContain('battaniye');
  });
});

describe('getResultMessage', () => {
  it('returns a message for each mood', () => {
    for (const moodId of Object.keys(MOOD_NAMES)) {
      const msg = getResultMessage([{ moodId, percentage: 100 }]);
      expect(msg).toBeTruthy();
      expect(typeof msg).toBe('string');
    }
  });

  it('returns fallback for empty input', () => {
    expect(getResultMessage([])).toBe('Bugün her türden film iyi gidebilir.');
    expect(getResultMessage(null)).toBe('Bugün her türden film iyi gidebilir.');
  });
});

describe('QUESTIONS structure', () => {
  it('has 6 questions with 4 answers each', () => {
    expect(QUESTIONS).toHaveLength(6);
    QUESTIONS.forEach(q => {
      expect(q.answers).toHaveLength(4);
      q.answers.forEach(a => {
        expect(a.targets.length).toBeGreaterThanOrEqual(1);
        a.targets.forEach(t => {
          expect(Object.keys(MOOD_NAMES)).toContain(t);
        });
      });
    });
  });
});
