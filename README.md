
> [!WARNING]  
> **⚠️❗☠️  EXPERIMENTAL PLAYGROUND 
>Your warranty is now void. I am not responsible for bricked devices, dead radios, thermonuclear war. YOU are choosing to make these modifications, and if you point the finger at me for messing up your device, I will laugh at you. ☠️❗⚠️**
>
##
### LICENSE: Please refer to LICENSE.md
### GNU General Public License v3: https://www.gnu.org/licenses/gpl-3.0.en.html
##
> [!NOTE]  
> This script is written for converting CHIRP csv export files to Quansheng TK11 import csv files for Quansheng's CPS version 2.6 and above. CAUTION IS ADVISED. CHECK AND RE-CHECK YOUR FREQUENCIES AFTER CONVERSION AND ALL ADDITIONAL SETTINGS
##
### USAGE
- The script produces three output files to try to overcome locale and regional problems in CSV files. Try the "outTK11-commadelim.csv" file first, then the others
 <pre>    outTK11-locale.csv
    outTK11-commadelim.csv
    outTK11-quotes.csv</pre>

- Python needed to be installed in the system
- Place the script in a directory also containing your CHIRP export csv file named "inCHIRP.csv"
- from command in the said directory run
<pre>python convert_chirp_to_tk11.py</pre>

- converted file will be outTK11.csv which can be imported to Quansheng's TK11 CPS. 
- Squelch value is set to all frequencies to "3"
- Power value is set to all frequencies to "Middle"
- ScanList value is set to all frequencies to "1"
- CAUTION IS ADVISED. CHECK AND RE-CHECK YOUR FREQUENCIES AFTER CONVERSION AND ALL ADDITIONAL SETTINGS

