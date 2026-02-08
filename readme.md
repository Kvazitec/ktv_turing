# KTV_Turing

**KTV_Turing** = Turing machine emulator powered by Python3

This emulator gets the CSV file with program for Turing machine.

### Format of CSV file:
1. **A1 cell is always void**
2. In **first line** lists the symbols, in **first column** lists states
3. At the intersections of the rows and columns there are command like:
   `"new_symbol, action, new_state"`
   or
   `"new_symbol action new_state"`
4. **Permitted actions:** R, L, S (move one cell to the left, move one cell to the right and stop machine accordingly)
   * Symbols can be indicated by any Unicode characters
   * States can be indicated by any combination of Unicode characters

#### Example:
```csv
,l,1,0
q0,"l, R, q1",,
q1,"0, R, q2","1, R, q1","1, L, q2"
q2,"0, L, q1","0, L, q4","0, L, q6"
q3,"1, L, q2","1, R, q3","0, R, q3"
q4,"l, R, q5","0, R, q3",
q5,,"1, S, q0","l, R, q5"
q6,,"1, L, q6","1, L, q7"
q7,,"0, L, q4","0, L, q7"
```

### Setup Parameters:
Before starting work the emulator is requested*:
1. Path to CSV file
2. Void symbol (the symbol for the initial filling of the tape)
3. Initial state
4. Input (the string of the symbols, void symbols are entered automatically)
5. Initial position of the head (it is counted from the leftmost character of the input string, the setting is done using the arrow keys)
6. Delay between steps

All of this parameters or something of this can be set in the configuration file, the path to which will need to be passed as a parameter when starting the emulator.

#### Config Example:
```text
example.csv
l
q0

-1
```
*\*parameters in file lists in this order*
If the line corresponding to any parameter turns out to be empty, the emulator will request data input from stdin to configure this parameter.

### Example of the starting emulator:
**Linux:**
```bash
python3 ktv_turing.py #without config file
python3 ktv_turing.py example.ktc #with config file
```
**Windows:**
```cmd
python ktv_turing.py ::without config file
python ktv_turing.py example.ktc ::with config file
```

### Example step vizualisation:
```text
--- Step 28 | State: [q2] ---
                               ▼
 l  l  l  1  0  0  0  1  1  0  1  1  l  l
```
