import { createFileRoute } from '@tanstack/react-router'
import { FormEvent, useEffect, useState } from 'react'
import { todosApi, Todo } from '../lib/todos-api'

export const Route = (createFileRoute as any)('/')({ component: Todos })
function Todos() {
  const [todos, setTodos] = useState<Todo[]>([]), [title, setTitle] = useState(''), [loading, setLoading] = useState(true), [busy, setBusy] = useState<string | null>(null), [error, setError] = useState('')
  useEffect(() => { todosApi.list().then(setTodos).catch(e => setError(e.message)).finally(() => setLoading(false)) }, [])
  async function add(e: FormEvent) { e.preventDefault(); const value = title.trim(); if (!value) { setError('A title is required.'); return }; setBusy('new'); setError(''); try { setTodos([await todosApi.create(value), ...todos]); setTitle('') } catch (e) { setError((e as Error).message) } finally { setBusy(null) } }
  async function toggle(todo: Todo) { setBusy(todo.id); try { const updated = await todosApi.update(todo.id, { completed: !todo.completed }); setTodos(todos.map(x => x.id === todo.id ? updated : x)) } catch (e) { setError((e as Error).message) } finally { setBusy(null) } }
  async function remove(todo: Todo) { setBusy(todo.id); try { await todosApi.remove(todo.id); setTodos(todos.filter(x => x.id !== todo.id)) } catch (e) { setError((e as Error).message) } finally { setBusy(null) } }
  return <main><section className="card"><p className="eyebrow">YOUR DAY, ORGANIZED</p><h1>Simple todos</h1><p className="intro">Keep track of what matters, one task at a time.</p><form onSubmit={add}><label htmlFor="title">New todo</label><div className="add"><input id="title" value={title} onChange={e => setTitle(e.target.value)} placeholder="What needs doing?" disabled={busy === 'new'} /><button disabled={busy === 'new'}>Add</button></div></form>{error && <p role="alert" className="error">{error}</p>}{loading ? <p role="status">Loading todos…</p> : todos.length === 0 ? <p className="empty">Nothing here yet. Add your first todo.</p> : <ul>{todos.map(todo => <li key={todo.id} className={todo.completed ? 'done' : ''}><input type="checkbox" aria-label={`Mark ${todo.title} complete`} checked={todo.completed} onChange={() => toggle(todo)} disabled={busy === todo.id} /><span>{todo.title}</span><button className="delete" onClick={() => remove(todo)} disabled={busy === todo.id} aria-label={`Delete ${todo.title}`}>Delete</button></li>)}</ul>}</section></main>
}
