import os
import math
import json

# --- CONFIGURATION ---
MODE = "DEG"
CHAOS = False
VAR_FILE = ".nex_vars.json"

# Base math setup
CONSTANTS = {"pi": math.pi, "e": math.e, "inf": float('inf'), "ans": 0}

def to_radians(val):
    return math.radians(val) if MODE == "DEG" else val

FUNCTIONS = {
    "sqrt": math.sqrt, "sin": lambda x: math.sin(to_radians(x)),
    "cos": lambda x: math.cos(to_radians(x)), "tan": lambda x: math.tan(to_radians(x)),
    "log": math.log10, "ln": math.log, "abs": abs
}

# --- PERSISTENCE ENGINE ---
def save_vars():
    # Only save user-defined variables
    user_data = {k: v for k, v in CONSTANTS.items() if k not in ["pi", "e", "inf", "ans"]}
    with open(VAR_FILE, "w") as f:
        json.dump(user_data, f)

def load_vars():
    if os.path.exists(VAR_FILE):
        try:
            with open(VAR_FILE, "r") as f:
                data = json.load(f)
                CONSTANTS.update(data)
        except: pass

# --- THE SMART TOKENIZER ---
def tokenize(data):
    data = data.replace(" ", "").lower().replace("%", "/100")
    tokens, temp, i = [], "", 0
    while i < len(data):
        char = data[i]
        # Collect numbers, letters, and underscores
        if char.isdigit() or char == "." or char.isalpha() or char == "_":
            temp += char
        elif char in "+-*/^()!":
            if temp:
                # Check CONSTANTS first (allows variables/overwrites to work)
                if temp in CONSTANTS: tokens.append(str(CONSTANTS[temp]))
                else: tokens.append(temp)
                temp = ""
            
            # Unary minus check
            if char == "-" and (i == 0 or data[i-1] in "+-*/^("):
                temp = "-"
                i += 1
                continue
            
            # Powers
            if char == "*" and i + 1 < len(data) and data[i+1] == "*":
                tokens.append("**"); i += 1
            elif char == "^": tokens.append("**")
            else: tokens.append(char)
        i += 1
    if temp:
        if temp in CONSTANTS: tokens.append(str(CONSTANTS[temp]))
        else: tokens.append(temp)
    return tokens

# --- THE RECURSIVE SOLVER ---
def solve(tokens):
    if not tokens: return 0
    t = list(tokens)
    while "!" in t:
        idx = t.index("!")
        t[idx-1 : idx+1] = [str(math.factorial(int(float(t[idx-1]))))]
    while "(" in t:
        start = -1
        for i in range(len(t)):
            if t[i] == "(": start = i
        end = t.index(")", start)
        inner_val = solve(t[start + 1:end])
        if start > 0 and t[start-1] in FUNCTIONS:
            res = FUNCTIONS[t[start-1]](float(inner_val))
            t[start-1 : end+1] = [str(res)]
        else: t[start : end+1] = [str(inner_val)]
    while "**" in t:
        idx = t.index("**")
        t[idx-1 : idx+2] = [str(float(t[idx-1]) ** float(t[idx+1]))]
    while "*" in t or "/" in t:
        for i in range(len(t)):
            if t[i] in ["*", "/"]:
                n1, n2 = float(t[i-1]), float(t[i+1])
                if t[i] == "/" and n2 == 0: return "CRITICAL ERROR: DIV BY ZERO"
                t[i-1 : i+2] = [str(n1 * n2 if t[i] == "*" else n1 / n2)]
                break
    result = float(t[0])
    for i in range(1, len(t), 2):
        op, n2 = t[i], float(t[i+1])
        result = result + n2 if op == "+" else result - n2
    return result

# --- EXECUTION LOOP ---
load_vars()
os.system('cls' if os.name == 'nt' else 'clear')
print("---CALCULATOR---")
print("Commands: 'deg', 'rad', 'vars', 'chaos', 'reset', 'exit'")

while True:
    try:
        user_input = input(f"\n({MODE}) {'[CHAOS] ' if CHAOS else ''}Math > ").strip()
        if not user_input: continue
        if user_input.lower() == "exit": break
        
        # Mode Controls
        if user_input.lower() in ["deg", "rad"]:
            MODE = user_input.upper(); print(f"Switched to {MODE} mode."); continue
        
        if user_input.lower() == "chaos":
            CHAOS = not CHAOS
            print(f"!! CHAOS MODE {'ENABLED' if CHAOS else 'DISABLED'} !!"); continue

        if user_input.lower() == "vars":
            for k, v in CONSTANTS.items(): print(f"{k} = {v}")
            continue

        if user_input.lower() == "reset":
            if os.path.exists(VAR_FILE): os.remove(VAR_FILE)
            CONSTANTS = {"pi": math.pi, "e": math.e, "inf": float('inf'), "ans": 0}
            print("Memory wiped. Reality restored."); continue

        # Handle Variable Assignment (e.g. radius = 5)
        if "=" in user_input and "==" not in user_input:
            name, expr = user_input.split("=")
            name = name.strip()
            
            # Chaos Check: Prevent numeric redefinition unless Chaos is ON
            is_numeric = name.replace('.', '', 1).replace('-', '', 1).isdigit()
            if not CHAOS and is_numeric:
                print(f"!! ERROR: Reality Protection is ON. Redefining '{name}' requires 'chaos' mode !!")
                continue
                
            if name in FUNCTIONS or name in ["pi", "e", "inf"]:
                print(f"!! ERROR: '{name}' is a protected system name !!"); continue
            
            val = solve(tokenize(expr))
            CONSTANTS[name] = val
            save_vars()
            print(f"Defined: {name} = {val}"); continue

        # Normal Calculation
        ans = solve(tokenize(user_input))
        if isinstance(ans, str):
            print(f"!! {ans} !!")
        else:
            CONSTANTS["ans"] = ans
            display = round(ans, 11)
            print(f"Result: {int(display) if display == int(display) else display}")

    except Exception as e:
        print(f"Error: {e}")
