import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

DB_NAME = 'todo_tasks.db'

# Database Setup
def setup_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    due_date TEXT NOT NULL)''')
    conn.commit()
    conn.close()

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced To-Do List Manager")
        self.create_gui()
        self.refresh_tasks()

    def create_gui(self):
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid()

        # Form
        ttk.Label(self.frame, text="Task Title:").grid(row=0, column=0, sticky=tk.W)
        self.title_entry = ttk.Entry(self.frame, width=30)
        self.title_entry.grid(row=0, column=1, columnspan=2)

        ttk.Label(self.frame, text="Priority (1-5):").grid(row=1, column=0, sticky=tk.W)
        self.priority_entry = ttk.Entry(self.frame)
        self.priority_entry.grid(row=1, column=1)

        ttk.Label(self.frame, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W)
        self.date_entry = ttk.Entry(self.frame)
        self.date_entry.grid(row=2, column=1)

        ttk.Button(self.frame, text="Add Task", command=self.add_task).grid(row=3, column=0, pady=5)
        ttk.Button(self.frame, text="Update Task", command=self.update_task).grid(row=3, column=1)
        ttk.Button(self.frame, text="Delete Task", command=self.delete_task).grid(row=3, column=2)

        # Task List
        self.tree = ttk.Treeview(self.frame, columns=('Title', 'Priority', 'Due Date'), show='headings')
        self.tree.heading('Title', text='Title')
        self.tree.heading('Priority', text='Priority')
        self.tree.heading('Due Date', text='Due Date')
        self.tree.grid(row=4, column=0, columnspan=3, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)

        ttk.Button(self.frame, text="Sort by Priority", command=self.sort_by_priority).grid(row=5, column=0)
        ttk.Button(self.frame, text="Sort by Due Date", command=self.sort_by_date).grid(row=5, column=1)

    def execute_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_db(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return rows

    def add_task(self):
        title = self.title_entry.get()
        priority = self.priority_entry.get()
        due_date = self.date_entry.get()

        if not title or not priority or not due_date:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            priority = int(priority)
            datetime.datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid priority or date format.")
            return

        self.execute_db("INSERT INTO tasks (title, priority, due_date) VALUES (?, ?, ?)", 
                        (title, priority, due_date))
        self.clear_inputs()
        self.refresh_tasks()

    def update_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "No task selected.")
            return
        task_id = self.tree.item(selected[0])['values'][0]

        title = self.title_entry.get()
        priority = self.priority_entry.get()
        due_date = self.date_entry.get()

        try:
            priority = int(priority)
            datetime.datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid priority or date format.")
            return

        self.execute_db("UPDATE tasks SET title=?, priority=?, due_date=? WHERE id=?",
                        (title, priority, due_date, task_id))
        self.clear_inputs()
        self.refresh_tasks()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "No task selected.")
            return
        task_id = self.tree.item(selected[0])['values'][0]
        self.execute_db("DELETE FROM tasks WHERE id=?", (task_id,))
        self.clear_inputs()
        self.refresh_tasks()

    def refresh_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.fetch_db("SELECT id, title, priority, due_date FROM tasks")
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def load_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])['values']
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, values[1])
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, values[2])
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, values[3])

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

    def sort_by_priority(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.fetch_db("SELECT id, title, priority, due_date FROM tasks ORDER BY priority ASC")
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def sort_by_date(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.fetch_db("SELECT id, title, priority, due_date FROM tasks ORDER BY due_date ASC")
        for row in rows:
            self.tree.insert('', 'end', values=row)

if __name__ == "__main__":
    setup_db()
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()
