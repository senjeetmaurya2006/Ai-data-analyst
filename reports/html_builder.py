from reports.visualizer import ChartFactory
from workflows.pipeline_context import PipelineContext


class HTMLDashboardBuilder:
    @staticmethod
    def build(context: PipelineContext, output_path: str):
        df = context.working_df
        profile = context.cleaned_profile
        kpis = context.kpi_report
        story = context.storytelling_report
        viz = context.visualization_report

        chart_divs = []
        for idx, spec in enumerate(viz.charts):
            fig = ChartFactory.build_figure(df, spec)
            chart_divs.append(
                fig.to_html(
                    full_html=False, include_plotlyjs="cdn" if idx == 0 else False
                )
            )

        kpi_cards = "".join(
            f"""
            <div class="kpi-card">
                <div class="kpi-cat">{k.category}</div>
                <div class="kpi-title">{k.name}</div>
                <div class="kpi-val">{k.formatted_value}</div>
            </div>
            """
            for k in kpis.kpis
        )

        charts_html = "".join(f'<div class="chart-box">{c}</div>' for c in chart_divs)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Executive BI Dashboard - {profile.filename}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; color: #0f172a; margin: 0; padding: 24px; }}
        .header {{ background: #0f172a; color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .kpi-card {{ background: white; padding: 18px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-left: 4px solid #2563eb; }}
        .kpi-cat {{ font-size: 12px; color: #64748b; text-transform: uppercase; }}
        .kpi-title {{ font-size: 14px; font-weight: 600; margin: 4px 0; }}
        .kpi-val {{ font-size: 24px; font-weight: 700; color: #1e3a8a; }}
        .narrative {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(480px, 1fr)); gap: 20px; }}
        .chart-box {{ background: white; padding: 16px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{profile.filename} — Interactive Executive BI Dashboard</h1>
        <p>{story.executive_headline}</p>
    </div>
    <div class="kpi-grid">{kpi_cards}</div>
    <div class="narrative">
        <h3>Executive Narrative</h3>
        <p><strong>What Happened:</strong> {story.what_happened}</p>
        <p><strong>Why It Happened:</strong> {story.why_it_happened}</p>
        <p><strong>Recommendations:</strong> {story.recommendations_narrative}</p>
    </div>
    <div class="chart-grid">{charts_html}</div>
</body>
</html>"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
