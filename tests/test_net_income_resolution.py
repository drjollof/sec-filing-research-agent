from src.tools.company_facts import CompanyFactsTool


EXPECTED = {
    "AAPL": {
        "fiscal_year": 2025,
        "value": 112010000000,
        "period_start": "2024-09-29",
        "period_end": "2025-09-27",
    },
    "MSFT": {
        "fiscal_year": 2026,
        "value": 133749000000,
        "period_start": "2025-07-01",
        "period_end": "2026-06-30",
    },
    "AMZN": {
        "fiscal_year": 2025,
        "value": 77670000000,
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
    },
    "GOOGL": {
        "fiscal_year": 2025,
        "value": 132170000000,
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
    },
    "NVDA": {
        "fiscal_year": 2026,
        "value": 120067000000,
        "period_start": "2025-01-27",
        "period_end": "2026-01-25",
    },
    "TSLA": {
        "fiscal_year": 2025,
        "value": 3794000000,
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
    },
    "JNJ": {
        "fiscal_year": 2025,
        "value": 26804000000,
        "period_start": "2024-12-30",
        "period_end": "2025-12-28",
    },
    "JPM": {
        "fiscal_year": 2025,
        "value": 57048000000,
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
    },
}


def main():
    tool = CompanyFactsTool()

    for ticker, expected in EXPECTED.items():
        print("\n" + "=" * 80)
        print(f"{ticker} FY{expected['fiscal_year']}")

        fact = tool.resolve_concept(
            ticker=ticker,
            metric="net_income",
            fiscal_year=expected["fiscal_year"],
            form="10-K",)

        assert fact is not None, (f"{ticker}: No net income fact resolved")

        concept_name, observation, label = fact

        print(f"Concept:       {concept_name}")
        print(f"Label:         {label}")
        print(f"Value:         {observation['val']}")
        print(f"Unit:          USD")
        print(f"Start:         {observation.get('start')}")
        print(f"End:           {observation.get('end')}")
        print(f"Form:          {observation.get('form')}")
        print(f"Filing date:   {observation.get('filed')}")
        print(f"Accession:     {observation.get('accn')}")

    
        assert concept_name == "NetIncomeLoss"
        assert observation['val'] == expected["value"]
        assert observation.get('start') == expected["period_start"]
        assert observation.get('end') == expected["period_end"]
        assert observation.get('form') == "10-K"
        assert observation.get("fp") == "FY"
        assert observation.get("fy") == expected["fiscal_year"]

        print("PASS")


if __name__ == "__main__":
    main()