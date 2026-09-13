from src.tools.company_facts import CompanyFactsTool


def main():

    tool = CompanyFactsTool()

    ticker = "AAPL"

    print(
        f"Retrieving CompanyFacts for {ticker}..."
    )

    data = tool.get_company_facts(ticker)

    print(
        f"Entity: {data['entityName']}"
    )

    print(
        "Available namespaces:",
        list(data["facts"].keys()),
    )

    us_gaap = data["facts"]["us-gaap"]

    print(
        f"Number of US-GAAP concepts: "
        f"{len(us_gaap)}"
    )

    for concept in [
        "Revenues",
        "ProfitLoss",
        "Assets",
    ]:

        print("\n" + "=" * 80)
        print(f"CONCEPT: {concept}")
        print("=" * 80)

        if concept not in us_gaap:
            print("Concept not found.")
            continue

        fact = us_gaap[concept]

        print(
            f"Label: {fact.get('label')}"
        )

        print(
            f"Units: "
            f"{list(fact.get('units', {}).keys())}"
        )

        for unit, observations in fact.get(
            "units",
            {}
        ).items():

            print(
                f"\nUnit: {unit}"
            )

            for observation in observations[-5:]:

                print(
                    observation
                )


if __name__ == "__main__":
    main()