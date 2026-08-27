import { z } from 'zod'

export const sourceSchema = z.enum(['Professor', 'Administration'])
export const announcementInputSchema = z.object({
  author: z.string().trim().min(1, 'Author is required').max(100, 'Author must be 100 characters or fewer'),
  source: sourceSchema,
  body: z.string().trim().min(1, 'Announcement text is required').max(500, 'Announcement must be 500 characters or fewer'),
})
export const announcementIdSchema = z.string().uuid('Announcement id is invalid')
export const updateAnnouncementSchema = announcementInputSchema.extend({ id: announcementIdSchema })
export const deleteAnnouncementSchema = z.object({ id: announcementIdSchema })
export type AnnouncementInput = z.infer<typeof announcementInputSchema>
