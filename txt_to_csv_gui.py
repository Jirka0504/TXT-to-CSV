name: Build TXT to CSV GUI EXE

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: windows-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install PyInstaller
        run: pip install pyinstaller

      - name: Build EXE
        run: pyinstaller --onefile --noconsole txt_to_csv_gui.py

      - name: Upload EXE
        uses: actions/upload-artifact@v4
        with:
          name: txt2csv-gui
          path: dist/txt_to_csv_gui.exe
