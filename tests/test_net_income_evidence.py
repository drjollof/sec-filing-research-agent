from src.tools.company_facts import CompanyFactsTool


def main():
    tool = CompanyFactsTool()

    fact = tool.get_metric(
        ticker="AAPL",
        metric="net_income",
        fiscal_year=2025,
        form="10-K",
    )

    print("\n" + "=" * 80)
    print("NET INCOME EVIDENCE")
    print("=" * 80)

    print(f"Company:       {fact.company}")
    print(f"Ticker:        {fact.ticker}")
    print(f"Metric:        {fact.label}")
    print(f"Concept:       {fact.fact_name}")
    print(f"Value:         {fact.value}")
    print(f"Unit:          {fact.unit}")
    print(f"Fiscal year:   {fact.fiscal_year}")
    print(f"Fiscal period: {fact.fiscal_period}")
    print(f"Start:         {fact.period_start}")
    print(f"End:           {fact.period_end}")
    print(f"Form:          {fact.form}")
    print(f"Filing date:   {fact.filing_date}")
    print(f"Accession:     {fact.accession_number}")

    assert fact.fact_name == "NetIncomeLoss"
    assert fact.value == 112010000000
    assert fact.unit == "USD"
    assert fact.fiscal_year == 2025
    assert fact.fiscal_period == "FY"
    assert fact.period_start == "2024-09-29"
    assert fact.period_end == "2025-09-27"
    assert fact.form == "10-K"

    evidence = tool.build_evidence(fact)

    print("\nEvidence dictionary:")
    for key, value in evidence.items():
        print(f"{key}: {value}")

    assert evidence["source"] == "SEC CompanyFacts"
    assert evidence["concept"] == "NetIncomeLoss"
    assert evidence["value"] == 112010000000
    assert evidence["unit"] == "USD"
    assert evidence["fiscal_year"] == 2025
    assert evidence["form"] == "10-K"
    assert evidence["accession_number"] == "0000320193-25-000079"

    print("\nPASS: Net income evidence contains expected provenance.")


if __name__ == "__main__":
    main()