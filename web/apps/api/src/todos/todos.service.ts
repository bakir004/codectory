import {
  BadRequestException,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import type { Repository } from 'typeorm';
import type { CreateTodoDto, UpdateTodoDto } from './dto.js';
import { Todo } from './todo.entity.js';
@Injectable()
export class TodosService {
  constructor(
    @InjectRepository(Todo) private readonly repo: Repository<Todo>,
  ) {}
  findAll() {
    return this.repo.find({ order: { createdAt: 'DESC' } });
  }
  create(dto: CreateTodoDto) {
    return this.repo.save(
      this.repo.create({ title: dto.title, completed: false }),
    );
  }
  async update(id: string, dto: UpdateTodoDto) {
    if (dto.title === undefined && dto.completed === undefined)
      throw new BadRequestException('Update cannot be empty');
    const todo = await this.repo.findOneBy({ id });
    if (!todo) throw new NotFoundException('Todo not found');
    Object.assign(todo, dto);
    return this.repo.save(todo);
  }
  async remove(id: string) {
    const result = await this.repo.delete(id);
    if (!result.affected) throw new NotFoundException('Todo not found');
  }
}
