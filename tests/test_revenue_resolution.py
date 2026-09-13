from src.tools.company_facts import CompanyFactsTool


TEST_CASES = [
    ("AAPL", 2025),
    ("GOOGL", 2025),
    ("JPM", 2025),
    ("MSFT", 2025),
    ("TSLA", 2025),
]


def main():
    tool = CompanyFactsTool()

    for ticker, fiscal_year in TEST_CASES:

        fact = tool.get_metric(
            ticker=ticker,
            metric="revenue",
            fiscal_year=fiscal_year,
        )

        print("\n" + "=" * 80)
        print(f"{ticker} FY{fiscal_year}")

        if fact is None:
            print("FAILED: No revenue fact resolved.")
            continue

        print(f"Concept:  {fact.fact_name}")
        print(f"Value:    {fact.value}")
        print(f"Unit:     {fact.unit}")
        print(f"Period:   {fact.period_start} → {fact.period_end}")
        print(f"Form:     {fact.form}")
        print(f"Filed:    {fact.filing_date}")
        print(f"Accn:     {fact.accession_number}")


if __name__ == "__main__":
    main()