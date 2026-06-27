import json
import logging
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

ARCHITECTURE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an enterprise software architect.

Your job:
Infer the high-level architecture of a legacy application by grouping \
related classes into logical components.

You must only use the provided structured metadata (classes, methods, \
packages, dependencies, and upstream analysis). Do not invent classes or \
technologies that are not present in the input.

Rules:
- Infer component names dynamically from class names, packages, and \
responsibilities.
- Every listed class must belong to exactly one component.
- Use class names exactly as provided.
- Return valid JSON only.

Respond with valid JSON only using this structure:
{{
  "components": [
    {{
      "name": "...",
      "responsibility": "...",
      "classes": ["...", "..."]
    }}
  ]
}}""",
        ),
        (
            "human",
            """Analyze the following application metadata and infer logical \
architecture components.

classes:
{classes}

methods:
{methods}

dependencies:
{dependencies}

code_analysis:
{code_analysis}

dependency_analysis:
{dependency_analysis}

risk_analysis:
{risk_analysis}""",
        ),
    ]
)

BUSINESS_CAPABILITY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an enterprise business analyst.

Your job:
Infer the primary business capabilities implemented by a legacy \
application based on its architecture and analysis metadata.

You must only use the provided structured analysis. Do not invent \
capabilities that are not supported by the input.

Rules:
- Infer capability names dynamically from architecture components and \
code analysis.
- Describe what each capability does in business terms.
- Return valid JSON only.

Respond with valid JSON only using this structure:
{{
  "business_capabilities": [
    {{
      "name": "...",
      "description": "..."
    }}
  ]
}}""",
        ),
        (
            "human",
            """Analyze the following application intelligence and infer \
business capabilities.

architecture_summary:
{architecture_summary}

code_analysis:
{code_analysis}

dependency_analysis:
{dependency_analysis}""",
        ),
    ]
)

DOCUMENTATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an enterprise software architect producing \
architecture documentation.

Your job:
Generate a comprehensive architecture report from structured application \
analysis.

You must only use the provided facts. Do not invent technologies or \
capabilities not present in the input.

Rules:
- Write in clear enterprise documentation style.
- Synthesize architecture, business capabilities, and technical risks.
- Use enterprise knowledge when relevant.
- Return valid JSON only.

Respond with valid JSON only using this structure:
{{
  "application_overview": "...",
  "architecture_summary": "...",
  "components": [],
  "business_capabilities": [],
  "technology_summary": "...",
  "technical_risks": [],
  "modernization_opportunities": []
}}""",
        ),
        (
            "human",
            """Generate an enterprise architecture report from the \
following application intelligence.

code_analysis:
{code_analysis}

dependency_analysis:
{dependency_analysis}

risk_analysis:
{risk_analysis}

architecture_summary:
{architecture_summary}

business_capabilities:
{business_capabilities}

Relevant Enterprise Knowledge:
{retrieved_context}""",
        ),
    ]
)

MODERNIZATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an enterprise software modernization architect.

Your job:
Analyze legacy application intelligence and recommend modernization strategy.

Focus on:
- cloud migration
- microservices readiness
- dependency risks
- API modernization
- migration sequencing

Rules:
Only use provided facts.
Do not invent technologies.
Use the provided enterprise knowledge as the primary source when creating
modernization recommendations.
Return concise enterprise recommendations.

Respond with valid JSON only using this structure:
{{
  "architecture_assessment": "...",
  "key_risks": [],
  "recommended_steps": [],
  "target_architecture": "..."
}}""",
        ),
        (
            "human",
            """Analyze the following legacy application intelligence and \
provide a modernization strategy.

code_analysis:
{code_analysis}

dependency_analysis:
{dependency_analysis}

risk_analysis:
{risk_analysis}

architecture_summary:
{architecture_summary}

business_capabilities:
{business_capabilities}

architecture_report:
{architecture_report}

dependencies:
{dependencies}

Relevant Enterprise Knowledge:
{retrieved_context}""",
        ),
    ]
)


