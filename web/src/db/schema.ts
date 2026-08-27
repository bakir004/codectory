import { pgTable, text, timestamp, uuid } from 'drizzle-orm/pg-core'

export const announcements = pgTable('announcements', {
  id: uuid('id').defaultRandom().primaryKey(),
  author: text('author').notNull(),
  source: text('source').notNull(),
  body: text('body').notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
})
