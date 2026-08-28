import streamlit as st

from copilot import (
    analyze_inquiry,
    draft_internal_response,
    answer_follow_up
)


st.set_page_config(
    page_title="Benefits Service Copilot",
    page_icon="📋",
    layout="wide"
)

st.title("Benefits Service Copilot")

st.write(
    "Analyze an employee-benefits inquiry, identify missing information, "
    "and generate a grounded internal response."
)


# Initialize persistent session state
if "inquiry" not in st.session_state:
    st.session_state.inquiry = None

if "draft" not in st.session_state:
    st.session_state.draft = None

if "sources" not in st.session_state:
    st.session_state.sources = []

if "previous_response_id" not in st.session_state:
    st.session_state.previous_response_id = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


inquiry_text = st.text_area(
    "Client inquiry",
    height=180,
    placeholder=(
        "Example: We have 27 employees in Ontario and our current "
        "benefits renewal increased significantly..."
    )
)


# Generate and save a new analysis
if st.button("Analyze inquiry", type="primary"):
    if not inquiry_text.strip():
        st.warning("Enter a client inquiry first.")

    else:
        try:
            with st.spinner("Analyzing inquiry..."):
                inquiry = analyze_inquiry(inquiry_text)

            with st.spinner("Searching the knowledge base..."):
                draft, sources, response_id = draft_internal_response(
                    inquiry_text,
                    inquiry
                )

            # Save results so they survive Streamlit reruns
            st.session_state.inquiry = inquiry
            st.session_state.draft = draft
            st.session_state.sources = sources
            st.session_state.previous_response_id = response_id

            # A new inquiry starts a new conversation
            st.session_state.chat_messages = []

        except Exception as error:
            st.error(f"Unable to analyze the inquiry: {error}")


# Display the saved analysis
if st.session_state.inquiry is not None:
    inquiry = st.session_state.inquiry

    st.subheader("Intake Summary")

    employee_count = (
        str(inquiry.employee_count)
        if inquiry.employee_count is not None
        else "Not provided"
    )

    province = inquiry.province or "Not provided"
    provider = inquiry.current_provider or "Not provided"

    if inquiry.has_existing_plan is True:
        existing_plan = "Yes"
    elif inquiry.has_existing_plan is False:
        existing_plan = "No"
    else:
        existing_plan = "Not provided"

    column1, column2, column3 = st.columns(3)

    column1.metric("Employees", employee_count)
    column2.metric("Province", province)
    column3.metric("Current provider", provider)

    monthly_budget = (
    f"${inquiry.monthly_budget:,.2f}"
    if inquiry.monthly_budget is not None
    else "Not provided"
    )

    employee_contribution = (
        f"{inquiry.employee_contribution_percent:.0f}%"
        if inquiry.employee_contribution_percent is not None
        else "Not provided"
    )

    renewal_date = inquiry.renewal_date or "Not provided"

    column1, column2, column3 = st.columns(3)

    column1.metric("Monthly budget", monthly_budget)
    column2.metric("Employee contribution", employee_contribution)
    column3.metric("Renewal date", renewal_date)

    desired_benefits = (
        ", ".join(inquiry.desired_benefits)
        if inquiry.desired_benefits
        else "Not provided"
    )

    st.write(f"**Desired benefits:** {desired_benefits}")

    st.write(f"**Inquiry type:** {inquiry.inquiry_type}")
    st.write(f"**Existing plan:** {existing_plan}")
    st.write(
        f"**Human review required:** "
        f"{'Yes' if inquiry.requires_human_review else 'No'}"
    )

    st.subheader("Missing Information")

    if inquiry.missing_information:
        for item in inquiry.missing_information:
            st.write(f"- {item}")
    else:
        st.write("No missing information identified.")

    st.subheader("Follow-up Questions")

    if inquiry.follow_up_questions:
        for follow_up_question in inquiry.follow_up_questions:
            st.write(f"- {follow_up_question}")
    else:
        st.write("No follow-up questions required.")

    st.subheader("Grounded Internal Draft")
    st.info("Draft only — human advisor review may be required.")
    st.markdown(st.session_state.draft)

    if st.session_state.sources:
        st.caption(
            f"Sources: {', '.join(st.session_state.sources)}"
        )
    else:
        st.warning("No knowledge-base source was cited.")

    report = (
                f"# Benefits Inquiry Report\n\n"
                f"## Inquiry Type\n{inquiry.inquiry_type}\n\n"
                f"## Internal Draft\n{st.session_state.draft}"
            )
    
    st.download_button(
                label="Download report",
                data=report,
                file_name="benefits_inquiry_report.md",
                mime="text/markdown"
    )
    st.divider()

    st.subheader("Ask a Follow-up Question")

    # Redisplay the conversation after every Streamlit rerun
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask about this inquiry or request a draft..."
    )

    if question:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer, response_id = answer_follow_up(
                        question,
                        st.session_state.previous_response_id
                    )

                st.markdown(answer)

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": answer
            })

            # Continue the conversation from this newest answer
            st.session_state.previous_response_id = response_id

        except Exception as error:
            st.error(f"Unable to answer the follow-up: {error}")

        