import os

from src.agent.generator import OpenRouterGenerator


def test_missing_api_key():
    original_key = os.environ.pop(
        "OPENROUTER_API_KEY",
        None,
    )

    try:
        try:
            OpenRouterGenerator(
                model="test-model",
                api_key=None,
            )
        except ValueError as exc:
            assert "OPENROUTER_API_KEY" in str(exc)
        else:
            raise AssertionError(
                "Expected missing API key to raise ValueError."
            )
    finally:
        if original_key is not None:
            os.environ["OPENROUTER_API_KEY"] = original_key


def test_generator_initializes_with_explicit_key():
    generator = OpenRouterGenerator(
        model="test-model",
        api_key="test-key",
    )

    assert generator.model == "test-model"
    assert generator.client is not None



def run_tests():
    tests = [
        test_missing_api_key,
        test_generator_initializes_with_explicit_key,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print(f"PASS: {passed}/{len(tests)} generator cases passed.")


if __name__ == "__main__":
    run_tests()