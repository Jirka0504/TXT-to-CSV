import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import re

def convert_txt_to_csv(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    rows = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = re.split(r"\s{2,}", line)

        if len(parts) < 4:
            continue

        code = parts[0]
        name = parts[1]
        qty = parts[-3]
        price = parts[-2]
        total = parts[-1]

        rows.append([code, name, qty, price, total])

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Kód", "Název", "Množství", "Cena", "Celkem"])
        writer.writerows(rows)

def select_input():
    file = filedialog.askopenfilename(filetypes=[("TXT files", "*.txt")])
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file)

def select_output():
    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file)

def run_conversion():
    input_file = input_entry.get()
    output_file = output_entry.get()

    if not input_file or not output_file:
        messagebox.showerror("Chyba", "Vyber soubory")
        return

    try:
        convert_txt_to_csv(input_file, output_file)
        messagebox.showinfo("Hotovo", "Převod dokončen")
    except Exception as e:
        messagebox.showerror("Chyba", str(e))

root = tk.Tk()
root.title("TXT → CSV převodník")

tk.Label(root, text="TXT soubor:").grid(row=0, column=0)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1)
tk.Button(root, text="Vybrat", command=select_input).grid(row=0, column=2)

tk.Label(root, text="CSV výstup:").grid(row=1, column=0)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1)
tk.Button(root, text="Uložit jako", command=select_output).grid(row=1, column=2)

tk.Button(root, text="Převést", command=run_conversion).grid(row=2, column=1)

root.mainloop()
