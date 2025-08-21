# --- Math Parsing and Solving Utilities ---
from sympy import sympify, Eq, solve, Symbol, Derivative, Integral, latex

def parse_equation(equation_str: str):
    """
    Parse a normalized equation string into a SymPy Eq object or expression.
    Returns None if parsing fails.
    """
    # Try to split at '='
    if '=' in equation_str:
        left, right = equation_str.split('=', 1)
        try:
            left_expr = sympify(left.strip())
            right_expr = sympify(right.strip())
            return Eq(left_expr, right_expr)
        except Exception:
            return None
    else:
        # Not an equation, just an expression
        try:
            expr = sympify(equation_str.strip())
            return expr
        except Exception:
            return None

def solve_equation(eq, var: str = None):
    """
    Solve a SymPy Eq or expression for the given variable (if provided).
    Returns the solution(s) or None if not solvable.
    """
    try:
        if isinstance(eq, Eq):
            if var:
                sym = Symbol(var)
                return solve(eq, sym)
            else:
                return solve(eq)
        else:
            # Just an expression, not an equation
            return None
    except Exception:
        return None

def compute_derivative(expr_str: str, var: str = 't'):
    """
    Compute the derivative of the given expression string with respect to var.
    Returns the derivative as a SymPy expression or None.
    """
    try:
        expr = sympify(expr_str)
        sym = Symbol(var)
        deriv = Derivative(expr, sym).doit()
        return deriv
    except Exception:
        return None

def compute_integral(expr_str: str, var: str = 't'):
    """
    Compute the indefinite integral of the given expression string with respect to var.
    Returns the integral as a SymPy expression or None.
    """
    try:
        expr = sympify(expr_str)
        sym = Symbol(var)
        integ = Integral(expr, sym).doit()
        return integ
    except Exception:
        return None

def to_latex(expr) -> str:
    """
    Convert a SymPy expression or equation to LaTeX string.
    """
    try:
        return latex(expr)
    except Exception:
        return str(expr)
import re
from typing import Tuple

# Mapping of spoken math phrases to symbols
MATH_PHRASE_MAP = [
    # Functions and parentheses
    (r"([a-zA-Z]) of ([a-zA-Z])", lambda m: f"{m.group(1)}({m.group(2)})"),
    (r"([a-zA-Z]) open parenthesis ([a-zA-Z]) close parenthesis", lambda m: f"{m.group(1)}({m.group(2)})"),
    # Exponents
    (r"([a-zA-Z0-9]+) to the power of ([0-9]+)", lambda m: f"{m.group(1)}^{m.group(2)}"),
    (r"([a-zA-Z]) squared", lambda m: f"{m.group(1)}²"),
    (r"([a-zA-Z]) cubed", lambda m: f"{m.group(1)}³"),
    # Fractions
    (r"([a-zA-Z0-9]+) over ([a-zA-Z0-9]+)", lambda m: f"{m.group(1)}/{m.group(2)}"),
    # Roots
    (r"square root of ([a-zA-Z0-9]+)", lambda m: f"√{m.group(1)}"),
    (r"cube root of ([a-zA-Z0-9]+)", lambda m: f"∛{m.group(1)}"),
    # Integrals and derivatives
    (r"integral of ([a-zA-Z]) of ([a-zA-Z]) d([a-zA-Z])", lambda m: f"∫{m.group(1)}({m.group(2)}) d{m.group(3)}"),
    (r"derivative of ([a-zA-Z]) of ([a-zA-Z])", lambda m: f"d/d{m.group(2)} {m.group(1)}({m.group(2)})"),
    # Trigonometry
    (r"sine of ([a-zA-Z0-9]+)", lambda m: f"sin({m.group(1)})"),
    (r"cosine of ([a-zA-Z0-9]+)", lambda m: f"cos({m.group(1)})"),
    (r"tangent of ([a-zA-Z0-9]+)", lambda m: f"tan({m.group(1)})"),
    # Arithmetic
    (r"plus", lambda m: "+"),
    (r"minus", lambda m: "-"),
    (r"times", lambda m: "×"),
    (r"multiplied by", lambda m: "×"),
    (r"divided by", lambda m: "÷"),
    (r"equals", lambda m: "="),
    # Inequalities
    (r"greater than or equal to", lambda m: "≥"),
    (r"less than or equal to", lambda m: "≤"),
    (r"greater than", lambda m: ">"),
    (r"less than", lambda m: "<"),
    # Greek letters
    (r"pi", lambda m: "π"),
    (r"theta", lambda m: "θ"),
    (r"alpha", lambda m: "α"),
    (r"beta", lambda m: "β"),
    (r"gamma", lambda m: "γ"),
    (r"delta", lambda m: "δ"),
]

def normalize_math_phrases(text: str) -> Tuple[str, bool]:
    """
    Replace spoken math phrases in text with their symbolic forms.
    Returns the normalized text and a boolean indicating if math was detected.
    """
    math_found = False
    for pattern, repl in MATH_PHRASE_MAP:
        # Apply repeatedly to handle multiple matches in a string
        while True:
            new_text, n = re.subn(pattern, repl, text, flags=re.IGNORECASE)
            if n == 0:
                break
            math_found = True
            text = new_text
    return text, math_found
