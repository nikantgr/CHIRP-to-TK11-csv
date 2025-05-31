# Copyright 2025 Nikos K. Kantarakias 
# https://www.youtube.com/@NikosKantarakias
# https://www.qrz.com/db/SY1EBE
#
# version 0.0.5
#
# This code are licensed under the GNU General Public License v3 (GPLv3).
# 
# Please refer to LICENSE.md
# 
# Further Information:
# GNU General Public License v3: https://www.gnu.org/licenses/gpl-3.0.en.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ---------------------------------------------------------------------------------


import csv
import os
import locale

# Define input and output files
input_file = "inCHIRP.csv"
output_file = "outTK11.csv"

# Check if input file exists
if not os.path.exists(input_file):
    print(f"Error: Input file {input_file} not found.")
    exit(1)

# Define TK11.csv header
tk11_header = [
    "No.", "Name", "RX Freq[MHZ]", "TX Freq[MHZ]", "QT Encode Type", "QT Encode1",
    "QT Decode Type", "QT Decode", "MSW", "Band", "Powrer", "Busy Lock",
    "ScanList", "Demode", "Freq Reverse", "SQ", "Encrypt", "Signaling Decode",
    "PTTID", "Signal"
]

# Function to determine Band based on Mode
def get_band(mode):
    return "12.5K" if mode == "NFM" else "25K"

# Function to determine DTCS polarity
def get_dtcs_type(polarity_char):
    return "NDCS" if polarity_char == "N" else "IDCS" if polarity_char == "R" else "Null"

# Function to calculate TX frequency
def calculate_tx_freq(frequency, duplex, offset):
    try:
        rx_freq = float(frequency)
        if duplex == "-":
            return f"{rx_freq - float(offset):.5f}"
        elif duplex == "+":
            return f"{rx_freq + float(offset):.5f}"
        elif duplex == "split":
            return f"{float(offset):.5f}"
        elif duplex == "off":
            return "0.15300"
        else:
            return f"{rx_freq:.5f}"
    except (ValueError, TypeError):
        return frequency

# Function to determine tone settings
def get_tone_settings(tone, rtonefreq, ctonefreq, dtcs_code, rx_dtcs_code, dtcs_polarity, cross_mode):
    qt_encode_type = "Null"
    qt_encode1 = "Null"
    qt_decode_type = "Null"
    qt_decode = "Null"

    if tone == "Tone":
        qt_encode_type = "Ctcss"
        qt_encode1 = rtonefreq if rtonefreq else "Null"
    elif tone == "TSQL":
        qt_encode_type = "Ctcss"
        qt_encode1 = ctonefreq if ctonefreq else "Null"
        qt_decode_type = "Ctcss"
        qt_decode = ctonefreq if ctonefreq else "Null"
    elif tone == "DTCS":
        qt_encode_type = get_dtcs_type(dtcs_polarity[0] if dtcs_polarity else "N")
        qt_encode1 = dtcs_code if dtcs_code else "Null"
        qt_decode_type = get_dtcs_type(dtcs_polarity[1] if len(dtcs_polarity) > 1 else "N")
        qt_decode = dtcs_code if dtcs_code else "Null"
    elif tone == "DTCS-R":
        qt_encode_type = get_dtcs_type(dtcs_polarity[0] if dtcs_polarity else "N")
        qt_encode1 = dtcs_code if dtcs_code else "Null"
        qt_decode_type = "IDCS"
        qt_decode = rx_dtcs_code if rx_dtcs_code else "Null"
    elif tone == "Cross" and cross_mode:
        tx_mode, rx_mode = cross_mode.split("->") if "->" in cross_mode else ("None", "None")
        # TX tone
        if tx_mode == "Tone":
            qt_encode_type = "Ctcss"
            qt_encode1 = rtonefreq if rtonefreq else "Null"
        elif tx_mode == "DTCS":
            qt_encode_type = get_dtcs_type(dtcs_polarity[0] if dtcs_polarity else "N")
            qt_encode1 = dtcs_code if dtcs_code else "Null"
        # RX tone
        if rx_mode == "Tone":
            qt_decode_type = "Ctcss"
            qt_decode = ctonefreq if ctonefreq else "Null"
        elif rx_mode == "DTCS":
            qt_decode_type = get_dtcs_type(dtcs_polarity[1] if len(dtcs_polarity) > 1 else "N")
            qt_decode = rx_dtcs_code if rx_dtcs_code else "Null"

    return qt_encode_type, qt_encode1, qt_decode_type, qt_decode

# Function to check if a row is empty (excluding Location)
def is_empty_row(row, fieldnames):
    return all(not row.get(field, "").strip() for field in fieldnames if field != "Location")

