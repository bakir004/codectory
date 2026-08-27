import type { TextareaHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'
export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) { return <textarea className={cn('min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-red-700', className)} {...props} /> }
