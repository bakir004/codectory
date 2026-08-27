import { existsSync } from 'node:fs'
import { resolve } from 'node:path'
import dotenv from 'dotenv'
import postgres from 'postgres'
import { drizzle } from 'drizzle-orm/postgres-js'
import * as schema from './schema'

function loadDatabaseEnvironment() {
  // Web scripts run from web/, while Docker Compose and the shared .env live
  // at the repository root. Preserve real process variables when deployed.
  const candidates = [resolve(process.cwd(), '.env'), resolve(process.cwd(), '../.env')]
  const path = candidates.find(existsSync)
  if (path) dotenv.config({ path })
}

loadDatabaseEnvironment()

function environment() {
  const required = ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST', 'POSTGRES_PORT'] as const
  for (const key of required) if (!process.env[key]) throw new Error(`Database configuration missing ${key}`)
  const port = Number(process.env.POSTGRES_PORT)
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Database configuration has an invalid POSTGRES_PORT')
  return { database: process.env.POSTGRES_DB!, username: process.env.POSTGRES_USER!, password: process.env.POSTGRES_PASSWORD!, host: process.env.POSTGRES_HOST!, port }
}

const sql = postgres(environment())
export const db = drizzle(sql, { schema })
export { sql }
