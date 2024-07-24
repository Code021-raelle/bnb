def get_currency_symbol(currency_code):
    currency_symbols = {
        'USD': '$',
        'NGN': '₦',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'AUD': '$',
        'CAD': '$',
        'CHF': 'CHF',
        'CNY': '¥',
        'HKD': '$',
        'NZD': '$',
        'SEK': 'kr',
        'SGD': '$',
        'ZAR': 'R'
    }
    return currency_symbols.get(currency_code, currency_code)
