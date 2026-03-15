"""
Explain Referral Agent: given plan benefits and optional provider, returns a short
"Why?" or "Why not?" explanation for the user (good fit vs caveats).
"""

from typing import Literal, Optional

import railtracks as rt

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _format_benefits(benefits: dict) -> str:
    if not benefits:
        return "No specific benefits listed."
    parts = []
    if benefits.get("coverage_percent") is not None:
        parts.append(f"{benefits['coverage_percent']}% coverage")
    if benefits.get("annual_limit_dollars"):
        parts.append(f"${benefits['annual_limit_dollars']}/year")
    if benefits.get("session_limit"):
        parts.append(f"{benefits['session_limit']} sessions")
    if benefits.get("per_session_cap_dollars"):
        parts.append(f"up to ${benefits['per_session_cap_dollars']}/session")
    if benefits.get("direct_bill_common"):
        parts.append("direct billing common")
    else:
        parts.append("often pay then submit receipt")
    if benefits.get("referral_required"):
        parts.append("referral required")
    if benefits.get("notes"):
        parts.append(f"Note: {benefits['notes']}")
    return "; ".join(parts)


def build_explain_prompt(
    provider_type: str,
    plan_name: str,
    insurer_name: str,
    insurer_slug: str,
    benefits_text: str,
    provider: Optional[dict] = None,
    question: Literal["why", "why_not"] = "why",
    cost_estimate: Optional[dict] = None,
    referral_required: bool = False,
) -> str:
    """Build prompt for the explain agent."""
    discipline = {"physio": "physiotherapy", "chiro": "chiropractic", "massage": "massage therapy", "urgent": "urgent/emergency care"}.get(provider_type, provider_type)
    parts = [
        f"The user's plan is {insurer_name} — {plan_name}.",
        f"For {discipline}, their plan typically includes: {benefits_text}.",
    ]
    if referral_required:
        parts.append("This plan may require a doctor's referral for this service.")
    if provider:
        prov_parts = [
            f"Provider: {provider.get('name')} at {provider.get('clinic')}.",
            f"Direct bill: {provider.get('accepts_direct_bill')}.",
            f"Languages: {', '.join(provider.get('languages') or [])}.",
        ]
        insurers_acc = provider.get("insurers_accepted") or []
        if insurers_acc:
            prov_parts.append(f"Provider accepts direct billing for: {', '.join(insurers_acc)}. User's insurer: {insurer_slug}.")
        parts.append(" ".join(prov_parts))
        parts.append("Your answer MUST focus on why this specific provider (name and clinic) is a good fit or might not be—e.g. languages, direct billing, insurer match, availability. Do NOT focus on explaining the user's insurance plan; only mention insurance when it is about this provider.")
    else:
        parts.append("No specific provider selected; explain in terms of this type of care and the plan.")
    if cost_estimate:
        c = cost_estimate
        pct = c.get("coverage_percent") or 0
        you_pay = c.get("you_pay", 0)
        parts.append(
            f"Cost summary: visit ${c.get('cost_per_visit', 0):.0f}, plan covers {pct}%, "
            f"you pay about ${you_pay:.0f} per visit out of pocket; annual limit ${c.get('annual_limit_dollars') or 0}."
        )
        parts.append("You MUST state clearly: (1) Their plan covers this care and covers [X]% of eligible costs. (2) They pay the rest out of pocket (about $[you_pay] per visit). Use the numbers above.")
    else:
        # No cost estimate but we may have coverage_percent from benefits
        if benefits_text and "coverage" in benefits_text.lower():
            parts.append("You MUST state clearly: whether their plan covers this care, what percentage the plan covers (from the benefits above), and that they pay the remainder out of pocket. Exact per-visit amount depends on the provider.")
    if question == "why":
        parts.append("In 2–3 short sentences, explain why this provider (if given) or this type of care is a good fit—focus on the provider when one is given.")
    else:
        parts.append("In 2–3 short sentences, explain why this provider or type of care might not be ideal—e.g. limits, direct billing, referral, or other caveats. Be helpful, not alarming. Focus on the provider when one is given.")
    return "\n".join(parts)


EXPLAIN_SYSTEM = """You are the FlexCare referral assistant. You help users understand coverage and providers.

When explaining coverage, you MUST clearly state: (1) Whether their plan covers this type of care (yes/no). (2) What percentage the plan covers (e.g. "Your plan covers 70%"). (3) That they pay the rest out of pocket (e.g. "you pay the remaining 30% out of pocket" or "you pay about $X per visit"). Use the cost and coverage numbers you are given.

When a specific provider is given, also explain why that provider is a good fit or not (e.g. direct billing, languages, insurer match). Keep the answer to 2–4 sentences. End with a brief disclaimer that final coverage is determined by the insurer. Be clear and practical."""


from backend.schemas.outputs import ExplainOutput

explain_agent = rt.agent_node(
    name="Explain Referral",
    llm=rt.llm.GeminiLLM("gemini-2.5-flash"),
    system_message=EXPLAIN_SYSTEM,
    output_schema=ExplainOutput,
)


async def run_explain(
    provider_type: str,
    plan_slug: str,
    question: Literal["why", "why_not"],
    provider_id: Optional[str] = None,
) -> str:
    """
    Return a short explanation (why this fits or why not).
    Uses referral_coverage for plan benefits and referral_providers for provider by id.
    Includes cost estimate and referral_required / insurers_accepted when available.
    """
    from backend.referral_coverage import get_plan_benefits, estimate_cost
    from backend.referral_providers import get_provider_by_id

    plan = get_plan_benefits(plan_slug)
    if not plan:
        return "We couldn't find that plan. Please check your selection and try again."
    insurer_slug = plan.get("insurer_slug", "")
    insurer_name = insurer_slug.replace("_", " ").title()
    benefits = (plan.get("benefits") or {}).get(provider_type)
    benefits_text = _format_benefits(benefits) if benefits else "Check your plan booklet for this service."
    referral_required = bool(benefits and benefits.get("referral_required"))

    provider = None
    if provider_id:
        provider = get_provider_by_id(provider_id)
        if not provider:
            return "We couldn't find that provider. Please check the selection and try again."
        # When explaining a specific provider, ensure we only use one of the same discipline
        if provider.get("provider_type") != provider_type:
            return "That provider doesn't match this type of care. Please pick a provider from the list above."

    cost_estimate = estimate_cost(plan_slug, provider_type, provider_id=provider_id)

    prompt = build_explain_prompt(
        provider_type=provider_type,
        plan_name=plan.get("name", plan_slug),
        insurer_name=insurer_name,
        insurer_slug=insurer_slug,
        benefits_text=benefits_text,
        provider=provider,
        question=question,
        cost_estimate=cost_estimate,
        referral_required=referral_required,
    )
    result = await rt.call(explain_agent, prompt)
    out = result.structured
    return out.explanation if hasattr(out, "explanation") and out.explanation else str(out)
