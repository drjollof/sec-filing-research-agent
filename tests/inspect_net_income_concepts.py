from src.tools.company_facts import CompanyFactsTool


COMPANIES = [
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOGL",
    "NVDA",
    "TSLA",
    "JNJ",
    "JPM",
]


def main():
    tool = CompanyFactsTool()

    for ticker in COMPANIES:
        print("\n" + "#" * 100)
        print(f"{ticker}")
        print("#" * 100)

        data = tool.get_company_facts(ticker)
        us_gaap = data.get("facts", {}).get("us-gaap", {})

        matches = []

        for concept_name, concept in us_gaap.items():

            label = concept.get("label") or ""
            name_lower = concept_name.lower()
            label_lower = label.lower()

            # Candidate concepts based on terminology.
            if not any(
                term in name_lower or term in label_lower
                for term in [
                    "netincome",
                    "net income",
                    "profitloss",
                    "profit loss",
                    "netearnings",
                    "net earnings",
                ]
            ):
                continue

            units = concept.get("units", {})

            if "USD" not in units:
                continue

            observations = units["USD"]

            # We only care about annual 10-K duration facts
            # for the company's latest fiscal year.
            annual = []

            for obs in observations:
                if obs.get("form") != "10-K":
                    continue

                if obs.get("fp") != "FY":
                    continue

                if not obs.get("start") or not obs.get("end"):
                    continue

                annual.append(obs)

            if not annual:
                continue

            # Determine the latest annual observation by period end.
            latest = max(
                annual,
                key=lambda obs: obs["end"],
            )

            matches.append(
                (
                    concept_name,
                    label,
                    latest,
                )
            )

        if not matches:
            print("No candidate net-income concepts found.")
            continue

        for concept_name, label, obs in matches:
            print("\n" + "=" * 80)
            print(f"Concept:       {concept_name}")
            print(f"Label:         {label}")
            print(f"Start:         {obs.get('start')}")
            print(f"End:           {obs.get('end')}")
            print(f"Value:         {obs.get('val')}")
            print(f"FY:            {obs.get('fy')}")
            print(f"FP:            {obs.get('fp')}")
            print(f"Form:          {obs.get('form')}")
            print(f"Filed:         {obs.get('filed')}")
            print(f"Accession:     {obs.get('accn')}")


if __name__ == "__main__":
    main()