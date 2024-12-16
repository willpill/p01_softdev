from flask import Blueprint, render_template, request
import money
from auth_utils import login_required

currency_bp = Blueprint('currency_bp', __name__)

@currency_bp.route('/currency_exchange', methods=['GET', 'POST'])
@login_required
def currency_exchange():
    message = None

    if request.method == 'POST':
        try:
            base_currency = request.form['base_currency']
            target_currency = request.form['target_currency']
            amount = float(request.form['amount'])

            if amount <= 0:
                raise ValueError("Amount must be a positive number.")
            if amount > 1_000_000_000_000:
                raise ValueError("Amount is too large. Maximum allowed is 1,000,000,000,000.")

            converted_amount = money.convert_currency(amount, base_currency, target_currency)

            converted_amount = round(converted_amount, 3)
            
            message = f"{amount} {base_currency} to {target_currency} is {converted_amount}"
        except ValueError as e:
            message = f"Error: {str(e)}"
        except (TypeError, Exception):
            message = "Invalid input or conversion error."

    return render_template('currency_exchange.html', result=message)