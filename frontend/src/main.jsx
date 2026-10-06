import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";

import "./style.css";

const API_URL = import.meta.env.VITE_API_URL || "";

function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");

  async function request(path, options) {
    const response = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!response.ok) {
      const result = await response.json().catch(() => ({}));
      throw new Error(result.error || `Request failed (${response.status})`);
    }
    return response.status === 204 ? null : response.json();
  }

  async function loadTodos() {
    try {
      setTodos(await request("/todos"));
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    if (API_URL) loadTodos();
  }, []);

  async function addTodo(event) {
    event.preventDefault();
    if (!title.trim()) return;
    try {
      await request("/todos", {
        method: "POST",
        body: JSON.stringify({ title: title.trim() }),
      });
      setTitle("");
      await loadTodos();
    } catch (err) {
      setError(err.message);
    }
  }

  async function toggleTodo(todo) {
    try {
      await request(`/todos/${todo.id}`, {
        method: "PATCH",
        body: JSON.stringify({ done: !todo.done }),
      });
      await loadTodos();
    } catch (err) {
      setError(err.message);
    }
  }

  async function deleteTodo(todo) {
    try {
      await request(`/todos/${todo.id}`, { method: "DELETE" });
      await loadTodos();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main>
      <h1>Todos</h1>
      {!API_URL && <p role="status">This image was built without an API URL.</p>}
      {error && <p role="alert">{error}</p>}
      <form onSubmit={addTodo}>
        <label htmlFor="new-todo">Add a todo</label>
        <input
          id="new-todo"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          disabled={!API_URL}
        />
        <button type="submit" disabled={!API_URL || !title.trim()}>
          Add
        </button>
      </form>
      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>
            <label>
              <input
                type="checkbox"
                checked={todo.done}
                onChange={() => toggleTodo(todo)}
              />
              <span className={todo.done ? "done" : ""}>{todo.title}</span>
            </label>
            <button type="button" onClick={() => deleteTodo(todo)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<TodoApp />);
