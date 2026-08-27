import { describe, expect, test } from 'bun:test'
import { canCreateAnnouncement } from './permissions'

describe('announcement permissions', () => {
  test('allows faculty to create announcements', () => {
    expect(canCreateAnnouncement('faculty')).toBe(true)
  })

  test('does not expose creation to students', () => {
    expect(canCreateAnnouncement('student')).toBe(false)
  })
})
