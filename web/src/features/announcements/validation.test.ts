import { describe, expect, test } from 'bun:test'
import { announcementIdSchema, announcementInputSchema } from './validation'

describe('announcement validation', () => {
  test('trims accepted values', () => expect(announcementInputSchema.parse({ author: '  Alex  ', source: 'Professor', body: '  Hello  ' })).toEqual({ author: 'Alex', source: 'Professor', body: 'Hello' }))
  test('rejects blank, oversized, and invalid source values', () => {
    expect(announcementInputSchema.safeParse({ author: ' ', source: 'Professor', body: 'Hi' }).success).toBe(false)
    expect(announcementInputSchema.safeParse({ author: 'A'.repeat(101), source: 'Professor', body: 'Hi' }).success).toBe(false)
    expect(announcementInputSchema.safeParse({ author: 'A', source: 'Student', body: 'Hi' }).success).toBe(false)
  })
  test('requires valid UUID ids', () => expect(announcementIdSchema.safeParse('not-an-id').success).toBe(false))
})
