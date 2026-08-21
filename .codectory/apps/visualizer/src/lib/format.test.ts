import { describe, expect, test } from 'bun:test'
import { payloadOk } from './format'

describe('payloadOk', () => {
  test('uses deterministic quality passed status', () => {
    expect(payloadOk(JSON.stringify({ passed: false }))).toBe(false)
    expect(payloadOk(JSON.stringify({ passed: true }))).toBe(true)
  })

  test('preserves agent tool ok status and legacy fallback', () => {
    expect(payloadOk(JSON.stringify({ ok: false }))).toBe(false)
    expect(payloadOk(JSON.stringify({ ok: true }))).toBe(true)
    expect(payloadOk(JSON.stringify({ legacy: true }))).toBe(true)
  })
})
