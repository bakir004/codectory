import { useState, type FormEvent } from 'react'
import { useRouter } from '@tanstack/react-router'
import { Pencil, Trash2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { addAnnouncement, editAnnouncement, removeAnnouncement, type AnnouncementRecord } from './server'
import { announcementInputSchema, type AnnouncementInput } from './validation'

const buttonClass = 'rounded-md bg-red-700 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-700 disabled:cursor-not-allowed disabled:opacity-60'
const empty: AnnouncementInput = { author: '', source: 'Professor', body: '' }
const formatDate = (value: string) => new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(new Date(value))

function AnnouncementForm({ announcement, onDone }: { announcement?: AnnouncementRecord; onDone: () => void }) {
  const router = useRouter()
  const [values, setValues] = useState<AnnouncementInput>(announcement ? { author: announcement.author, source: announcement.source as AnnouncementInput['source'], body: announcement.body } : empty)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [serverError, setServerError] = useState('')
  const [saving, setSaving] = useState(false)
  async function submit(event: FormEvent) {
    event.preventDefault()
    setServerError('')
    const result = announcementInputSchema.safeParse(values)
    if (!result.success) { setErrors(Object.fromEntries(result.error.issues.map((issue) => [String(issue.path[0]), issue.message]))); return }
    setErrors({}); setSaving(true)
    try { if (announcement) await editAnnouncement({ data: { ...result.data, id: announcement.id } }); else await addAnnouncement({ data: result.data }); await router.invalidate(); onDone() }
    catch (error) { setServerError(error instanceof Error ? error.message : 'Unable to save announcement') }
    finally { setSaving(false) }
  }
  const update = (key: keyof AnnouncementInput, value: string) => setValues((current) => ({ ...current, [key]: value }))
  return <form onSubmit={submit} className="space-y-4">
    <div><Label htmlFor="announcement-author">Author</Label><Input id="announcement-author" value={values.author} maxLength={100} required onChange={(e) => update('author', e.target.value)} aria-invalid={!!errors.author} aria-describedby={errors.author ? 'announcement-author-error' : undefined} />{errors.author && <p id="announcement-author-error" className="mt-1 text-sm text-red-700">{errors.author}</p>}</div>
    <div><Label htmlFor="announcement-source">Source</Label><select id="announcement-source" className="h-10 w-full rounded-md border bg-background px-3 text-sm focus-visible:outline-2 focus-visible:outline-red-700" value={values.source} required onChange={(e) => update('source', e.target.value)} aria-invalid={!!errors.source} aria-describedby={errors.source ? 'announcement-source-error' : undefined}><option>Professor</option><option>Administration</option></select>{errors.source && <p id="announcement-source-error" className="mt-1 text-sm text-red-700">{errors.source}</p>}</div>
    <div><Label htmlFor="announcement-body">Announcement</Label><Textarea id="announcement-body" value={values.body} maxLength={500} required onChange={(e) => update('body', e.target.value)} aria-invalid={!!errors.body} aria-describedby={errors.body ? 'announcement-body-error' : undefined} />{errors.body && <p id="announcement-body-error" className="mt-1 text-sm text-red-700">{errors.body}</p>}</div>
    {serverError && <p role="alert" className="rounded-md bg-red-50 p-3 text-sm text-red-800">{serverError}</p>}
    <div className="flex justify-end gap-3"><button type="button" className={buttonClass} onClick={onDone} disabled={saving}>Cancel</button><button type="submit" className={buttonClass} disabled={saving}>{saving ? 'Saving…' : announcement ? 'Save changes' : 'Create announcement'}</button></div>
  </form>
}

export function Announcements({ announcements }: { announcements: AnnouncementRecord[] }) {
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<AnnouncementRecord>()
  const [deleting, setDeleting] = useState<AnnouncementRecord>()
  const [deleteError, setDeleteError] = useState('')
  const [deletingNow, setDeletingNow] = useState(false)
  const router = useRouter()
  async function confirmDelete() {
    if (!deleting) return
    setDeletingNow(true); setDeleteError('')
    try { await removeAnnouncement({ data: { id: deleting.id } }); await router.invalidate(); setDeleting(undefined) }
    catch (error) { setDeleteError(error instanceof Error ? error.message : 'Unable to delete announcement') }
    finally { setDeletingNow(false) }
  }
  return <>
    <CardHeader><div className="flex items-center justify-between gap-4"><div><CardTitle id="announcements-heading">Announcements</CardTitle><CardDescription>From your campus community</CardDescription></div><button type="button" className={buttonClass} onClick={() => { setEditing(undefined); setOpen(true) }}>Create announcement</button></div></CardHeader>
    <CardContent>{announcements.length === 0 ? <p className="py-4 text-sm text-muted-foreground">No announcements yet. Create the first one.</p> : <ul className="space-y-4">{announcements.map((announcement, index) => <li key={announcement.id}><article><div className="flex items-center gap-2"><Badge variant={announcement.source === 'Professor' ? 'secondary' : 'outline'}>{announcement.source}</Badge><time className="text-xs text-muted-foreground" dateTime={announcement.createdAt}>{formatDate(announcement.createdAt)}</time></div><h3 className="mt-2 font-semibold">{announcement.author}</h3><p className="mt-1 text-sm leading-relaxed text-muted-foreground">{announcement.body}</p><div className="mt-3 flex gap-2"><button type="button" className={buttonClass} onClick={() => { setEditing(announcement); setOpen(true) }}><Pencil className="mr-1 inline size-3.5" aria-hidden="true" />Edit</button><button type="button" className={buttonClass} onClick={() => setDeleting(announcement)}><Trash2 className="mr-1 inline size-3.5" aria-hidden="true" />Delete</button></div></article>{index < announcements.length - 1 && <hr className="mt-4 border-border" />}</li>)}</ul>}</CardContent>
    <Dialog open={open} onOpenChange={setOpen}><DialogContent><DialogHeader><DialogTitle>{editing ? 'Edit announcement' : 'Create announcement'}</DialogTitle><DialogDescription>Share a clear update with your campus community.</DialogDescription></DialogHeader><AnnouncementForm key={editing?.id ?? 'new'} announcement={editing} onDone={() => setOpen(false)} /></DialogContent></Dialog>
    <AlertDialog open={!!deleting} onOpenChange={(value) => !value && setDeleting(undefined)}><AlertDialogContent><AlertDialogHeader><AlertDialogTitle>Delete announcement?</AlertDialogTitle><AlertDialogDescription>This action cannot be undone. The announcement will be removed permanently.</AlertDialogDescription></AlertDialogHeader>{deleteError && <p role="alert" className="mt-3 text-sm text-red-700">{deleteError}</p>}<AlertDialogFooter><AlertDialogCancel disabled={deletingNow}>Cancel</AlertDialogCancel><AlertDialogAction onClick={(event) => { event.preventDefault(); void confirmDelete() }} disabled={deletingNow}>{deletingNow ? 'Deleting…' : 'Delete announcement'}</AlertDialogAction></AlertDialogFooter></AlertDialogContent></AlertDialog>
  </>
}
