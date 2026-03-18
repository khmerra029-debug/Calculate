import tkinter as tk
from tkinter import font as tkfont
import math

# ── Palette ──────────────────────────────────────────────────────────────────
BG          = "#0d0d0f"
DISPLAY_BG  = "#111116"
DISPLAY_FG  = "#f0eeff"
EXPR_FG     = "#6b6880"

BTN_NUM_BG  = "#1c1c24"
BTN_NUM_FG  = "#e8e4ff"
BTN_NUM_HOV = "#26263a"

BTN_OP_BG   = "#1a1030"
BTN_OP_FG   = "#b39dff"
BTN_OP_HOV  = "#261848"

BTN_EQ_BG   = "#5b3fff"
BTN_EQ_FG   = "#ffffff"
BTN_EQ_HOV  = "#7256ff"

BTN_CLR_BG  = "#1f1520"
BTN_CLR_FG  = "#ff6b9d"
BTN_CLR_HOV = "#2e1a2e"

RADIUS      = 16   # corner radius (pixels, drawn via canvas)
PAD         = 8
# ─────────────────────────────────────────────────────────────────────────────


def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    """Draw a rounded rectangle on a Canvas."""
    pts = [
        x1+r, y1,  x2-r, y1,
        x2, y1,    x2, y1+r,
        x2, y2-r,  x2, y2,
        x2-r, y2,  x1+r, y2,
        x1, y2,    x1, y2-r,
        x1, y1+r,  x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


class RoundButton(tk.Canvas):
    """A Canvas-based button with a rounded-rectangle background."""

    def __init__(self, master, text, bg, fg, hover, command=None,
                 font=None, width=72, height=72, radius=RADIUS, **kw):
        super().__init__(master, width=width, height=height,
                         bg=BG, highlightthickness=0, **kw)
        self._bg, self._fg, self._hover = bg, fg, hover
        self._cmd = command
        self._width, self._height, self._radius = width, height, radius

        self._rect = rounded_rect(self, 2, 2, width-2, height-2, radius,
                                  fill=bg, outline="")
        self._lbl  = self.create_text(width//2, height//2, text=text,
                                      fill=fg, font=font, anchor="center")

        self.bind("<Enter>",         self._on_enter)
        self.bind("<Leave>",         self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, _):
        self.itemconfig(self._rect, fill=self._hover)

    def _on_leave(self, _):
        self.itemconfig(self._rect, fill=self._bg)

    def _on_press(self, _):
        self.move(self._rect, 0, 2)
        self.move(self._lbl,  0, 2)

    def _on_release(self, _):
        self.move(self._rect, 0, -2)
        self.move(self._lbl,  0, -2)
        if self._cmd:
            self._cmd()


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calc")
        self.resizable(False, False)
        self.configure(bg=BG)

        # State
        self._expr   = ""   # full expression string
        self._result = "0"  # main display
        self._just_evaluated = False

        self._build_fonts()
        self._build_display()
        self._build_buttons()
        self._bind_keyboard()

        # Centre on screen
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    # ── Fonts ─────────────────────────────────────────────────────────────────
    def _build_fonts(self):
        self.f_result = tkfont.Font(family="SF Pro Display",  size=38, weight="bold")
        self.f_expr   = tkfont.Font(family="SF Pro Text",     size=13)
        self.f_btn    = tkfont.Font(family="SF Pro Display",  size=17, weight="bold")
        self.f_btn_sm = tkfont.Font(family="SF Pro Display",  size=14, weight="bold")
        # Fallback if SF Pro not installed
        for f in (self.f_result, self.f_expr, self.f_btn, self.f_btn_sm):
            try:
                f.actual()
            except Exception:
                pass  # tkinter always succeeds; bad family just falls back

    # ── Display ───────────────────────────────────────────────────────────────
    def _build_display(self):
        outer = tk.Frame(self, bg=BG, padx=PAD, pady=PAD)
        outer.pack(fill="x")

        disp = tk.Frame(outer, bg=DISPLAY_BG,
                        highlightbackground="#2a2a3a", highlightthickness=1)
        disp.pack(fill="x")

        # Expression label (small, top)
        self._expr_var = tk.StringVar(value="")
        tk.Label(disp, textvariable=self._expr_var, bg=DISPLAY_BG,
                 fg=EXPR_FG, font=self.f_expr, anchor="e"
                 ).pack(fill="x", padx=16, pady=(12, 0))

        # Result label (big, bottom)
        self._result_var = tk.StringVar(value="0")
        tk.Label(disp, textvariable=self._result_var, bg=DISPLAY_BG,
                 fg=DISPLAY_FG, font=self.f_result, anchor="e"
                 ).pack(fill="x", padx=16, pady=(4, 16))

    # ── Button grid ───────────────────────────────────────────────────────────
    def _build_buttons(self):
        grid = tk.Frame(self, bg=BG)
        grid.pack(padx=PAD, pady=(0, PAD))

        BW, BH = 76, 72   # button width / height
        SP = 8             # spacing

        def num(t): return (BTN_NUM_BG, BTN_NUM_FG, BTN_NUM_HOV, self.f_btn,   BW)
        def op(t):  return (BTN_OP_BG,  BTN_OP_FG,  BTN_OP_HOV,  self.f_btn,   BW)
        def eq(t):  return (BTN_EQ_BG,  BTN_EQ_FG,  BTN_EQ_HOV,  self.f_btn,   BW)
        def cl(t):  return (BTN_CLR_BG, BTN_CLR_FG, BTN_CLR_HOV, self.f_btn_sm, BW)

        layout = [
            # (label, style-fn, command)
            [("C",  cl, self._clear),  ("⌫",  cl, self._backspace),
             ("%",  op, lambda: self._append_op("%")), ("÷",  op, lambda: self._append_op("/"))],
            [("7",  num, lambda: self._append("7")), ("8", num, lambda: self._append("8")),
             ("9",  num, lambda: self._append("9")), ("×", op,  lambda: self._append_op("*"))],
            [("4",  num, lambda: self._append("4")), ("5", num, lambda: self._append("5")),
             ("6",  num, lambda: self._append("6")), ("−", op,  lambda: self._append_op("-"))],
            [("1",  num, lambda: self._append("1")), ("2", num, lambda: self._append("2")),
             ("3",  num, lambda: self._append("3")), ("+", op,  lambda: self._append_op("+"))],
            [("±",  cl,  self._toggle_sign),         ("0", num, lambda: self._append("0")),
             (".",  num, lambda: self._append(".")),  ("=", eq,  self._evaluate)],
        ]

        for r, row in enumerate(layout):
            for c, (label, style_fn, cmd) in enumerate(row):
                bg, fg, hov, fnt, w = style_fn(label)
                btn = RoundButton(grid, text=label, bg=bg, fg=fg, hover=hov,
                                  command=cmd, font=fnt, width=w, height=BH)
                btn.grid(row=r, column=c,
                         padx=SP//2, pady=SP//2,
                         sticky="nsew")

    # ── Keyboard ──────────────────────────────────────────────────────────────
    def _bind_keyboard(self):
        mapping = {
            "0":"0","1":"1","2":"2","3":"3","4":"4",
            "5":"5","6":"6","7":"7","8":"8","9":"9",
            ".":".", "+":"+", "-":"-", "*":"*", "/":"/",
            "Return":None, "KP_Enter":None,
            "BackSpace":None, "Escape":None,
        }
        self.bind("<Key>", self._on_key)

    def _on_key(self, event):
        k = event.keysym
        c = event.char
        if c in "0123456789.":
            self._append(c)
        elif c in "+-*/":
            self._append_op(c)
        elif k in ("Return", "KP_Enter"):
            self._evaluate()
        elif k == "BackSpace":
            self._backspace()
        elif k == "Escape":
            self._clear()
        elif c == "%":
            self._append_op("%")

    # ── Logic ─────────────────────────────────────────────────────────────────
    def _append(self, ch):
        if self._just_evaluated and ch not in ".":
            self._expr   = ""
            self._result = ""
        self._just_evaluated = False
        # Prevent multiple decimals in same number
        if ch == ".":
            # find last number segment
            import re
            nums = re.split(r"[+\-*/]", self._result)
            if nums and "." in nums[-1]:
                return
        if self._result == "0" and ch != ".":
            self._result = ch
        else:
            self._result += ch
        self._result_var.set(self._fmt(self._result))

    def _append_op(self, op):
        self._just_evaluated = False
        sym_map = {"/": "÷", "*": "×", "-": "−", "+": "+", "%": "%"}
        display_op = sym_map.get(op, op)
        # move result into expression
        self._expr  += self._result + f" {display_op} "
        self._result = ""
        self._expr_var.set(self._expr)
        self._result_var.set("0")

    def _evaluate(self):
        if not self._result and not self._expr:
            return
        full_expr = self._expr + self._result
        # Build evaluable string
        eval_str = (full_expr
                    .replace("÷", "/")
                    .replace("×", "*")
                    .replace("−", "-"))
        # Handle % as /100 of the preceding value
        import re
        eval_str = re.sub(r"(\d+\.?\d*)\s*%", r"(\1/100)", eval_str)
        try:
            result = eval(eval_str, {"__builtins__": {}}, {})
            # Avoid floating point noise
            if isinstance(result, float) and result == int(result):
                result = int(result)
            elif isinstance(result, float):
                result = round(result, 10)
            self._expr_var.set(full_expr + " =")
            self._result = str(result)
            self._result_var.set(self._fmt(self._result))
            self._just_evaluated = True
            self._expr = ""
        except ZeroDivisionError:
            self._result_var.set("÷ 0 Error")
            self._expr_var.set(full_expr)
            self._result = ""
            self._expr   = ""
            self._just_evaluated = True
        except Exception:
            self._result_var.set("Error")
            self._result = ""
            self._expr   = ""
            self._just_evaluated = True

    def _clear(self):
        self._expr   = ""
        self._result = "0"
        self._just_evaluated = False
        self._expr_var.set("")
        self._result_var.set("0")

    def _backspace(self):
        if self._just_evaluated:
            self._clear()
            return
        self._result = self._result[:-1] or "0"
        self._result_var.set(self._fmt(self._result))

    def _toggle_sign(self):
        if self._result and self._result != "0":
            if self._result.startswith("-"):
                self._result = self._result[1:]
            else:
                self._result = "-" + self._result
            self._result_var.set(self._fmt(self._result))

    def _fmt(self, s):
        """Auto-shorten huge numbers for display."""
        try:
            val = float(s)
            if abs(val) >= 1e15:
                return f"{val:.6e}"
        except Exception:
            pass
        return s if s else "0"


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
