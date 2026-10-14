from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from workflows.pipeline_context import PipelineContext


class PDFReportBuilder:
    @staticmethod
    def build(context: PipelineContext, output_path: str):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ExecTitle",
            parent=styles["Heading1"],
            fontSize=20,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=12,
        )
        h2_style = ParagraphStyle(
            "ExecH2",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#1E3A8A"),
            spaceBefore=14,
            spaceAfter=6,
        )
        body_style = styles["BodyText"]

        elements = []
        profile = context.cleaned_profile
        biz = context.business_context
        clean_rep = context.cleaning_report
        story = context.storytelling_report
        kpis = context.kpi_report
        insights = context.insight_report
        causes = context.root_cause_report
        recs = context.recommendation_report

        elements.append(
            Paragraph(f"Executive BI Report: {profile.filename}", title_style)
        )
        elements.append(
            Paragraph(
                f"<b>Domain:</b> {biz.domain} | <b>Rows:</b> {profile.row_count:,} | <b>Health Score:</b> {clean_rep.final_quality_score}/100",
                body_style,
            )
        )
        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(
                f"<b>Executive Headline:</b> {story.executive_headline}", body_style
            )
        )
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("1. Key Performance Indicators", h2_style))
        kpi_data = [["KPI Name", "Category", "Value"]]
        for k in kpis.kpis:
            kpi_data.append([k.name, k.category, k.formatted_value or str(k.value)])
        t = Table(kpi_data, colWidths=[200, 120, 180])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(t)

        elements.append(Paragraph("2. Executive Storytelling Narrative", h2_style))
        for label, text in [
            ("What Happened", story.what_happened),
            ("Why It Happened", story.why_it_happened),
            ("Business Impact", story.business_impact),
            ("Key Risks", story.risks),
            ("Opportunities", story.opportunities),
            ("Immediate Next Steps", story.next_steps),
        ]:
            elements.append(Paragraph(f"<b>{label}:</b> {text}", body_style))
            elements.append(Spacer(1, 6))

        elements.append(PageBreak())

        elements.append(Paragraph("3. Verified Business Insights", h2_style))
        for ins in insights.insights:
            elements.append(
                Paragraph(
                    f"• <b>[{ins.impact_level}] {ins.title}:</b> {ins.business_insight} <i>({ins.raw_finding})</i>",
                    body_style,
                )
            )
            elements.append(Spacer(1, 4))

        elements.append(Paragraph("4. Ranked Root Causes", h2_style))
        for rc in causes.root_causes:
            elements.append(
                Paragraph(
                    f"<b>Rank #{rc.rank} - {rc.primary_driver} ({rc.dimension_analyzed}):</b> {rc.supporting_evidence}",
                    body_style,
                )
            )
            elements.append(Spacer(1, 4))

        elements.append(Paragraph("5. Strategic & Tactical Recommendations", h2_style))
        for r in recs.recommendations:
            elements.append(
                Paragraph(
                    f"• <b>[{r.tier}] {r.title}:</b> {r.action} (Expected Impact: {r.expected_impact})",
                    body_style,
                )
            )
            elements.append(Spacer(1, 4))

        doc.build(elements)
