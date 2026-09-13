from src.tools.company_facts import CompanyFactsTool


def main():
    tool = CompanyFactsTool()

    data = tool.get_company_facts("JPM")
    us_gaap = data.get("facts", {}).get("us-gaap", {})

    for concept_name, concept in us_gaap.items():

        label = concept.get("label", "")

        if "cash" not in concept_name.lower() and "cash" not in label.lower():
            continue

        units = concept.get("units", {})

        if "USD" not in units:
            continue

        observations = units["USD"]

        annual = [
            obs
            for obs in observations
            if obs.get("form") == "10-K"
            and obs.get("end")
        ]

        if not annual:
            continue

        latest = max(
            annual,
            key=lambda obs: obs["end"],
        )

        print("\n" + "=" * 80)
        print(f"Concept: {concept_name}")
        print(f"Label:   {label}")
        print(f"End:     {latest.get('end')}")
        print(f"Value:   {latest.get('val')}")
        print(f"FY:      {latest.get('fy')}")
        print(f"FP:      {latest.get('fp')}")
        print(f"Form:    {latest.get('form')}")
        print(f"Filed:   {latest.get('filed')}")
        print(f"Accn:    {latest.get('accn')}")


if __name__ == "__main__":
    main()