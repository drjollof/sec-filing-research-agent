from src.config import COMPANIES
from src.tools.company_facts import CompanyFactsTool


CANDIDATE_CONCEPTS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
    "SalesRevenueGoodsNet",
    "SalesRevenueServicesNet",
]


def main():
    tool = CompanyFactsTool()

    for ticker in COMPANIES:
        print("\n" + "=" * 90)
        print(ticker)
        print("=" * 90)

        data = tool.get_company_facts(ticker)
        us_gaap = data.get("facts", {}).get("us-gaap", {})

        found = False

        for concept_name in CANDIDATE_CONCEPTS:

            if concept_name not in us_gaap:
                continue

            concept = us_gaap[concept_name]
            units = concept.get("units", {})

            if "USD" not in units:
                continue

            observations = units["USD"]

            annual = [
                obs
                for obs in observations
                if obs.get("form") == "10-K"
                and obs.get("fp") == "FY"
                and obs.get("start")
                and obs.get("end")
            ]

            if not annual:
                continue

            latest = max(
                annual,
                key=lambda obs: obs.get("end", "")
            )

            print(f"\nConcept: {concept_name}")
            print(f"Label:   {concept.get('label', '')}")
            print(f"Start:   {latest.get('start')}")
            print(f"End:     {latest.get('end')}")
            print(f"Value:   {latest.get('val')}")
            print(f"FY:      {latest.get('fy')}")
            print(f"FP:      {latest.get('fp')}")
            print(f"Form:    {latest.get('form')}")
            print(f"Filed:   {latest.get('filed')}")
            print(f"Accn:    {latest.get('accn')}")

            found = True

        if not found:
            print("No candidate revenue concept found.")


if __name__ == "__main__":
    main()