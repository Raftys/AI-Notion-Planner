import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import ollama
import threading

# Template instruction to always prepend
notion_instruction = """
Create a Notion page for the following project idea.

Output formatting rules:
- Do NOT include any extra text, explanations, or commentary.
- The **first line** must be the project title as heading 1 (# Title).
- All other sections must use heading 2 (## Section).
- Separate sections with ---.
- Content under sections should be plain text, bullet points, or numbered lists. Do not use headings for content.
- Only include ALL the sections listed below in the given order.
- Do NOT number or rename section titles.
- For the To-do list, you MUST format each item as:
  - [ ] Task description

Use the following template as a guide for structure and formatting:

# Title

## Description
description text

---

## To-Do
- [ ] Task
- [ ] Task
- [ ] Task

---

## Bugs
- Bug: Bug Description
- Bug: bug description

---

## Things to be careful about
1. thing to be careful text
2. thing to be careful text
3. thing to be careful text

---

## Later adjustments
- later adjustments text
- later adjustments text
- later adjustments text


Sections to include:
- Description: brief description of the project.
- Progress: If the project idea includes programming language and IDE, list them. If not, suggest two languages and IDEs.
- To-do: List important first steps for the project, using checkboxes (- [ ]).
- Bugs: leave empty initially.
- Things to be careful about: highlight potential pitfalls.
- Later adjustments: include ideas for future improvements.

Project idea:
"""

MAX_TOKENS = 800  # for progress bar scaling

def generate_page():
    idea = input_box.get("1.0", tk.END).strip()
    if not idea:
        messagebox.showwarning("Input Required", "Please enter a project idea.")
        return

    output_box.delete("1.0", tk.END)
    progress_bar["value"] = 0
    progress_label.config(text="0%")
    output_box.insert(tk.END, "🤖 Generating...\n")

    copy_button.config(state="disabled")  # disable copy until finished

    def worker():
        final_prompt = f"{notion_instruction}{idea}"
        response_chunks = []
        tokens_generated = 0

        stream = ollama.chat(
            model="deepseek-r1:1.5b",
            messages=[{"role": "user", "content": final_prompt}],
            stream=True,
            options={"num_predict": MAX_TOKENS},
        )

        for chunk in stream:
            response_chunks.append(chunk["message"]["content"])
            tokens_generated += 1
            progress = min(int((tokens_generated / MAX_TOKENS) * 100), 99)

            # Update progress bar in GUI thread
            progress_bar.after(0, lambda p=progress: update_progress(p))

        try:
            final_response = "".join(response_chunks).split("</think>", 1)[1].strip()
        except:
            final_response = "".join(response_chunks).strip()

        # Finish progress bar
        progress_bar.after(0, lambda: update_progress(100))

        # Show result
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, final_response)

        # Enable copy button
        copy_button.after(0, lambda: copy_button.config(state="normal"))

    threading.Thread(target=worker).start()

def update_progress(value):
    progress_bar["value"] = value
    progress_label.config(text=f"{value}%")
    root.update_idletasks()

def copy_to_clipboard():
    content = output_box.get("1.0", tk.END).strip()
    if not content:
        messagebox.showwarning("Empty", "No content to copy!")
        return
    root.clipboard_clear()
    root.clipboard_append(content)
    root.update()
    messagebox.showinfo("Copied", "✅ Content copied to clipboard!")

# GUI Setup
root = tk.Tk()
root.title("📝 Notion Page Generator")
root.geometry("850x650")

# Input
tk.Label(root, text="Project Idea:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
input_box = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD)
input_box.pack(fill="x", padx=10, pady=5)

# Buttons + Progress
btn_frame = tk.Frame(root)
btn_frame.pack(fill="x", padx=10, pady=5)
tk.Button(btn_frame, text="Generate", command=generate_page, bg="#4CAF50", fg="white").pack(side="left", padx=5)

# Progress bar
progress_frame = tk.Frame(root)
progress_frame.pack(fill="x", padx=10, pady=5)
progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(side="left", padx=5)
progress_label = tk.Label(progress_frame, text="0%")
progress_label.pack(side="left", padx=5)

# Output + Copy button
output_frame = tk.Frame(root)
output_frame.pack(fill="both", expand=True, padx=10, pady=5)

tk.Label(output_frame, text="Generated Notion Page:", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=2)

output_box = scrolledtext.ScrolledText(output_frame, height=20, wrap=tk.WORD)
output_box.pack(fill="both", expand=True, padx=5, pady=(0,5))

copy_button = tk.Button(output_frame, text="📋 Copy", command=copy_to_clipboard, state="disabled", bg="#FF9800", fg="white")
copy_button.pack(anchor="e", padx=5, pady=5)

root.mainloop()