class LLMService:
    def __init__(self) -> None:
        self._llm: ChatOpenAI | None = None

    @property
    def llm(self) -> ChatOpenAI:
        if self._llm is None:
            self._llm = ChatOpenAI(
                model="gpt-4.1-mini",
                temperature=0,
            )
        return self._llm

    def generate_architecture_summary(self, context: dict) -> dict:
        prompt = ARCHITECTURE_PROMPT.format_messages(
            classes=json.dumps(context.get("classes", []), indent=2),
            methods=json.dumps(context.get("methods", []), indent=2),
            dependencies=json.dumps(
                context.get("dependencies", []),
                indent=2,
            ),
            code_analysis=json.dumps(
                context.get("code_analysis", {}),
                indent=2,
            ),
            dependency_analysis=json.dumps(
                context.get("dependency_analysis", {}),
                indent=2,
            ),
            risk_analysis=json.dumps(
                context.get("risk_analysis", {}),
                indent=2,
            ),
        )

        response = self.llm.invoke(prompt)
        content = self._extract_response_content(response.content)
        return self._parse_architecture_response(content)

    def generate_business_capabilities(self, context: dict) -> dict:
        prompt = BUSINESS_CAPABILITY_PROMPT.format_messages(
            architecture_summary=json.dumps(
                context.get("architecture_summary", {}),
                indent=2,
            ),
            code_analysis=json.dumps(
                context.get("code_analysis", {}),
                indent=2,
            ),
            dependency_analysis=json.dumps(
                context.get("dependency_analysis", {}),
                indent=2,
            ),
        )

        response = self.llm.invoke(prompt)
        content = self._extract_response_content(response.content)
        return self._parse_business_capabilities_response(content)

    def generate_architecture_report(self, context: dict) -> dict:
        retrieved_context = context.get("retrieved_context", [])
        if retrieved_context:
            retrieved_context_text = "\n".join(
                f"- {item}" for item in retrieved_context
            )
        else:
            retrieved_context_text = "No enterprise knowledge retrieved."

        prompt = DOCUMENTATION_PROMPT.format_messages(
            code_analysis=json.dumps(
                context.get("code_analysis", {}),
                indent=2,
            ),
            dependency_analysis=json.dumps(
                context.get("dependency_analysis", {}),
                indent=2,
            ),
            risk_analysis=json.dumps(
                context.get("risk_analysis", {}),
                indent=2,
            ),
            architecture_summary=json.dumps(
                context.get("architecture_summary", {}),
                indent=2,
            ),
            business_capabilities=json.dumps(
                context.get("business_capabilities", {}),
                indent=2,
            ),
            retrieved_context=retrieved_context_text,
        )

        response = self.llm.invoke(prompt)
        content = self._extract_response_content(response.content)
        return self._parse_architecture_report_response(content)

    def generate_modernization_strategy(self, context: dict) -> dict:
        retrieved_context = context.get("retrieved_context", [])
        if retrieved_context:
            retrieved_context_text = "\n".join(
                f"- {item}" for item in retrieved_context
            )
        else:
            retrieved_context_text = "No enterprise knowledge retrieved."

        prompt = MODERNIZATION_PROMPT.format_messages(
            code_analysis=json.dumps(
                context.get("code_analysis", {}),
                indent=2,
            ),
            dependency_analysis=json.dumps(
                context.get("dependency_analysis", {}),
                indent=2,
            ),
            risk_analysis=json.dumps(
                context.get("risk_analysis", {}),
                indent=2,
            ),
            architecture_summary=json.dumps(
                context.get("architecture_summary", {}),
                indent=2,
            ),
            business_capabilities=json.dumps(
                context.get("business_capabilities", {}),
                indent=2,
            ),
            architecture_report=json.dumps(
                context.get("architecture_report", {}),
                indent=2,
            ),
            dependencies=json.dumps(
                context.get("dependencies", []),
                indent=2,
            ),
            retrieved_context=retrieved_context_text,
        )

        response = self.llm.invoke(prompt)
        content = self._extract_response_content(response.content)

        return self._parse_json_response(content)

    def _extract_response_content(self, content: str | list) -> str:
        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, dict):
                    parts.append(block.get("text", ""))
                else:
                    parts.append(str(block))
            content = "".join(parts)

        return str(content)

    def _parse_architecture_response(self, content: str) -> dict:
        cleaned = content.strip()

        fence_match = re.search(
            r"```(?:json)?\s*(.*?)\s*```",
            cleaned,
            re.DOTALL,
        )
        if fence_match:
            cleaned = fence_match.group(1).strip()

        result = json.loads(cleaned)

        if "components" not in result:
            raise ValueError("LLM response missing required field: components")

        if not isinstance(result["components"], list):
            raise ValueError("LLM response field 'components' must be a list")

        for component in result["components"]:
            if not isinstance(component, dict):
                raise ValueError("Each component must be an object")
            for field in ("name", "responsibility", "classes"):
                if field not in component:
                    raise ValueError(
                        f"Component missing required field: {field}"
                    )

        return result

    def _parse_business_capabilities_response(self, content: str) -> dict:
        cleaned = content.strip()

        fence_match = re.search(
            r"```(?:json)?\s*(.*?)\s*```",
            cleaned,
            re.DOTALL,
        )
        if fence_match:
            cleaned = fence_match.group(1).strip()

        result = json.loads(cleaned)

        if "business_capabilities" not in result:
            raise ValueError(
                "LLM response missing required field: business_capabilities"
            )

        capabilities = result["business_capabilities"]
        if not isinstance(capabilities, list):
            raise ValueError(
                "LLM response field 'business_capabilities' must be a list"
            )

        for capability in capabilities:
            if not isinstance(capability, dict):
                raise ValueError("Each capability must be an object")
            for field in ("name", "description"):
                if field not in capability:
                    raise ValueError(
                        f"Capability missing required field: {field}"
                    )

        return {"capabilities": capabilities}

    def _parse_architecture_report_response(self, content: str) -> dict:
        cleaned = content.strip()

        fence_match = re.search(
            r"```(?:json)?\s*(.*?)\s*```",
            cleaned,
            re.DOTALL,
        )
        if fence_match:
            cleaned = fence_match.group(1).strip()

        result = json.loads(cleaned)

        required_fields = (
            "application_overview",
            "architecture_summary",
            "components",
            "business_capabilities",
            "technology_summary",
            "technical_risks",
            "modernization_opportunities",
        )
        for field in required_fields:
            if field not in result:
                raise ValueError(
                    f"LLM response missing required field: {field}"
                )

        list_fields = (
            "components",
            "business_capabilities",
            "technical_risks",
            "modernization_opportunities",
        )
        for field in list_fields:
            if not isinstance(result[field], list):
                raise ValueError(f"LLM response field '{field}' must be a list")

        return result

    def _parse_json_response(self, content: str) -> dict:
        cleaned = content.strip()

        fence_match = re.search(
            r"```(?:json)?\s*(.*?)\s*```",
            cleaned,
            re.DOTALL,
        )
        if fence_match:
            cleaned = fence_match.group(1).strip()

        result = json.loads(cleaned)

        required_fields = (
            "architecture_assessment",
            "key_risks",
            "recommended_steps",
            "target_architecture",
        )
        for field in required_fields:
            if field not in result:
                raise ValueError(
                    f"LLM response missing required field: {field}"
                )

        return result
