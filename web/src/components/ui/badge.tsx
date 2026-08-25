import type { HTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
const badgeVariants = cva('inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap', { variants: { variant: { default: 'border-transparent bg-primary text-primary-foreground', secondary: 'border-transparent bg-secondary text-secondary-foreground', outline: 'text-foreground', destructive: 'border-transparent bg-red-600 text-white' } }, defaultVariants: { variant: 'default' } })
export function Badge({ className, variant, ...props }: HTMLAttributes<HTMLDivElement> & VariantProps<typeof badgeVariants>) { return <div className={cn(badgeVariants({ variant }), className)} {...props} /> }
