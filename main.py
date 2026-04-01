import json
import threading
import tkinter as tk
import tkinter.filedialog as fd
import anthropic

BG = "#000000"
USER_COLOR = "#00ff41"
CLAUDE_COLOR = "#00cc33"
INPUT_BG = "#000000"
FONT = ("Segoe UI", 11)

key = open("key.txt").read().strip()
client = anthropic.Anthropic(api_key=key)
messages = []

def send(event=None):
    text = input_var.get().strip()
    if not text or busy:
        return
    input_var.set("")

    if text == "/export":
        export_conversation()
        return
    if text == "/load":
        load_conversation()
        return

    append_user_message(text)
    messages.append({"role": "user", "content": text})
    set_busy(True)
    threading.Thread(target=stream_response, daemon=True).start()


def export_conversation():
    if not messages:
        system_message("Nothing to export.")
        return
    path = fd.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        title="Export conversation",
    )
    if not path:
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    system_message(f"Exported to {path}")


def load_conversation():
    path = fd.askopenfilename(
        filetypes=[("JSON files", "*.json")],
        title="Load conversation",
    )
    if not path:
        return
    with open(path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    messages.clear()
    messages.extend(loaded)
    chat.config(state="normal")
    chat.delete("1.0", "end")
    chat.config(state="disabled")
    for msg in messages:
        if msg["role"] == "user":
            append_user_message(msg["content"])
        else:
            chat.config(state="normal")
            chat.insert("end", "Claude\n", "claude_name")
            chat.insert("end", msg["content"] + "\n\n", "claude_body")
            chat.config(state="disabled")
    system_message(f"Loaded {path}")


def system_message(text):
    chat.config(state="normal")
    chat.insert("end", f"{text}\n\n", "system_msg")
    chat.see("end")
    chat.config(state="disabled")

def stream_response():
    chat.config(state="normal")
    chat.insert("end", "Claude\n", "claude_name")
    chat.config(state="disabled")

    response_text = ""
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=16000,
        messages=messages,
    ) as stream:
        for chunk in stream.text_stream:
            response_text += chunk
            chat.config(state="normal")
            chat.insert("end", chunk, "claude_body")
            chat.see("end")
            chat.config(state="disabled")

    chat.config(state="normal")
    chat.insert("end", "\n\n", "claude_body")
    chat.config(state="disabled")
    messages.append({"role": "assistant", "content": response_text})
    set_busy(False)

def append_user_message(text):
    chat.config(state="normal")
    chat.insert("end", "You\n", "user_name")
    chat.insert("end", f"{text}\n\n", "user_body")
    chat.see("end")
    chat.config(state="disabled")

def set_busy(state):
    global busy
    busy = state
    send_btn.config(state="disabled" if state else "normal")
    input_box.config(state="disabled" if state else "normal")
    if not state:
        input_box.focus()

busy = False

root = tk.Tk()
root.title("Claude")
root.configure(bg=BG)
root.geometry("700x520")
root.minsize(400, 300)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

chat = tk.Text(
    root, bg=BG, fg=CLAUDE_COLOR, font=FONT,
    wrap="word", bd=0, padx=16, pady=12,
    relief="flat", state="disabled", cursor="arrow",
    selectbackground="#003b00",
)
chat.grid(row=0, column=0, sticky="nsew")

scrollbar = tk.Scrollbar(root, command=chat.yview, bg=BG, troughcolor=BG, bd=0, width=8)
scrollbar.grid(row=0, column=1, sticky="ns")
chat.config(yscrollcommand=scrollbar.set)

chat.tag_config("claude_name", foreground=CLAUDE_COLOR, font=(FONT[0], FONT[1], "bold"), justify="left")
chat.tag_config("claude_body", foreground=CLAUDE_COLOR, justify="left")
chat.tag_config("user_name", foreground=USER_COLOR, font=(FONT[0], FONT[1], "bold"), justify="right")
chat.tag_config("user_body", foreground=USER_COLOR, justify="right")
chat.tag_config("system_msg", foreground="#006600", justify="center", font=(FONT[0], 9, "italic"))

bottom = tk.Frame(root, bg=INPUT_BG, pady=10, padx=10)
bottom.grid(row=1, column=0, columnspan=2, sticky="ew")
bottom.columnconfigure(0, weight=1)

input_var = tk.StringVar()
input_box = tk.Entry(
    bottom, textvariable=input_var, bg=INPUT_BG, fg=USER_COLOR,
    font=FONT, bd=0, insertbackground=USER_COLOR,
    relief="flat", disabledbackground=INPUT_BG, disabledforeground=USER_COLOR,
)
input_box.grid(row=0, column=0, sticky="ew", ipady=6)
input_box.bind("<Return>", send)
input_box.focus()

send_btn = tk.Button(
    bottom, text="Send", command=send,
    bg="#000000", fg=USER_COLOR, font=FONT,
    activebackground="#003b00", activeforeground=USER_COLOR,
    relief="flat", bd=0, padx=12, cursor="hand2",
)
send_btn.grid(row=0, column=1, padx=(8, 0))
root.mainloop()