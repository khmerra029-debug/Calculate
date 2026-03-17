class Calculator {
    constructor() {
        this.exprElement = document.getElementById('expression');
        this.resultElement = document.getElementById('result');
        this.expr = "";
        this.result = "0";
        this.justEvaluated = false;

        this.setupEventListeners();
        this.updateDisplay();
    }

    setupEventListeners() {
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                const val = btn.dataset.val;

                if (action === "number") this.appendNumber(val);
                if (action === "operator") this.appendOperator(val);
                if (action === "equals") this.evaluate();
                if (action === "clear") this.clear();
                if (action === "backspace") this.backspace();
                if (action === "toggle") this.toggleSign();

                // Add a small pulse animation to display
                this.pulseDisplay();
            });
        });

        // Keyboard support
        document.addEventListener('keydown', (e) => {
            if (e.key >= '0' && e.key <= '9' || e.key === '.') { this.appendNumber(e.key); this.simulateClickOrPulse(e.key); }
            if (['+', '-', '*', '/', '%'].includes(e.key)) { this.appendOperator(e.key); this.simulateClickOrPulse(e.key); }
            if (e.key === 'Enter' || e.key === '=') { this.evaluate(); this.simulateClickOrPulse('='); }
            if (e.key === 'Backspace') { this.backspace(); this.simulateClickOrPulse('backspace'); }
            if (e.key === 'Escape') { this.clear(); this.simulateClickOrPulse('clear'); }
        });
    }

    simulateClickOrPulse(key) {
        this.pulseDisplay();
        // You would normally trigger the active state style of buttons here too
    }

    pulseDisplay() {
        this.resultElement.style.transform = 'scale(0.98)';
        this.resultElement.style.transition = 'transform 0.05s ease';
        setTimeout(() => {
            this.resultElement.style.transform = 'scale(1)';
        }, 50);
    }

    updateDisplay() {
        this.resultElement.textContent = this.formatNumber(this.result) || "0";
        this.exprElement.textContent = this.expr;
    }

    appendNumber(num) {
        if (this.justEvaluated && num !== ".") {
            this.expr = "";
            this.result = "0";
        }
        this.justEvaluated = false;

        if (num === "." && this.result.includes(".")) return;

        if (this.result === "0" && num !== ".") {
            this.result = num;
        } else {
            this.result += num;
        }

        this.updateDisplay();
    }

    appendOperator(op) {
        this.justEvaluated = false;
        const symMap = { '/': '÷', '*': '×', '-': '−', '+': '+', '%': '%' };
        const displayOp = symMap[op] || op;

        if (this.result === "" && this.expr !== "") {
            // override last operator
            this.expr = this.expr.slice(0, -3) + " " + displayOp + " ";
        } else {
            this.expr += this.result + ` ${displayOp} `;
            this.result = "";
        }
        this.updateDisplay();
    }

    evaluate() {
        if (!this.result && !this.expr) return;

        let fullExpr = this.expr + this.result;
        let evalStr = fullExpr
            .replace(/÷/g, '/')
            .replace(/×/g, '*')
            .replace(/−/g, '-');

        // Handle percentage
        evalStr = evalStr.replace(/(\d+\.?\d*)\s*%/g, '($1/100)');

        try {
            // Use Function instead of eval for safer execution
            let res = new Function('return ' + evalStr)();

            if (res === Infinity || isNaN(res) || res === undefined) {
                this.result = "Error";
            } else {
                // Rounding to avoid floating point noise
                res = Math.round(res * 1e10) / 1e10;
                this.result = String(res);
            }
            this.expr = fullExpr + " =";
            this.justEvaluated = true;
        } catch (e) {
            this.result = "Error";
            this.justEvaluated = true;
        }

        this.updateDisplay();
    }

    clear() {
        this.expr = "";
        this.result = "0";
        this.justEvaluated = false;
        this.updateDisplay();
    }

    backspace() {
        if (this.justEvaluated) {
            this.clear();
            return;
        }
        this.result = this.result.slice(0, -1) || "0";
        this.updateDisplay();
    }

    toggleSign() {
        if (this.result && this.result !== "0") {
            if (this.result.startsWith('-')) {
                this.result = this.result.slice(1);
            } else {
                this.result = '-' + this.result;
            }
            this.updateDisplay();
        }
    }

    formatNumber(str) {
        if (str === "Error") return str;
        try {
            const val = parseFloat(str);
            if (Math.abs(val) >= 1e10 || (Math.abs(val) < 1e-6 && val !== 0)) {
                return val.toExponential(4);
            }
        } catch (e) { }
        return str;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Calculator();
});
