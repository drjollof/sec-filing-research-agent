from src.tools.company_facts import CompanyFactsTool


def main():
    tool = CompanyFactsTool()

    fact = tool.get_metric(
        ticker="AAPL",
        metric="revenue",
        fiscal_year=2025,
    )

    if fact is None:
        raise AssertionError(
            "Revenue fact was not resolved."
        )

    evidence = tool.build_evidence(fact)

    print("\nSEC CompanyFacts Evidence")
    print("=" * 80)

    for key, value in evidence.items():
        print(f"{key}: {value}")

    # Basic integrity checks
    assert evidence["source"] == "SEC CompanyFacts"
    assert evidence["ticker"] == "AAPL"
    assert evidence["fiscal_year"] == 2025
    assert evidence["form"] == "10-K"
    assert evidence["period_end"] == "2025-09-27"
    assert evidence["value"] == 416161000000
    assert evidence["unit"] == "USD"
    assert evidence["accession_number"] == (
        "0000320193-25-000079"
    )

    print("\nPASS: Evidence contains the expected provenance.")


if __name__ == "__main__":
    main()