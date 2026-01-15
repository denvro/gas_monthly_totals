# Gas Monthly Totals

Small batch processor that scans a folder for `.xlsx` and `.csv` gas usage files, normalises records, and writes per-file monthly totals plus detailed transformed data into an output folder.

Key files

- `gas_monthly_totals.py`         : main script — auto-detects `.xlsx` and `.csv`, parses two supported templates, aggregates by year/month, and writes Excel outputs.
- `.\dist\gas_monthly_totals.exe` : executable distribution (no Python install needed)
- `gasdata_template_1.xlsx`       : example XLSX template included for reference.
- `gasdata_template_2.csv`        : example CSV template (semicolon-delimited) included for reference.
- `requirements.txt`              : Python dependencies; `pandas` and `openpyxl` are required for Excel output.

Requirements

- Python 3.8+
- Install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
```

Quick overview

- The script finds `.xlsx` and `.csv` files in the chosen source folder, normalises each file to a common record format (`date`, `day`, `month`, `year`, `value`), aggregates monthly totals (grouped by `year` and `month`), and writes two Excel files per input file into the output folder:
  - `<original_basename>_monthly_totals.xlsx` — aggregated totals
  - `<original_basename>_details.xlsx` — transformed input with added columns

CLI / Usage

You can run the script with Python or use a built executable (`gas_monthly_totals.exe`) produced by the project build.

Using Python

```powershell
python .\gas_monthly_totals.py [--source|-s <source_folder>] [--output|-o <output_folder>] [--verbose|-v]
```

Using the packaged executable

```powershell
.\gas_monthly_totals.exe -s "C:\path\to\data" -o "C:\path\to\output" -v
```

Options

- `--source`, `-s` : Source folder to scan for `.xlsx` and `.csv`. Default: `./`.
- `--output`, `-o` : Output folder where results are written. Default: `./output/`.
- `--verbose`, `-v` : Enable verbose (debug) logging to see processing details.

Examples

- Process files in the current working folder and write results to `output/`:

```powershell
python .\gas_monthly_totals.py
```

- Process a custom folder and set output location:

```powershell
.\gas_monthly_totals.exe -s "D:\MyGasData" -o "D:\MyGasData\results"
```

Supported input templates

1) Excel (`.xlsx`) — template 1

- Expects the first column to contain a combined date/time string (renamed to `date_time`) and the second column to contain the numeric reading (`value`).
- The script splits the combined date/time into `date` and a `time_slot`, splits the times into `start_time` and `end_time`, parses `date` with `%d.%m.%Y`, and when the `start_time` is before `06:00` attributes the reading to the previous date.

2) CSV (`.csv`, semicolon delimited) — template 2

- Reads CSVs with `;` as delimiter. Expects the second column to be the daylightsaving datetime and the third column the numeric reading in m3.
- Parses the datetime with `%d-%m-%Y %H:%M`, creates `date` and `time`, attributes the reading to the previous day when the hour ≤ 6 for overnight usage, and converts `value` to MWh by multiplying by `0.01055` (conversion used in code).

Notes

- Only `.xlsx` and `.csv` files are processed; other file types are skipped.
- Processing errors for individual files are caught and logged; the batch continues with remaining files.
- Output files are Excel `.xlsx` files written into the folder specified by `--output` (default `output/`).

Suggestions / Next steps

- CSV outputs, single-file processing, or different aggregation, can optionaly be added to `gas_monthly_totals.py`.

License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

