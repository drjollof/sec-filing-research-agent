from src.tools.company_facts import CompanyFactsTool


def main():

    tool = CompanyFactsTool()

    data = tool.get_company_facts("AAPL")

    us_gaap = data["facts"]["us-gaap"]

    matches = []

    for concept_name, concept in us_gaap.items():

        label = concept.get("label", "")

        text = (
            f"{concept_name} {label}"
        ).lower()

        if (
            "revenue" in text
            or "sales" in text
            or "net sales" in text
        ):
            matches.append(
                (
                    concept_name,
                    label,
                    concept.get("units", {}),
                )
            )

    print(
        f"Revenue/sales-related concepts: "
        f"{len(matches)}"
    )

    for concept_name, label, units in matches:

        print("\n" + "=" * 80)
        print(f"Concept: {concept_name}")
        print(f"Label:   {label}")
        print(
            f"Units:   {list(units.keys())}"
        )

        for unit, observations in units.items():

            print(
                f"  {unit}: "
                f"{len(observations)} observations"
            )

            for observation in observations:

                if observation.get("form") == "10-K":
                    print(
                        "   ",
                        observation,
                    )


if __name__ == "__main__":
    main()