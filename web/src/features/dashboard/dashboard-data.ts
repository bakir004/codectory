export type Activity = { id: string; date: string; title: string; category: string; location?: string }
export type Assignment = { id: string; title: string; course: string; due: string; status: 'Not started' | 'In progress' | 'Submitted' }
export type Score = { id: string; title: string; course: string; earned: number; possible: number; graded: string }
export type Announcement = { id: string; author: string; source: 'Professor' | 'Administration'; posted: string; excerpt: string }
export type Course = { id: string; code: string; title: string; professor: string; meeting: string; progress: number }

export const upcomingActivities: Activity[] = [
  { id: 'a1', date: '2026-04-14T09:00:00', title: 'Calculus II lecture', category: 'Class', location: 'Science Hall 204' },
  { id: 'a2', date: '2026-04-15T13:30:00', title: 'Design critique', category: 'Workshop', location: 'Arts Building 118' },
  { id: 'a3', date: '2026-04-17T16:00:00', title: 'Study group: World History', category: 'Study', location: 'Library, floor 2' },
]
export const assignments: Assignment[] = [
  { id: 'as1', title: 'Problem set 8', course: 'MATH 202 · Calculus II', due: '2026-04-13T23:59:00', status: 'In progress' },
  { id: 'as2', title: 'Visual essay draft', course: 'ART 110 · Design Foundations', due: '2026-04-16T17:00:00', status: 'Not started' },
  { id: 'as3', title: 'Primary source analysis', course: 'HIST 240 · World History', due: '2026-04-21T23:59:00', status: 'Not started' },
]
export const scores: Score[] = [
  { id: 's1', title: 'Lab report: Motion', course: 'PHYS 105', earned: 92, possible: 100, graded: '2026-04-08' },
  { id: 's2', title: 'Reading response 5', course: 'HIST 240', earned: 18, possible: 20, graded: '2026-04-05' },
  { id: 's3', title: 'Quiz 3', course: 'MATH 202', earned: 45, possible: 50, graded: '2026-04-02' },
]
export const announcements: Announcement[] = [
  { id: 'n1', author: 'Dr. Maya Chen', source: 'Professor', posted: '2026-04-10', excerpt: 'Office hours will move to Thursday this week. Bring your draft questions.' },
  { id: 'n2', author: 'Office of Student Life', source: 'Administration', posted: '2026-04-09', excerpt: 'Spring research showcase registration is open through Friday, April 17.' },
]
export const courses: Course[] = [
  { id: 'c1', code: 'MATH 202', title: 'Calculus II', professor: 'Dr. Elena Ruiz', meeting: 'Mon & Wed · 9:00 AM · Science Hall 204', progress: 68 },
  { id: 'c2', code: 'ART 110', title: 'Design Foundations', professor: 'Prof. James Okafor', meeting: 'Tue & Thu · 1:30 PM · Arts Building 118', progress: 52 },
  { id: 'c3', code: 'HIST 240', title: 'World History', professor: 'Dr. Maya Chen', meeting: 'Fri · 10:00 AM · Humanities 301', progress: 76 },
]

/** Returns a stable, ascending copy without changing the source array. */
export function sortAssignmentsByDueDate(items: Assignment[]): Assignment[] {
  return items.map((item, index) => ({ item, index })).sort((a, b) => a.item.due.localeCompare(b.item.due) || a.index - b.index).map(({ item }) => item)
}
