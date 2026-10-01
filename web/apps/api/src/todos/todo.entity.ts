import { Column, CreateDateColumn, Entity, PrimaryGeneratedColumn, UpdateDateColumn } from 'typeorm'
@Entity('todos')
export class Todo { @PrimaryGeneratedColumn('uuid') id!: string; @Column({ type: 'varchar', length: 200 }) title!: string; @Column({ default: false }) completed!: boolean; @CreateDateColumn() createdAt!: Date; @UpdateDateColumn() updatedAt!: Date }
