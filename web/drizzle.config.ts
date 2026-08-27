import { defineConfig } from 'drizzle-kit'
import { resolve } from 'node:path'
import dotenv from 'dotenv'
dotenv.config({ path: resolve(process.cwd(), '../.env'), override: true })

export default defineConfig({ schema: './src/db/schema.ts', out: './drizzle', dialect: 'postgresql', dbCredentials: { host: process.env.POSTGRES_HOST!, port: Number(process.env.POSTGRES_PORT), user: process.env.POSTGRES_USER!, password: process.env.POSTGRES_PASSWORD!, database: process.env.POSTGRES_DB! } })
