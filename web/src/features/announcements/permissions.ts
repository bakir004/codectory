export type DashboardRole = 'student' | 'faculty'

export function canCreateAnnouncement(role: DashboardRole): boolean {
  return role === 'faculty'
}
