# CurrencyHedgeCalculator

## Project Overview

The **CurrencyHedgeCalculator** is a Python package to manage foreign exchange transaction exposure using **money market hedging**. It leverages real-time data from exchange rate and interest rate APIs to calculate hedging strategies for foreign currency **Accounts Payable (AP)** and **Accounts Receivable (AR)**. 

Users can input transaction parameters, including **money amount**, **domestic country name**, **foreign country name**, and the package provides clear calculations and steps to construct a money market hedge decision, inclduing values like present value of transactions, necessary borrowing or investment amounts, and effective forward rates. This package simplifies hedging decisions, ensuring cost predictability and reducing the risks associated with exchange rate fluctuations.

---

## Features

1. Fetches real-time **spot exchange rates** and **interest rates**.
2. Calculates hedging strategies for:
   - **Accounts Payable**: Borrowing in domestic currency.
   - **Accounts Receivable**: Borrowing in foreign currency.
3. Outputs key financial data and effective forward rates.
4. Generates combined reports for both AP and AR.

---

## Installation

Install the package:
```bash
pip install -i https://test.pypi.org/simple/ currencyhedgecalc
```

---

## Setting Up API Keys

To use this tool, you need to provide the API Key of [Exchange Rate](https://www.exchangerate-api.com/docs/overview) and [Interest Rate](https://www.api-ninjas.com/api/interestrate). You can get each API key for free through a free registration.

To use the MoneyMarketHedgeCalculator package, you must set the following environment variables:
- `EXCHANGE_RATE_API_KEY`: Your API key for the Exchange Rate API.
- `INTEREST_RATE_API_KEY`: Your API key for the Interest Rate API.

#### On Windows:
Open the Command Prompt and run:
```shell
setx EXCHANGE_RATE_API_KEY "your_exchange_rate_api_key"
setx INTEREST_RATE_API_KEY "your_interest_rate_api_key"
```

#### On macOS/Linux:
Open the Command Prompt and run:
```shell
export EXCHANGE_RATE_API_KEY="your_exchange_rate_api_key"
export INTEREST_RATE_API_KEY="your_interest_rate_api_key"
```

## User Guide & Vignettes

Example 1: Calculate Payable <br>

```bash
from CurrencyHedgeCalculator import CurrencyHedgeCalculator

hedge_calculator = CurrencyHedgeCalculator()
result = hedge_calculator.calculate_payable(
    payable_amount_fc=1_000_000,
    dc_country="UK",
    fc_country="China"
)
print("Payable Calculation:", result)
```
- Sample Result 1:

```bash
{'Borrow in FC': 103287.34438502754, 'Final Investment in FC': 106489.25206096338, 'Effective Forward Rate': 9.390619059165859}
```

Example 2: Calculate Receivable

```bash
result = hedge_calculator.calculate_receivable(
    receivable_amount_dc=1_000_000,
    dc_country="United Kingdom",
    fc_country="China"
)
print("Receivable Calculation:", result)
```
- Sample Result 2:

```bash
Receivable Calculation: {'Borrow in FC': 103287.34438502754, 'Final Investment in FC': 106489.25206096338, 'Effective Forward Rate': 9.390619059165859}
```


Example 3: Generate Combined Report

```bash
report = hedge_calculator.generate_combined_report(
    money_amount=1_000_000,
    dc_country="uk",
    fc_country="china"
)
print(report)
```
- Sample Result 3:

```bash
        Key Rates:
        - Spot exchange rate (GBP/CNY): 9.2427 (Last updated: Fri, 13 Dec 2024 00:00:01 +0000)
        - United Kingdom interest rate: 4.75% (Last updated: 11-07-2024)
        - China interest rate: 3.10% (Last updated: 10-21-2024)

        
        Account Payable Hedging Report:

        If Account Payable is 1000000 CNY, we should

        1. Borrow the United Kingdom currency (GBP) equivalent to the present value of the China currency (CNY) payable:
        - Present Value of CNY: PV(AP_fc) = 1000000 / (1 + fc_interest_rate) = 96240.6565 CNY
        - Borrowed Amount in GBP: Borrow Needed = PV(AP_fc) * spot_rate = 8964791.4646 GBP

        2. Convert the borrowed GBP into CNY and deposit it at the China interest rate:
        - Deposit grows to 1000000 CNY after one year.

        3. Repay the United Kingdom loan with interest:
        - Total Repayment in GBP: Final Owe = 9390619.0592 GBP

        4. Effective Locked-in Forward Rate:
        - Effective Forward Rate = Final Owe / Payable Amount = 9.3906 GBP/CNY

        
        Account Receivable Hedging Report:

        If Account Receivable is 1000000 GBP, we should

        1. Borrow the China currency (CNY) equivalent to the present value of the United Kingdom currency (GBP) receivable of 1000000 GBP:
        - Present Value of GBP: PV(AR_dc) = 1000000 / (1 + dc_interest_rate) = 96240.6565 GBP
        - Borrowed Amount in CNY: Borrow Needed = PV(AR_dc) / spot_rate = 103287.3444 CNY

        2. Invest the borrowed CNY at the China interest rate:
        - Investment grows to Final Investment = 106489.2521 CNY

        3. Use the receivable 1000000 GBP to settle obligations.

        4. Effective Locked-in Forward Rate:
        - Effective Forward Rate = Receivable / Final Investment = 9.3906 GBP/CNY  
```


For a detailed tutorial and examples, refer to the vignette:
- [Currency HedgeCalc Vignette (Jupyter Notebook)](./vignettes/vignette_hedgecalc.ipynb)

---

## Supported Countries

Since this package is entirely free, only some countries are avaliable.

The following countries are supported for calculations:

- China (CNY)
- Czech Republic (CZK)
- Denmark (DKK)
- Mexico (MXN)
- New Zealand (NZD)
- Norway (NOK)
- Poland (PLN)
- Russia (RUB)
- Sweden (SEK)
- Switzerland (CHF)
- Türkiye (TRY)
- United Kingdom (GBP)


## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`currencyhedgecalc` was created by Fung Chau. It is licensed under the terms of the MIT license.

## Credits

`currencyhedgecalc` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
