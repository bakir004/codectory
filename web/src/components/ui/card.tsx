import type { HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'
export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={cn('bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm', className)} {...props} /> }
export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={cn('grid auto-rows-min items-start gap-1.5 px-6', className)} {...props} /> }
export function CardTitle({ className, ...props }: HTMLAttributes<HTMLHeadingElement>) { return <h3 className={cn('leading-none font-semibold tracking-tight', className)} {...props} /> }
export function CardDescription({ className, ...props }: HTMLAttributes<HTMLParagraphElement>) { return <p className={cn('text-muted-foreground text-sm', className)} {...props} /> }
export function CardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={cn('px-6', className)} {...props} /> }
