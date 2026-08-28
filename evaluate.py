from copilot import analyze_inquiry, draft_internal_response


test_cases = [
    {
        "name": "Existing Ontario plan",
        "input": (
            "We have 27 employees in Ontario. Our current provider is "
            "Sun Life and our renewal increased significantly."
        ),
        "expected": {
            "employee_count": 27,
            "province": "Ontario",
            "has_existing_plan": True,
            "current_provider": "Sun Life",
            "monthly_budget": None,
            "desired_benefits": [],
            "employee_contribution_percent": None,
            "renewal_date": None,
            "requires_human_review": True
        }
    },
    {
        "name": "New Alberta plan",
        "input": (
            "We are an Alberta company with 14 employees. We do not "
            "currently have an employee benefits plan."
        ),
        "expected": {
            "employee_count": 14,
            "province": "Alberta",
            "has_existing_plan": False,
            "current_provider": None,
            "monthly_budget": None,
            "desired_benefits": [],
            "employee_contribution_percent": None,
            "renewal_date": None
        }
    },
    {
        "name": "Very incomplete inquiry",
        "input": "We want to explore better employee benefits.",
        "expected": {
            "employee_count": None,
            "province": None,
            "has_existing_plan": None,
            "current_provider": None,
            "monthly_budget": None,
            "desired_benefits": [],
            "employee_contribution_percent": None,
            "renewal_date": None,
            "requires_human_review": True
        }
    },
    {
        "name": "Detailed plan comparison",
        "input": (
            "We have 27 employees in Ontario and currently use Sun Life. "
            "Our renewal is October 1, 2026. Our total monthly budget is "
            "$8,000, and the employer pays 75% of the premium. We want "
            "prescription drugs, major dental, vision, and an employee "
            "assistance program. Please compare alternative plans."
        ),
        "expected": {
            "employee_count": 27,
            "province": "Ontario",
            "has_existing_plan": True,
            "current_provider": "Sun Life",
            "monthly_budget": 8000.0,
            "employee_contribution_percent": 25.0,
            "requires_human_review": True
        },
        "required_benefit_groups": [
            ("drug", "prescription"),
            ("dental",),
            ("vision",),
            ("employee assistance", "eap")
        ],
        "renewal_date_required": True,
        "expects_plan_matches": True
    }
]


required_sections = [
    "Summary",
    "Missing Information",
    "Suggested Next Steps",
    "Advisor Review"
]


fictional_plan_names = [
    "Essential Shield",
    "Balanced Choice",
    "Enhanced Plus",
    "FlexCare Modular"
]


def print_check(check_name, passed, expected=None, received=None):
    if passed:
        print(f"PASS: {check_name}")
    else:
        print(f"FAIL: {check_name}")

        if expected is not None:
            print(f"  Expected: {expected}")

        if received is not None:
            print(f"  Received: {received}")


def evaluate_case(test_case):
    print(f"\n{'=' * 60}")
    print(f"Test: {test_case['name']}")

    inquiry = analyze_inquiry(test_case["input"])

    passed_checks = 0
    total_checks = 0

    print("\nStructured Extraction")

    for field, expected_value in test_case["expected"].items():
        actual_value = getattr(inquiry, field)
        passed = actual_value == expected_value

        print_check(
            field,
            passed,
            expected=expected_value,
            received=actual_value
        )

        total_checks += 1
        passed_checks += int(passed)

    # Check desired benefits by meaning rather than exact wording.
    desired_benefit_groups = test_case.get(
        "required_benefit_groups",
        []
    )

    if desired_benefit_groups:
        desired_text = " ".join(inquiry.desired_benefits).lower()

        for alternatives in desired_benefit_groups:
            passed = any(
                term in desired_text
                for term in alternatives
            )

            check_name = (
                "Desired benefit includes "
                f"{' or '.join(alternatives)}"
            )

            print_check(
                check_name,
                passed,
                expected=alternatives,
                received=inquiry.desired_benefits
            )

            total_checks += 1
            passed_checks += int(passed)

    if test_case.get("renewal_date_required"):
        passed = bool(inquiry.renewal_date)

        print_check(
            "Renewal date extracted",
            passed,
            expected="A non-empty renewal date",
            received=inquiry.renewal_date
        )

        total_checks += 1
        passed_checks += int(passed)

    draft, sources, _ = draft_internal_response(
        test_case["input"],
        inquiry
    )

    word_count = len(draft.split())

    report_checks = {
        "180 words or fewer": word_count <= 180,
        "Contains required sections": all(
            section.lower() in draft.lower()
            for section in required_sections
        ),
        "Knowledge-base source cited": bool(sources)
    }

    if test_case.get("expects_plan_matches"):
        report_checks["Contains Potential Plan Matches"] = (
            "potential plan matches" in draft.lower()
        )

        mentioned_plans = [
            plan
            for plan in fictional_plan_names
            if plan.lower() in draft.lower()
        ]

        report_checks["Mentions one or two fictional plans"] = (
            1 <= len(mentioned_plans) <= 2
        )
    else:
        mentioned_plans = []

    print("\nRAG Report")

    for check_name, passed in report_checks.items():
        print_check(check_name, passed)

        total_checks += 1
        passed_checks += int(passed)

    print(f"Word count: {word_count}")

    if mentioned_plans:
        print(f"Plans found: {', '.join(mentioned_plans)}")

    print("\nGenerated report:")
    print(draft)

    if sources:
        print(f"\nSources: {', '.join(sources)}")

    return passed_checks, total_checks


if __name__ == "__main__":
    total_passed = 0
    total_checks = 0

    for test_case in test_cases:
        passed, checks = evaluate_case(test_case)
        total_passed += passed
        total_checks += checks

    score = total_passed / total_checks * 100

    print(f"\n{'=' * 60}")
    print("Final Evaluation Results")
    print(f"Passed: {total_passed}/{total_checks}")
    print(f"Score: {score:.1f}%")