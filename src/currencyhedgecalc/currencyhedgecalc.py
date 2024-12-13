import requests
import os
import re
from datetime import datetime

class CurrencyHedgeCalculator:
    """
    A Python package to manage foreign exchange transaction exposure using money market hedging.
    """

    def __init__(self):
        # Fetch API keys from environment variables
        self.exchange_rate_api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        self.interest_rate_api_key = os.getenv("INTEREST_RATE_API_KEY")
        self.cache = {}

        # Validate that API keys are set
        if not self.exchange_rate_api_key or not self.interest_rate_api_key:
            raise ValueError("API keys are missing. Please set 'EXCHANGE_RATE_API_KEY' and 'INTEREST_RATE_API_KEY' as environment variables.")

        # Alternate country names mapping
        self.alternate_country_names = {
            "China": ["China"],
            "Czech Republic": ["Czechia", "Czech Republic", "Czech"],
            "Denmark": ["Denmark"],
            "Mexico": ["Mexico"],
            "New Zealand": ["NZ", "New Zealand"],
            "Norway": ["Norway"],
            "Poland": ["Poland"],
            "Russia": ["Russia", "Russian Federation"],
            "Sweden": ["Sweden"],
            "Switzerland": ["Switzerland"],
            "Türkiye": ["Turkey", "Turkiye", "Türkiye"],
            "United Kingdom": ["UK", "United Kingdom", "Britain", "England"]
        }

    def canonicalize_country_name(self, user_input):
        """
        Match user input to the canonical country name using alternate names and regex.
        """
        user_input = user_input.strip().lower()  # Normalize input to lowercase
        for canonical_name, alternates in self.alternate_country_names.items():
            for alternate in alternates:
                # Use regex to match user input with alternate names
                if re.fullmatch(alternate.lower(), user_input):
                    return canonical_name
        raise ValueError(f"Country '{user_input}' is not recognized. Supported countries: {', '.join(self.alternate_country_names.keys())}")

    def fetch_exchange_rate(self, dc, fc):
        """
        Fetch the spot exchange rate and last updated time between domestic (dc) and foreign (fc) currencies.
        """
        if (dc, fc) in self.cache:
            return self.cache[(dc, fc)], self.cache[(dc, "last_updated")]

        url = f"https://v6.exchangerate-api.com/v6/{self.exchange_rate_api_key}/latest/{dc}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            rates = data.get('conversion_rates', {})
            last_updated = data.get('time_last_update_utc', "Unknown")

            if fc in rates:
                self.cache[(dc, fc)] = rates[fc]
                self.cache[(dc, "last_updated")] = last_updated
                return rates[fc], last_updated
            else:
                raise ValueError(f"Exchange rate for {fc} not found.")
        else:
            raise ConnectionError(f"Failed to fetch exchange rate: {response.status_code} - {response.text}")

    def fetch_interest_rate(self, country):
        """
        Fetch the one-year interest rate and last updated time for a specified country.
        """
        # Validate country using canonicalization
        country = self.canonicalize_country_name(country)

        # Make the API call
        url = f"https://api.api-ninjas.com/v1/interestrate?country={country}"
        headers = {"X-Api-Key": self.interest_rate_api_key}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # Extract the rate from the nested structure
            if "central_bank_rates" in data and len(data["central_bank_rates"]) > 0:
                rate_data = data["central_bank_rates"][0]
                rate = rate_data.get("rate_pct")
                last_updated = rate_data.get("last_updated", "Unknown")
                if rate is not None:
                    return rate, last_updated
            raise ValueError(f"Interest rate for {country} not found in the response.")
        else:
            raise ConnectionError(f"Failed to fetch interest rate: {response.status_code} - {response.text}")

    @staticmethod
    def calculate_present_value(future_value, interest_rate):
        """
        Calculate the present value of an amount using the formula:
        PV = FV / (1 + i)
        """
        return future_value / (1 + interest_rate)

    @staticmethod
    def calculate_forward_rate(final_owe, transaction_amount):
        """
        Calculate the effective forward rate:
        Effective Rate = Final Amount Owed / Transaction Amount
        """
        return final_owe / transaction_amount

    def calculate_payable(self, payable_amount_fc, dc_country, fc_country):
        """
        Perform money market hedge calculations for Account Payable.
        """
        # Canonicalize country names
        dc_country = self.canonicalize_country_name(dc_country)
        fc_country = self.canonicalize_country_name(fc_country)

        # Map countries to currencies
        country_to_currency = {
            "China": "CNY",
            "Czech Republic": "CZK",
            "Denmark": "DKK",
            "Mexico": "MXN",
            "New Zealand": "NZD",
            "Norway": "NOK",
            "Poland": "PLN",
            "Russia": "RUB",
            "Sweden": "SEK",
            "Switzerland": "CHF",
            "Türkiye": "TRY",
            "United Kingdom": "GBP"
        }

        # Derive currencies
        dc = country_to_currency[dc_country]
        fc = country_to_currency[fc_country]

        # Step 1: Fetch interest rates and exchange rate
        fc_rate, _ = self.fetch_interest_rate(fc_country)
        dc_rate, _ = self.fetch_interest_rate(dc_country)
        fc_rate /= 100  # Convert percentage to decimal
        dc_rate /= 100  # Convert percentage to decimal
        spot_rate, _ = self.fetch_exchange_rate(dc, fc)

        # Step 2: Present Value of Payable in foreign currency
        pv_fc = self.calculate_present_value(payable_amount_fc, fc_rate)

        # Step 3: Borrow equivalent in domestic currency
        borrow_needed_dc = pv_fc * spot_rate

        # Step 4: Repay the domestic currency loan
        final_owe_dc = borrow_needed_dc * (1 + dc_rate)

        # Step 5: Effective Forward Rate
        effective_forward_rate = self.calculate_forward_rate(final_owe_dc, payable_amount_fc)

        return {
            "Borrow in DC": borrow_needed_dc,
            "Final Owe in DC": final_owe_dc,
            "Effective Forward Rate": effective_forward_rate
        }

    def calculate_receivable(self, receivable_amount_dc, dc_country, fc_country):
        """
        Perform money market hedge calculations for Account Receivable.
        """
        # Canonicalize country names
        dc_country = self.canonicalize_country_name(dc_country)
        fc_country = self.canonicalize_country_name(fc_country)

        # Map countries to currencies
        country_to_currency = {
            "China": "CNY",
            "Czech Republic": "CZK",
            "Denmark": "DKK",
            "Mexico": "MXN",
            "New Zealand": "NZD",
            "Norway": "NOK",
            "Poland": "PLN",
            "Russia": "RUB",
            "Sweden": "SEK",
            "Switzerland": "CHF",
            "Türkiye": "TRY",
            "United Kingdom": "GBP"
        }

        # Derive currencies
        dc = country_to_currency[dc_country]
        fc = country_to_currency[fc_country]

        # Step 1: Fetch interest rates and exchange rate
        fc_rate, _ = self.fetch_interest_rate(fc_country)
        dc_rate, _ = self.fetch_interest_rate(dc_country)
        fc_rate /= 100  # Convert percentage to decimal
        dc_rate /= 100  # Convert percentage to decimal
        spot_rate, _ = self.fetch_exchange_rate(dc, fc)

        # Step 2: Present Value of Receivable in domestic currency
        pv_dc = self.calculate_present_value(receivable_amount_dc, dc_rate)

        # Step 3: Borrow equivalent in foreign currency
        borrow_needed_fc = pv_dc / spot_rate

        # Step 4: Invest foreign currency at its local interest rate
        final_investment_fc = borrow_needed_fc * (1 + fc_rate)

        # Step 5: Effective Forward Rate
        effective_forward_rate = self.calculate_forward_rate(receivable_amount_dc, final_investment_fc)

        return {
            "Borrow in FC": borrow_needed_fc,
            "Final Investment in FC": final_investment_fc,
            "Effective Forward Rate": effective_forward_rate
        }

    def generate_combined_report(self, money_amount, dc_country, fc_country):
        """
        Generate a combined report for both Account Payable and Account Receivable.
        """
        # Canonicalize country names
        dc_country = self.canonicalize_country_name(dc_country)
        fc_country = self.canonicalize_country_name(fc_country)

        # Map countries to currencies
        country_to_currency = {
            "China": "CNY",
            "Czech Republic": "CZK",
            "Denmark": "DKK",
            "Mexico": "MXN",
            "New Zealand": "NZD",
            "Norway": "NOK",
            "Poland": "PLN",
            "Russia": "RUB",
            "Sweden": "SEK",
            "Switzerland": "CHF",
            "Türkiye": "TRY",
            "United Kingdom": "GBP"
        }

        # Derive currencies
        dc = country_to_currency[dc_country]
        fc = country_to_currency[fc_country]

        # Fetch key rates
        spot_rate, spot_last_updated = self.fetch_exchange_rate(dc, fc)
        dc_rate, dc_last_updated = self.fetch_interest_rate(dc_country)
        fc_rate, fc_last_updated = self.fetch_interest_rate(fc_country)

        # Perform Account Payable calculation
        payable_result = self.calculate_payable(
            payable_amount_fc=money_amount,
            dc_country=dc_country,
            fc_country=fc_country
        )

        # Perform Account Receivable calculation
        receivable_result = self.calculate_receivable(
            receivable_amount_dc=money_amount,
            dc_country=dc_country,
            fc_country=fc_country
        )

        # Format the report
        report = f"""
        Key Rates:
        - Spot exchange rate ({dc}/{fc}): {spot_rate:.4f} (Last updated: {spot_last_updated})
        - {dc_country} interest rate: {dc_rate:.2f}% (Last updated: {dc_last_updated})
        - {fc_country} interest rate: {fc_rate:.2f}% (Last updated: {fc_last_updated})

        
        Account Payable Hedging Report:

        If Account Payable is {money_amount} {fc}, we should

        1. Borrow the {dc_country} currency ({dc}) equivalent to the present value of the {fc_country} currency ({fc}) payable:
        - Present Value of {fc}: PV(AP_fc) = {money_amount} / (1 + fc_interest_rate) = {money_amount / (1 + payable_result['Effective Forward Rate']):.4f} {fc}
        - Borrowed Amount in {dc}: Borrow Needed = PV(AP_fc) * spot_rate = {payable_result['Borrow in DC']:.4f} {dc}

        2. Convert the borrowed {dc} into {fc} and deposit it at the {fc_country} interest rate:
        - Deposit grows to {money_amount} {fc} after one year.

        3. Repay the {dc_country} loan with interest:
        - Total Repayment in {dc}: Final Owe = {payable_result['Final Owe in DC']:.4f} {dc}

        4. Effective Locked-in Forward Rate:
        - Effective Forward Rate = Final Owe / Payable Amount = {payable_result['Effective Forward Rate']:.4f} {dc}/{fc}

        
        Account Receivable Hedging Report:

        If Account Receivable is {money_amount} {dc}, we should

        1. Borrow the {fc_country} currency ({fc}) equivalent to the present value of the {dc_country} currency ({dc}) receivable of {money_amount} {dc}:
        - Present Value of {dc}: PV(AR_dc) = {money_amount} / (1 + dc_interest_rate) = {money_amount / (1 + receivable_result['Effective Forward Rate']):.4f} {dc}
        - Borrowed Amount in {fc}: Borrow Needed = PV(AR_dc) / spot_rate = {receivable_result['Borrow in FC']:.4f} {fc}

        2. Invest the borrowed {fc} at the {fc_country} interest rate:
        - Investment grows to Final Investment = {receivable_result['Final Investment in FC']:.4f} {fc}

        3. Use the receivable {money_amount} {dc} to settle obligations.

        4. Effective Locked-in Forward Rate:
        - Effective Forward Rate = Receivable / Final Investment = {receivable_result['Effective Forward Rate']:.4f} {dc}/{fc}
        """

        return report