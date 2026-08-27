import { createServerFn } from '@tanstack/react-start'
import { createAnnouncement, deleteAnnouncement, listAnnouncements, updateAnnouncement } from './repository.server'
import { announcementIdSchema, announcementInputSchema, deleteAnnouncementSchema, updateAnnouncementSchema } from './validation'

const json = (row: Awaited<ReturnType<typeof createAnnouncement>>) => ({ ...row, createdAt: row.createdAt.toISOString(), updatedAt: row.updatedAt.toISOString() })
export const getAnnouncements = createServerFn({ method: 'GET' }).handler(async () => (await listAnnouncements()).map(json))
export const addAnnouncement = createServerFn({ method: 'POST' }).validator(announcementInputSchema).handler(async ({ data }) => json(await createAnnouncement(data)))
export const editAnnouncement = createServerFn({ method: 'POST' }).validator(updateAnnouncementSchema).handler(async ({ data }) => { const { id, ...input } = data; return json(await updateAnnouncement(id, input)) })
export const removeAnnouncement = createServerFn({ method: 'POST' }).validator(deleteAnnouncementSchema).handler(async ({ data }) => { announcementIdSchema.parse(data.id); return deleteAnnouncement(data.id) })
export type AnnouncementRecord = Awaited<ReturnType<typeof getAnnouncements>>[number]
