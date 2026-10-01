import 'reflect-metadata'
import { DataSource } from 'typeorm'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { Todo } from './todos/todo.entity.js'
export default new DataSource({ type: 'postgres', url: process.env.DATABASE_URL || 'postgres://todo:todo@localhost:5432/todos', entities: [Todo], migrations: [join(dirname(fileURLToPath(import.meta.url)), 'migrations/*{.ts,.js}')] })
