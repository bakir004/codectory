import 'reflect-metadata'
import { ValidationPipe } from '@nestjs/common'
import { NestFactory } from '@nestjs/core'
import { AppModule } from './app.module.js'

async function bootstrap() { const app = await NestFactory.create(AppModule); app.setGlobalPrefix('api'); app.enableCors({ origin: process.env.FRONTEND_ORIGIN || 'http://localhost:3000' }); app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true })); await app.listen(Number(process.env.API_PORT || 3001)) }
bootstrap()
