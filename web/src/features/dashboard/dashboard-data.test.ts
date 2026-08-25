import { describe, expect, test } from 'bun:test'
import { sortAssignmentsByDueDate, type Assignment } from './dashboard-data'

const item = (id: string, due: string): Assignment => ({ id, title: id, course: 'TEST', due, status: 'Not started' })
describe('sortAssignmentsByDueDate', () => {
  test('sorts nearest first and does not mutate input', () => {
    const input = [item('later', '2026-05-02'), item('soon', '2026-04-12')]
    expect(sortAssignmentsByDueDate(input).map((x) => x.id)).toEqual(['soon', 'later'])
    expect(input.map((x) => x.id)).toEqual(['later', 'soon'])
  })
  test('preserves source order for equal due dates', () => {
    expect(sortAssignmentsByDueDate([item('one', '2026-04-12'), item('two', '2026-04-12')]).map((x) => x.id)).toEqual(['one', 'two'])
  })
})
