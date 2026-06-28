from fpdf import FPDF


class EnterpriseReportPdf(FPDF):
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def generate_pdf(report: dict) -> bytes:
    pdf = EnterpriseReportPdf()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(20, 20, 20)

    _render_cover_page(pdf, report)
    _render_project_information(pdf, report)
    _render_section(pdf, "Executive Summary", report.get("executive_summary", ""))
    _render_section(pdf, "Application Overview", report.get("application_overview", ""))

    architecture_summary = report.get("architecture_summary", {})
    architecture_text = architecture_summary.get("narrative", "")
    if architecture_summary.get("technology_summary"):
        architecture_text = (
            f"{architecture_text}\n\n"
            f"Technology Summary: {architecture_summary['technology_summary']}"
        ).strip()
    _render_section(pdf, "Architecture Summary", architecture_text)
    _render_architecture_components(pdf, report.get("architecture_components", []))
    _render_business_capabilities(pdf, report.get("business_capabilities", []))
    _render_dependency_analysis(pdf, report.get("dependency_analysis", {}))
    _render_risk_assessment(pdf, report.get("technical_risk_assessment", {}))
    _render_modernization_plan(pdf, report.get("modernization_plan", {}))
    _render_code_modernization(pdf, report.get("code_modernization", []))
    _render_modernization_roadmap(pdf, report.get("modernization_roadmap", []))
    _render_section(pdf, "Conclusion", report.get("conclusion", ""))
    _render_section(
        pdf,
        "Report Generation Timestamp",
        report.get("report_generated_at", ""),
    )

    return bytes(pdf.output())


def _render_cover_page(pdf: FPDF, report: dict) -> None:
    cover = report.get("cover_page", {})
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(30, 58, 95)
    pdf.ln(50)
    pdf.multi_cell(0, 12, cover.get("title", "Enterprise Modernization Assessment"))
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 10, cover.get("subtitle", ""))
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Project ID: {cover.get('project_id', '')}")
    pdf.ln(20)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())


def _render_project_information(pdf: FPDF, report: dict) -> None:
    info = report.get("project_information", {})
    pdf.add_page()
    _section_heading(pdf, "Project Information")
    rows = [
        ("Project Name", info.get("project_name", "")),
        ("Project ID", str(info.get("project_id", ""))),
        ("Upload Date", info.get("upload_date", "")),
        ("Analysis Summary", info.get("analysis_summary", "")),
        ("Total Dependencies", str(info.get("total_dependencies", ""))),
        ("Overall Risk", info.get("overall_risk", "")),
    ]
    _render_key_value_table(pdf, rows)


def _render_section(pdf: FPDF, title: str, content: str) -> None:
    if not content:
        return
    pdf.add_page()
    _section_heading(pdf, title)
    _body_text(pdf, content)


def _render_architecture_components(pdf: FPDF, components: list) -> None:
    if not components:
        return
    pdf.add_page()
    _section_heading(pdf, "Architecture Components")
    for component in components:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 8, component.get("name", "Component"))
        _body_text(pdf, f"Responsibility: {component.get('responsibility', '')}")
        classes = ", ".join(component.get("classes", []))
        _body_text(pdf, f"Classes: {classes}")
        pdf.ln(4)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(4)


def _render_business_capabilities(pdf: FPDF, capabilities: list) -> None:
    if not capabilities:
        return
    pdf.add_page()
    _section_heading(pdf, "Business Capabilities")
    for capability in capabilities:
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 8, capability.get("name", ""))
        pdf.set_font("Helvetica", "", 11)
        _body_text(pdf, capability.get("description", ""))
        pdf.ln(4)


