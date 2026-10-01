import { Module } from '@nestjs/common'
import { TypeOrmModule } from '@nestjs/typeorm'
import { TodosModule } from './todos/todos.module.js'
import { Todo } from './todos/todo.entity.js'

@Module({ imports: [TypeOrmModule.forRoot({ type: 'postgres', url: process.env.DATABASE_URL || 'postgres://todo:todo@localhost:5432/todos', entities: [Todo], migrations: ['dist/src/migrations/*.js'], synchronize: false }), TodosModule] })
export class AppModule {}
