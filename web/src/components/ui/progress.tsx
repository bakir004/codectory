import * as ProgressPrimitive from '@radix-ui/react-progress'
import type { ComponentProps } from 'react'
import { cn } from '@/lib/utils'
export function Progress({ className, value, ...props }: ComponentProps<typeof ProgressPrimitive.Root>) { return <ProgressPrimitive.Root className={cn('bg-secondary relative h-2 w-full overflow-hidden rounded-full', className)} {...props}><ProgressPrimitive.Indicator className="bg-primary h-full w-full flex-1 transition-all" style={{ transform: `translateX(-${100 - (value || 0)}%)` }} /></ProgressPrimitive.Root> }
