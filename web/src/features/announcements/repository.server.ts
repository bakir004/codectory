import { desc, eq } from 'drizzle-orm'
import { db } from '@/db/client.server'
import { announcements } from '@/db/schema'
import type { AnnouncementInput } from './validation'

export async function listAnnouncements() {
  return db.select().from(announcements).orderBy(desc(announcements.createdAt), desc(announcements.id))
}
export async function createAnnouncement(input: AnnouncementInput) {
  const [row] = await db.insert(announcements).values(input).returning()
  return row
}
export async function updateAnnouncement(id: string, input: AnnouncementInput) {
  const [row] = await db.update(announcements).set({ ...input, updatedAt: new Date() }).where(eq(announcements.id, id)).returning()
  if (!row) throw new Error('Announcement was not found')
  return row
}
export async function deleteAnnouncement(id: string) {
  const [row] = await db.delete(announcements).where(eq(announcements.id, id)).returning({ id: announcements.id })
  if (!row) throw new Error('Announcement was not found')
  return row
}
