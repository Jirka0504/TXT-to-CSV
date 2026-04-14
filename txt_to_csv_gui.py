import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


APP_TITLE = "TXT → CSV převodník (bank export)"


def parse_txt(path: str):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        raise ValueError("Vstupní TXT je prázdný.")

    header = lines[0].split(";")
    if len(header) < 6:
        raise ValueError("První řádek TXT nemá očekávaný formát.")

    client_name = header[3].strip()
    bank_account = f"{header[4].strip()}/{header[5].strip()}"

    rows = []
    for line in lines[1:]:
        parts = line.split(";")
        parts += [""] * (10 - len(parts))
        rows.append({
            "id": parts[0].strip(),
            "amount": parts[1].strip(),
            "currency": parts[2].strip(),
            "variable_symbol": parts[3].strip(),
            "timestamp": parts[4].strip(),
            "flag": parts[5].strip(),
            "invoice_no": parts[9].strip(),
        })

    paid_date = ""
    if rows:
        try:
            paid_date = max(
                datetime.strptime(r["timestamp"], "%d.%m.%Y %H:%M")
                for r in rows if r["timestamp"]
            ).strftime("%d.%m.%Y")
        except Exception:
            paid_date = ""

    return {
        "client_name": client_name,
        "bank_account": bank_account,
        "paid_date": paid_date,
        "rows": rows,
    }


def write_csv(path: str, parsed: dict, email: str = ""):
    with open(path, "w", encoding="cp1250", errors="replace", newline="") as f:
        w = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Hlavička podle vzoru
        w.writerow(["General Logistics Systems Czech Republic s.r.o.", "", "", "", "", "", ""])
        w.writerow(["", "", "", "", "", "", ""])
        w.writerow([f"Název klienta: {parsed['client_name']}", "", "", "", "", "", ""])
        w.writerow([f"E-mailová adresa: {email}", "", "", "", "", "", ""])
        w.writerow([f"Bankovní účet: {parsed['bank_account']}", "", "", "", "", "", ""])
        w.writerow([f"Datum odplacení: {parsed['paid_date']}", "", "", "", "", "", ""])
        w.writerow(["", "", "", "", "", "", ""])
        w.writerow(["Journal", "Číslo balíku", "Variabilní symbol", "Datum doručení", "Částka", "", "Název a adresa příjemce"])

        # Data, která v TXT opravdu jsou
        for r in parsed["rows"]:
            w.writerow([
                "",                         # Journal - v TXT není
                "",                         # Číslo balíku - v TXT není
                r["variable_symbol"],       # Variabilní symbol
                "",                         # Datum doručení - v TXT není
                r["amount"],                # Částka
                r["currency"],              # měna
                "",                         # Název a adresa příjemce - v TXT není
            ])


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x520")

        self.txt_path = tk.StringVar()
        self.csv_path = tk.StringVar()
        self.email = tk.StringVar()

        self.client_name = tk.StringVar()
        self.bank_account = tk.StringVar()
        self.paid_date = tk.StringVar()

        self.parsed = None

        self.build_ui()

    def build_ui(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Vstupní TXT:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=self.txt_path, width=80).grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Button(frm, text="Vybrat…", command=self.pick_txt).grid(row=0, column=2, padx=6)

        ttk.Label(frm, text="Výstupní CSV:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=self.csv_path, width=80).grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Button(frm, text="Uložit jako…", command=self.pick_csv).grid(row=1, column=2, padx=6)

        ttk.Separator(frm, orient="horizontal").grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)

        ttk.Label(frm, text="Název klienta:").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=self.client_name, width=80).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(frm, text="E-mailová adresa:").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=self.email, width=80).grid(row=4, column=1, sticky="ew", pady=4)

        ttk.Label(frm, text="Bankovní účet:").grid(row=5, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=self.bank_account, width=80).grid(row=5, column=1, sticky="ew", pady=4)

        ttk.Label(frm, text="Datum odplacení:").grid(row=6, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=self.paid_date, width=80).grid(row=6, column=1, sticky="ew", pady=4)

        note = (
            "Poznámka: TXT neobsahuje Journal, Číslo balíku, Datum doručení ani Název a adresu příjemce.\n"
            "Tyto sloupce proto zůstanou prázdné, pokud nepřidáme další zdroj dat pro doplnění."
        )
        ttk.Label(frm, text=note, foreground="#555").grid(row=7, column=0, columnspan=3, sticky="w", pady=(6, 12))

        self.preview = tk.Text(frm, height=15, wrap="none")
        self.preview.grid(row=8, column=0, columnspan=3, sticky="nsew")

        btns = ttk.Frame(frm)
        btns.grid(row=9, column=0, columnspan=3, sticky="e", pady=12)
        ttk.Button(btns, text="Načíst TXT", command=self.load_txt).pack(side="left", padx=4)
        ttk.Button(btns, text="Převést", command=self.convert).pack(side="left", padx=4)
        ttk.Button(btns, text="Konec", command=self.destroy).pack(side="left", padx=4)

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(8, weight=1)

    def pick_txt(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.txt_path.set(path)

    def pick_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            self.csv_path.set(path)

    def load_txt(self):
        try:
            self.parsed = parse_txt(self.txt_path.get().strip())
        except Exception as e:
            messagebox.showerror("Chyba", str(e))
            return

        self.client_name.set(self.parsed["client_name"])
        self.bank_account.set(self.parsed["bank_account"])
        self.paid_date.set(self.parsed["paid_date"])

        lines = [
            f"Klient: {self.parsed['client_name']}",
            f"Bankovní účet: {self.parsed['bank_account']}",
            f"Datum odplacení: {self.parsed['paid_date']}",
            "",
            "První řádky dat:",
        ]
        for r in self.parsed["rows"][:10]:
            lines.append(
                f"VS={r['variable_symbol']} | částka={r['amount']} {r['currency']} | čas={r['timestamp']} | faktura={r['invoice_no']}"
            )

        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", "\n".join(lines))

    def convert(self):
        if not self.parsed:
            self.load_txt()
            if not self.parsed:
                return

        out = self.csv_path.get().strip()
        if not out:
            messagebox.showerror("Chyba", "Vyber výstupní CSV.")
            return

        self.parsed["client_name"] = self.client_name.get().strip()
        self.parsed["bank_account"] = self.bank_account.get().strip()
        self.parsed["paid_date"] = self.paid_date.get().strip()

        try:
            write_csv(out, self.parsed, self.email.get().strip())
        except Exception as e:
            messagebox.showerror("Chyba", str(e))
            return

        messagebox.showinfo("Hotovo", f"CSV bylo uloženo:\n{out}")


if __name__ == "__main__":
    App().mainloop()
