import { describe, it, expect, beforeEach } from 'vitest';
import { isStreakMilestone, STREAK_MILESTONES } from './streak';

describe('isStreakMilestone', () => {
  it('returns true for milestone values', () => {
    STREAK_MILESTONES.forEach(n => {
      expect(isStreakMilestone(n)).toBe(true);
    });
  });

  it('returns false for non-milestone values', () => {
    expect(isStreakMilestone(2)).toBe(false);
    expect(isStreakMilestone(5)).toBe(false);
    expect(isStreakMilestone(99)).toBe(false);
  });

  it('includes expected values', () => {
    expect(STREAK_MILESTONES).toContain(3);
    expect(STREAK_MILESTONES).toContain(7);
    expect(STREAK_MILESTONES).toContain(30);
  });
});