def _render_dependency_analysis(pdf: FPDF, dependency_analysis: dict) -> None:
    dependencies = dependency_analysis.get("dependencies", [])
    if not dependencies:
        return
    pdf.add_page()
    _section_heading(pdf, "Dependency Analysis")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 8, "Technology", border=1)
    pdf.cell(25, 8, "Risk", border=1)
    pdf.cell(0, 8, "Dependency", border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for dependency in dependencies:
        pdf.cell(45, 8, _truncate(dependency.get("technology", ""), 24), border=1)
        pdf.cell(25, 8, dependency.get("risk_level", ""), border=1)
        pdf.cell(
            0,
            8,
            _truncate(dependency.get("dependency", ""), 70),
            border=1,
            new_x="LMARGIN",
            new_y="NEXT",
        )


def _render_risk_assessment(pdf: FPDF, risk_assessment: dict) -> None:
    if not risk_assessment:
        return
    pdf.add_page()
    _section_heading(pdf, "Technical Risk Assessment")
    _body_text(pdf, f"Overall Risk: {risk_assessment.get('overall_risk', '')}")
    _body_text(pdf, risk_assessment.get("reason", ""))
    risks = risk_assessment.get("technical_risks", [])
    if risks:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Technical Risks", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        for index, risk in enumerate(risks, start=1):
            _body_text(pdf, f"{index}. {risk}")


def _render_modernization_plan(pdf: FPDF, modernization_plan: dict) -> None:
    if not modernization_plan:
        return
    pdf.add_page()
    _section_heading(pdf, "Modernization Plan")
    _body_text(
        pdf,
        modernization_plan.get(
            "architecture_assessment",
            modernization_plan.get("summary", ""),
        ),
    )
    _body_text(pdf, f"Target Architecture: {modernization_plan.get('target_architecture', '')}")
    key_risks = modernization_plan.get("key_risks", [])
    if key_risks:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Key Risks", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        for index, risk in enumerate(key_risks, start=1):
            _body_text(pdf, f"{index}. {risk}")
    steps = modernization_plan.get("recommended_steps", [])
    if not steps:
        steps = modernization_plan.get("recommendations", [])
    if steps:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Recommended Steps", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        for index, step in enumerate(steps, start=1):
            _body_text(pdf, f"{index}. {step}")


def _render_code_modernization(pdf: FPDF, opportunities: list) -> None:
    if not opportunities:
        return
    pdf.add_page()
    _section_heading(pdf, "Code Modernization Recommendations")
    for index, opportunity in enumerate(opportunities, start=1):
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 8, f"{index}. {opportunity.get('component', 'Component')}")
        pdf.set_font("Helvetica", "", 11)
        _body_text(
            pdf,
            f"Legacy: {opportunity.get('legacy_technology_or_pattern', '')}",
        )
        _body_text(
            pdf,
            f"Modern: {opportunity.get('recommended_approach', '')}",
        )
        _body_text(pdf, f"Reason: {opportunity.get('justification', '')}")
        if opportunity.get("example_modernized_code"):
            pdf.set_font("Courier", "", 9)
            _body_text(pdf, opportunity["example_modernized_code"])
        pdf.ln(4)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(4)


def _render_modernization_roadmap(pdf: FPDF, phases: list) -> None:
    if not phases:
        return
    pdf.add_page()
    _section_heading(pdf, "Modernization Roadmap")
    for phase in phases:
        pdf.set_font("Helvetica", "B", 13)
        pdf.multi_cell(
            0,
            8,
            f"Phase {phase.get('phase', '')}: {phase.get('title', '')}",
        )
        pdf.set_font("Helvetica", "", 11)
        for item in phase.get("items", []):
            _body_text(pdf, f"- {item.get('recommended_action', '')}")
            _body_text(
                pdf,
                f"  Component: {item.get('component', '')} | "
                f"Priority: {item.get('priority', '')} | "
                f"Outcome: {item.get('expected_outcome', '')}",
            )
        pdf.ln(4)


def _section_heading(pdf: FPDF, title: str) -> None:
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(30, 58, 95)
    pdf.multi_cell(0, 10, title)
    pdf.ln(2)
    pdf.set_draw_color(30, 58, 95)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)
    pdf.set_text_color(40, 40, 40)


def _body_text(pdf: FPDF, text: str) -> None:
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, text or "")


def _render_key_value_table(pdf: FPDF, rows: list[tuple[str, str]]) -> None:
    for label, value in rows:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, label, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        _body_text(pdf, value or "—")
        pdf.ln(2)


def _truncate(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return f"{value[: max_length - 3]}..."
