from src.tools.company_facts import CompanyFactsTool


def main():

    tool = CompanyFactsTool()

    fact = tool.get_fact(
        ticker="AAPL",
        fact_name="Revenues",
        fiscal_year=2025,
        form="10-K",
    )

    if fact is None:
        print("Fact not found.")
        return

    print("Company:", fact.company)
    print("Ticker:", fact.ticker)
    print("Fact:", fact.fact_name)
    print("Label:", fact.label)
    print("Value:", fact.value)
    print("Unit:", fact.unit)
    print("Fiscal year:", fact.fiscal_year)
    print("Fiscal period:", fact.fiscal_period)
    print("Form:", fact.form)
    print("Filing date:", fact.filing_date)
    print("Accession:", fact.accession_number)


if __name__ == "__main__":
    main()