# Read CHIRP.csv and collect rows with Location
output_rows = []
location_rows = {}  # Map Location to row
min_location = float('inf')
max_location = -1
fieldnames = None
with open(input_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames
    for row in reader:
        location = row.get("Location", "").strip()
        if location:
            try:
                loc_num = int(location)
                location_rows[loc_num] = row
                min_location = min(min_location, loc_num)
                max_location = max(max_location, loc_num)
            except ValueError:
                print(f"Warning: Invalid Location value '{location}' skipped.")

# Generate output rows for all locations from min to max
row_number = 1  # Start numbering from 1
for loc in range(min_location, max_location + 1):
    if loc not in location_rows:
        # Add empty row for missing Location
        output_rows.append({"No.": str(row_number), "raw": f"{row_number},,,,,,,,,,,,,,,,,,,"})
        row_number += 1
        continue

    # Process existing row
    row = location_rows[loc]
    if is_empty_row(row, fieldnames):
        output_rows.append({"No.": str(row_number), "raw": f"{row_number},,,,,,,,,,,,,,,,,,,"})
        row_number += 1
        continue

    # Extract fields for non-empty row
    name = row.get("Name", "")
    frequency = row.get("Frequency", "0.0")
    duplex = row.get("Duplex", "")
    offset = row.get("Offset", "0.0")
    tone = row.get("Tone", "")
    rtonefreq = row.get("rToneFreq", "")
    ctonefreq = row.get("cToneFreq", "")
    dtcs_code = row.get("DtcsCode", "")
    rx_dtcs_code = row.get("RxDtcsCode", "")
    dtcs_polarity = row.get("DtcsPolarity", "NN")
    cross_mode = row.get("CrossMode", "")
    mode = row.get("Mode", "FM")

    # Assign sequential No.
    no = str(row_number)

    # Calculate RX and TX frequencies
    rx_freq = f"{float(frequency):.5f}" if frequency else "0.0"
    tx_freq = calculate_tx_freq(frequency, duplex, offset)

    # Determine Demode
    valid_modes = {"FM", "AM", "LSB", "USB", "CW"}
    demode = mode if mode in valid_modes else "FM"

    # Determine Band
    band = get_band(mode)

    # Determine tone settings
    qt_encode_type, qt_encode1, qt_decode_type, qt_decode = get_tone_settings(
        tone, rtonefreq, ctonefreq, dtcs_code, rx_dtcs_code, dtcs_polarity, cross_mode
    )

    # Create TK11 row
    tk11_row = {
        "No.": no,
        "Name": name,
        "RX Freq[MHZ]": rx_freq,
        "TX Freq[MHZ]": tx_freq,
        "QT Encode Type": qt_encode_type,
        "QT Encode1": qt_encode1,
        "QT Decode Type": qt_decode_type,
        "QT Decode": qt_decode,
        "MSW": "2K",
        "Band": band,
        "Powrer": "Middle",
        "Busy Lock": "OFF",
        "ScanList": "1",
        "Demode": demode,
        "Freq Reverse": "OFF",
        "SQ": "3",
        "Encrypt": "OFF",
        "Signaling Decode": "OFF",
        "PTTID": "OFF",
        "Signal": "DTMF"
    }
    output_rows.append(tk11_row)
    row_number += 1

# Write to TK11.csv
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=tk11_header)
    writer.writeheader()
    for row in output_rows:
        if "raw" in row:
            csvfile.write(row["raw"] + "\n")
        else:
            writer.writerow(row)

# Define fields to be quoted
quoted_fields = ["RX Freq[MHZ]", "TX Freq[MHZ]", "QT Encode1", "QT Decode", "MSW", "Band"]

# Create a quoted copy of the output file (outTK11-quotes.csv)
quoted_output_file = "outTK11-quotes.csv"
with open(output_file, newline='') as infile, open(quoted_output_file, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    # Write unquoted header
    outfile.write(','.join(tk11_header) + '\n')
    # Write data rows with selective quoting
    for row in reader:
        modified_row = []
        for field in tk11_header:
            value = row[field]
            # Escape commas and quotes in the value
            if ',' in value or '"' in value:
                value = f'"{value.replace('"', '""')}"'
            elif field in quoted_fields:
                value = f'"{value}"'
            modified_row.append(value)
        outfile.write(','.join(modified_row) + '\n')

# Create a quoted copy with comma decimal separators (outTK11-commadelim.csv)
comma_output_file = "outTK11-commadelim.csv"
comma_fields = ["RX Freq[MHZ]", "TX Freq[MHZ]", "QT Encode1", "QT Decode", "MSW", "Band"]
with open(output_file, newline='') as infile, open(comma_output_file, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    # Write unquoted header
    outfile.write(','.join(tk11_header) + '\n')
    # Write data rows with selective quoting and comma decimals
    for row in reader:
        modified_row = []
        for field in tk11_header:
            value = row[field]
            if field in quoted_fields:
                if field in comma_fields and value and value != "Null":
                    value = value.replace('.', ',')
                # Escape commas and quotes in the value
                if ',' in value or '"' in value:
                    value = f'"{value.replace('"', '""')}"'
                else:
                    value = f'"{value}"'
            elif ',' in value or '"' in value:
                value = f'"{value.replace('"', '""')}"'
            modified_row.append(value)
        outfile.write(','.join(modified_row) + '\n')

# Create a quoted copy with locale-specific decimal separators (outTK11-locale.csv)
locale_output_file = "outTK11-locale.csv"
try:
    # Set system default locale
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    print("Warning: Failed to set system locale. Falling back to 'en_US.UTF-8'.")
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        print("Warning: Failed to set 'en_US.UTF-8'. Using default format (period decimals).")

decimal_point = locale.localeconv().get('decimal_point', '.')
locale_numeric_fields = ["RX Freq[MHZ]", "TX Freq[MHZ]", "QT Encode1", "QT Decode"]
with open(output_file, newline='') as infile, open(locale_output_file, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    # Write unquoted header
    outfile.write(','.join(tk11_header) + '\n')
    # Write data rows with selective quoting and locale-specific decimals
    for row in reader:
        modified_row = []
        for field in tk11_header:
            value = row[field]
            if field in quoted_fields:
                if field in locale_numeric_fields and value and value != "Null":
                    value = value.replace('.', decimal_point)
                # Escape commas and quotes in the value
                if ',' in value or '"' in value:
                    value = f'"{value.replace('"', '""')}"'
                else:
                    value = f'"{value}"'
            elif ',' in value or '"' in value:
                value = f'"{value.replace('"', '""')}"'
            modified_row.append(value)
        outfile.write(','.join(modified_row) + '\n')

print(f"Conversion complete. Outputs written to {output_file}, {quoted_output_file}, {comma_output_file}, and {locale_output_file}.")
os.remove(output_file)