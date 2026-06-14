import { describe, it, expect, beforeEach } from 'vitest';
import { computeMilestones, milestoneSummary, MILESTONES } from './milestones';

describe('computeMilestones', () => {
  it('returns all milestones with progress data', () => {
    const result = computeMilestones({ saved: 5, watched: 0, notes: 0 });
    expect(result).toHaveLength(MILESTONES.length);
    expect(result[0]).toHaveProperty('progress');
    expect(result[0]).toHaveProperty('achieved');
    expect(result[0]).toHaveProperty('current');
  });

  it('marks milestone as achieved when threshold met', () => {
    const result = computeMilestones({ saved: 10, watched: 1, notes: 0 });
    const saved10 = result.find(m => m.id === 'saved_10');
    expect(saved10.achieved).toBe(true);
    expect(saved10.progress).toBe(1);

    const watched1 = result.find(m => m.id === 'watched_1');
    expect(watched1.achieved).toBe(true);
  });

  it('calculates partial progress correctly', () => {
    const result = computeMilestones({ saved: 5 });
    const saved10 = result.find(m => m.id === 'saved_10');
    expect(saved10.progress).toBe(0.5);
    expect(saved10.achieved).toBe(false);
  });

  it('handles empty stats gracefully', () => {
    const result = computeMilestones();
    expect(result.every(m => m.achieved === false)).toBe(true);
    expect(result.every(m => m.progress === 0)).toBe(true);
  });

  it('clamps progress to 1', () => {
    const result = computeMilestones({ saved: 200 });
    const saved1 = result.find(m => m.id === 'saved_1');
    expect(saved1.progress).toBe(1);
  });
});

describe('milestoneSummary', () => {
  it('returns correct unlocked count', () => {
    const summary = milestoneSummary({ saved: 10, watched: 1, notes: 0 });
    expect(summary.unlocked).toBe(3); // saved_1, saved_10, watched_1
    expect(summary.total).toBe(MILESTONES.length);
  });

  it('returns zero unlocked for empty stats', () => {
    const summary = milestoneSummary({});
    expect(summary.unlocked).toBe(0);
  });
});
