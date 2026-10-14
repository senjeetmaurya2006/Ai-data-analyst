from datetime import datetime
from agents.base import BaseAgent
from core.models import PipelineArtifacts
from reports.pdf_builder import PDFReportBuilder
from reports.pptx_builder import PPTXReportBuilder
from reports.html_builder import HTMLDashboardBuilder
from workflows.pipeline_context import PipelineContext


class ReportAgent(BaseAgent):
    """Compiles Executive PDF, PowerPoint presentation, and Interactive HTML Dashboard."""

    def _execute(self, context: PipelineContext) -> PipelineArtifacts:
        version = datetime.utcnow().strftime("v%Y%m%d_%H%M%S")
        out_dir = self.config.storage_dir / "outputs"
        stem = context.cleaned_profile.filename.rsplit(".", 1)[0]

        pdf_path = str(out_dir / f"{stem}_{version}.pdf")
        pptx_path = str(out_dir / f"{stem}_{version}.pptx")
        html_path = str(out_dir / f"{stem}_{version}.html")

        PDFReportBuilder.build(context, pdf_path)
        PPTXReportBuilder.build(context, pptx_path)
        HTMLDashboardBuilder.build(context, html_path)

        artifacts = PipelineArtifacts(
            version=version,
            pdf_path=pdf_path,
            pptx_path=pptx_path,
            html_path=html_path,
        )
        context.artifacts = artifacts
        return artifacts
