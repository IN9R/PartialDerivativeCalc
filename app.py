from flask import Flask, render_template, request
from sympy import symbols, diff, latex
from latex2sympy2 import latex2sympy

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}

    if request.method == 'POST':
        latex_expr = request.form.get('latex_expr', '')
        var_input = request.form.get('variables', '')
        func_name = request.form.get('func_name', 'f') or 'f'

        try:
            expr = latex2sympy(latex_expr)
            var_names = [v.strip() for v in var_input.split(",") if v.strip()]
            vars_sym = symbols(var_names)

            # Partial derivatives
            partials = {str(v): diff(expr, v) for v in vars_sym}
            partials_latex = {str(v): latex(partials[str(v)]) for v in vars_sym}

            result['original'] = latex(expr)
            result['partials'] = partials_latex
            result['var_names'] = var_names
            result['func_name'] = func_name

            # Uncertainty LaTeX
            uncertainty_terms = [
                f"\\left| {latex(partials[v])} \\right| \\Delta {v}" for v in var_names
            ]
            uncertainty_expr_latex = " + ".join(uncertainty_terms)
            result['uncertainty_expr'] = uncertainty_expr_latex

            # Export LaTeX block for copying
            export_lines = []

            # Function line
            export_lines.append(f"${func_name} = {latex(expr)}$")

            # Derivatives
            for v in var_names:
                export_lines.append(
                    f"$\\frac{{\\partial {func_name}}}{{\\partial {v}}} = {partials_latex[v]}$"
                )

            # Uncertainty expression
            export_lines.append(
                f"$\\Delta {func_name} = {uncertainty_expr_latex}$"
            )

            result['export_latex'] = "\n".join(export_lines)

        except Exception as e:
            result['error'] = str(e)

    return render_template("index.html", result=result)

if __name__ == '__main__':
    app.run(debug=True)
