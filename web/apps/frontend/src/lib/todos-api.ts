export type Todo = {
  id: string;
  title: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
};
const base = import.meta.env.VITE_API_URL || 'http://localhost:3001';
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!response.ok)
    throw new Error(
      (await response.json().catch(() => null))?.message ||
        `Request failed (${response.status})`,
    );
  return response.status === 204 ? (undefined as T) : response.json();
}
export const todosApi = {
  list: () => request<Todo[]>('/api/todos'),
  create: (title: string) =>
    request<Todo>('/api/todos', {
      method: 'POST',
      body: JSON.stringify({ title }),
    }),
  update: (id: string, data: Partial<Pick<Todo, 'title' | 'completed'>>) =>
    request<Todo>(`/api/todos/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  remove: (id: string) =>
    request<void>(`/api/todos/${id}`, { method: 'DELETE' }),
};
