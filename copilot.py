from openai import OpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")
if not VECTOR_STORE_ID:
    raise RuntimeError(
        "OPENAI_VECTOR_STORE_ID is missing from the environment."
    )


client = OpenAI()


user_text = """
We operate a plumbing company with 27 employees in Ontario.
We currently have a Sun Life benefits plan, but our renewal
cost increased significantly. We want to compare alternatives.
"""

class BenefitsInquiry(BaseModel): #Structures the data
    inquiry_type: str
    employee_count: int | None
    province: str | None
    has_existing_plan: bool | None
    current_provider: str | None
    missing_information: list[str]
    requires_human_review: bool
    follow_up_questions: list[str]
    monthly_budget: float | None
    desired_benefits: list[str]
    employee_contribution_percent: float | None
    renewal_date: str | None

def analyze_inquiry(inquiry):
    response = client.responses.parse(
        model = "gpt-5.6-luna",
        reasoning={"effort":"high"},
        instructions=(
            "You analyze employee-benefits inquiries for an internal service team. "
            "Extract only information explicitly provided in the inquiry. "
            "Use null when information was not provided. "
            "The employee_contribution_percent field must always represent the "
            "employee's share of the monthly premium, never the employer's share. "
            "If only the employer contribution is provided, calculate the employee "
            "contribution as 100 minus the employer contribution. "
            "For example, if the employer pays 75%, return 25 for "
            "employee_contribution_percent. If the employee pays 40%, return 40. "
            "Return null only when neither percentage is provided. "
            "Identify important information that is still missing. "
            "Do not provide financial, legal, coverage, or eligibility decisions."
            "Set requires_human_review to true when the inquiry requests "
            "plan or provider comparisons, renewal or pricing analysis, "
            "coverage or eligibility advice, or when the request is too vague "
            "to determine a safe next action. Set it to false only for clear, "
            "routine administrative requests that require no professional judgment."
        ),
        input = inquiry,
        text_format=BenefitsInquiry
    )
    return response.output_parsed

def draft_internal_response(inquiry_text: str, inquiry: BenefitsInquiry) -> tuple[str, list[str], str]:
    response = client.responses.create(
            model = "gpt-5.6-luna",
            reasoning={"effort":"high"},
            text={"verbosity": "low"},
            instructions=(
            "You are an internal employee-benefits service copilot. "
            "Use file search before drafting the response. "
            "Base all procedural guidance on the retrieved knowledge-base content. "
            "If the knowledge base does not contain enough information, say so. "
            "Do not invent pricing, coverage, eligibility rules, or provider recommendations. "
            "Write an internal draft with these sections: Summary, "
            "Missing Information, Suggested Next Steps, and Advisor Review. The draft must contain these sections exactly."
            "If the inquiry involves comparing, replacing, renewing, or selecting a"
            "benefits plan, include a section titled 'Potential Plan Matches'."

            "Identify no more than two potential matches from the fictional plan"
            "catalogue in the knowledge base. For each match, explain why it may fit,"
            "its important trade-offs, and which assumptions still require"
            "verification."

            "Never invent a plan, provider, price, eligibility rule, or coverage"
            "detail. Do not describe a potential match as a final recommendation or"
            "binding quote. State clearly that a qualified benefits advisor must"
            "review the result."
            "Keep output response below 180 words. THIS IS NON-NEGOTIABLE"
        ),

        input=(
            f"Original client inquiry:\n{inquiry_text}\n\n"
            f"Structured intake:\n{inquiry.model_dump_json(indent=2)}"
        ),
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [VECTOR_STORE_ID],
                "max_num_results": 10
            }
        ]
    )

    sources = set()

    for output_item in response.output: #Associates output with source
        if output_item.type != "message":
            continue

        for content_item in output_item.content:
            if content_item.type != "output_text":
                continue

            for annotation in content_item.annotations:
                if annotation.type == "file_citation":
                    sources.add(annotation.filename)

    return response.output_text, sorted(sources), response.id
    

def answer_follow_up(follow_up: str, previous_response_id: str) -> tuple[str, str]:
    response = client.responses.create(
            model = "gpt-5.6-luna",
            reasoning={"effort":"high"},
            previous_response_id=previous_response_id,
            text={"verbosity": "medium"},
            instructions=(
            "You are an internal employee-benefits service copilot. "
            "Answer questions about the previously analyzed client inquiry. "
            "Use file search for procedural or benefits-related guidance. "
            "Do not invent pricing, coverage, eligibility rules, or provider "
            "recommendations. Keep answers concise and identify when advisor "
            "review is required."
            
        ),
        input= follow_up,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [VECTOR_STORE_ID],
                "max_num_results": 3
            }
        ]
    )
    return response.output_text, response.id

def display_report(inquiry: BenefitsInquiry):
    print("\n--- BENEFITS SERVICE INTAKE ---")
    print(f"Inquiry type: {inquiry.inquiry_type}")
    print(f"Employee count: {inquiry.employee_count}")
    print(f"Province: {inquiry.province}")
    print(f"Existing plan: {inquiry.has_existing_plan}")
    print(f"Current provider: {inquiry.current_provider}")
    print(f"Human review required: {inquiry.requires_human_review}")

    print("\nMissing information:")
    for item in inquiry.missing_information:
        print(f"- {item}")

    print("\nRecommended follow-up questions:")
    for question in inquiry.follow_up_questions:
        print(f"- {question}")

if __name__ == "__main__":
    inquiry = analyze_inquiry(user_text)
    display_report(inquiry)

    draft, sources, _ = draft_internal_response(user_text, inquiry)
    print(draft)
    print(f"\nSources: {', '.join(sources)}")


