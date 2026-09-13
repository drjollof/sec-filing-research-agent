from src.tools.company_facts import CompanyFactsTool


def main():

    tool = CompanyFactsTool()

    data = tool.get_company_facts("AAPL")

    revenues = (
        data["facts"]["us-gaap"]["Revenues"]
        ["units"]["USD"]
    )

    print(
        f"Total revenue observations: "
        f"{len(revenues)}"
    )

    print("\n2025-related observations:")

    for observation in revenues:

        if (
            observation.get("form") == "10-K"
            and (
                "2025" in observation.get("end", "")
                or observation.get("fy") == 2025
            )
        ):
            print(observation)


if __name__ == "__main__":
    main()