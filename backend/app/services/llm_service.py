import json
import logging
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

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
            dependencies=json.dumps(
                context.get("dependencies", []),
                indent=2,
            ),
            retrieved_context=retrieved_context_text,
        )

        response = self.llm.invoke(prompt)
        content = response.content

        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, dict):
                    parts.append(block.get("text", ""))
                else:
                    parts.append(str(block))
            content = "".join(parts)

        return self._parse_json_response(str(content))

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
