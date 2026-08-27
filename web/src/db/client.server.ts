import postgres from 'postgres'
import { drizzle } from 'drizzle-orm/postgres-js'
import * as schema from './schema'

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
