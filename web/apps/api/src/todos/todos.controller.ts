import {
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  Param,
  ParseUUIDPipe,
  Patch,
  Post,
} from '@nestjs/common';
import type { CreateTodoDto, UpdateTodoDto } from './dto.js';
import type { TodosService } from './todos.service.js';
@Controller('todos')
export class TodosController {
  constructor(private readonly service: TodosService) {}
  @Get() findAll() {
    return this.service.findAll();
  }
  @Post() create(@Body() dto: CreateTodoDto) {
    return this.service.create(dto);
  }
  @Patch(':id') update(
    @Param('id', new ParseUUIDPipe()) id: string,
    @Body() dto: UpdateTodoDto,
  ) {
    return this.service.update(id, dto);
  }
  @Delete(':id') @HttpCode(204) async remove(
    @Param('id', new ParseUUIDPipe()) id: string,
  ) {
    await this.service.remove(id);
  }
}
