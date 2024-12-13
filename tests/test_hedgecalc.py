import pytest
from currencyhedgecalc import CurrencyHedgeCalculator

def test_canonicalize_country_name():
    calc = CurrencyHedgeCalculator()
    assert calc.canonicalize_country_name("UK") == "United Kingdom"
    assert calc.canonicalize_country_name("Turkey") == "Türkiye"

import pytest
from currencyhedgecalc import CurrencyHedgeCalculator


def test_calculate_payable():
    calculator = CurrencyHedgeCalculator()
    result = calculator.calculate_payable(
        1000000,  # Payable amount in foreign currency
        "United Kingdom",  # Domestic country
        "Türkiye"  # Foreign country
    )
    assert "Borrow in DC" in result
    assert "Final Owe in DC" in result
    assert "Effective Forward Rate" in result
    assert result["Borrow in DC"] > 0, "Borrow in DC should be positive"
    assert result["Final Owe in DC"] > 0, "Final Owe in DC should be positive"
    assert result["Effective Forward Rate"] > 0, "Effective Forward Rate should be positive"


def test_calculate_receivable():
    calculator = CurrencyHedgeCalculator()
    result = calculator.calculate_receivable(
        2000000,  # Receivable amount in domestic currency
        "United Kingdom",  # Domestic country
        "Sweden"  # Foreign country
    )
    assert "Borrow in FC" in result
    assert "Final Investment in FC" in result
    assert "Effective Forward Rate" in result
    assert result["Borrow in FC"] > 0, "Borrow in FC should be positive"
    assert result["Final Investment in FC"] > 0, "Final Investment in FC should be positive"
    assert result["Effective Forward Rate"] > 0, "Effective Forward Rate should be positive"


def test_generate_combined_report():
    calculator = CurrencyHedgeCalculator()
    report = calculator.generate_combined_report(
        1500000,  # Transaction amount
        "Norway",  # Domestic country
        "Poland"  # Foreign country
    )
    assert "Key Rates" in report, "Combined report should contain Key Rates section"
    assert "Account Payable Hedging Report" in report, "Report should contain Account Payable Hedging Report"
    assert "Account Receivable Hedging Report" in report, "Report should contain Account Receivable Hedging Report"
    assert "Spot exchange rate" in report, "Report should include spot exchange rate"
    assert "interest rate" in report, "Report should include interest rates"

