import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from agents.orchestrator_agent import OrchestratorAgent
from analysis.profiler import DataProfiler
from core.models import ChartSpec, ChartType
from reports.visualizer import ChartFactory
from workflows.pipeline_context import PipelineContext

st.set_page_config(page_title="AI End-to-End Data Analyst", layout="wide")


@st.cache_resource
def get_orchestrator() -> OrchestratorAgent:
    return OrchestratorAgent()


def render_app():
    st.title("Autonomous AI Business Intelligence & Data Analyst")
    st.caption(
        "Brain: Gemini 2.5 Pro API | Muscles: Polars + DuckDB (100% Local Processing)"
    )

    orch = get_orchestrator()

    with st.sidebar:
        st.header("1. Upload Dataset")
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel (.xlsx)", type=["csv", "xlsx"]
        )
        selected_sheet = None

        if uploaded_file:
            upload_path = orch.config.storage_dir / "uploads" / uploaded_file.name
            upload_path.write_bytes(uploaded_file.getbuffer())

            if upload_path.suffix.lower() in [".xlsx", ".xls"]:
                _, _, sheets = DataProfiler.load_dataset(str(upload_path))
                selected_sheet = st.selectbox(
                    "Select Excel Sheet", options=sheets, index=0
                )

            if st.button(
                "Run Autonomous End-to-End Analysis",
                type="primary",
                use_container_width=True,
            ):
                progress_bar = st.progress(0.0)
                status_text = st.empty()

                def update_ui(msg: str, pct: float):
                    status_text.info(msg)
                    progress_bar.progress(pct)

                st.session_state["context"] = orch.run_full_pipeline(
                    str(upload_path),
                    sheet_name=selected_sheet,
                    progress_callback=update_ui,
                )

    if "context" not in st.session_state:
        st.info(
            "Upload a CSV or Excel file from the sidebar to trigger the 15-agent autonomous pipeline."
        )
        return

    ctx: PipelineContext = st.session_state["context"]
    df = ctx.working_df
    profile = ctx.cleaned_profile
    biz = ctx.business_context
    quality = ctx.quality_report
    clean_rep = ctx.cleaning_report
    kpis = ctx.kpi_report
    viz = ctx.visualization_report
    insights = ctx.insight_report
    causes = ctx.root_cause_report
    recs = ctx.recommendation_report
    story = ctx.storytelling_report
    artifacts = ctx.artifacts

    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    col_d1.metric(
        "Data Health Score",
        f"{clean_rep.final_quality_score}/100",
        f"{round(clean_rep.final_quality_score - clean_rep.initial_quality_score, 2)}",
    )
    col_d2.download_button(
        "Download Executive PDF",
        data=Path(artifacts.pdf_path).read_bytes(),
        file_name=Path(artifacts.pdf_path).name,
        mime="application/pdf",
        use_container_width=True,
    )
    col_d3.download_button(
        "Download PowerPoint (.pptx)",
        data=Path(artifacts.pptx_path).read_bytes(),
        file_name=Path(artifacts.pptx_path).name,
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True,
    )
    col_d4.download_button(
        "Download HTML Dashboard",
        data=Path(artifacts.html_path).read_bytes(),
        file_name=Path(artifacts.html_path).name,
        mime="text/html",
        use_container_width=True,
    )

    tabs = st.tabs(
        [
            "Executive Dashboard",
            "Storytelling & Insights",
            "Data Health & Cleaning",
            "Data Dictionary & EDA",
            "Conversational Data Chat (SQL)",
            "Agent Execution Traces",
        ]
    )

    with tabs[0]:
        st.subheader(f"{biz.domain} — Executive Overview")
        st.markdown(f"**Headline:** {story.executive_headline}")
        kpi_cols = st.columns(min(len(kpis.kpis), 4))
        for idx, kpi in enumerate(kpis.kpis):
            kpi_cols[idx % len(kpi_cols)].metric(
                label=f"{kpi.name} ({kpi.category})", value=kpi.formatted_value
            )

        st.divider()
        chart_cols = st.columns(2)
        for idx, spec in enumerate(viz.charts):
            fig = ChartFactory.build_figure(df, spec)
            chart_cols[idx % 2].plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.subheader("Consulting Narrative")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**1. What Happened**\n\n{story.what_happened}")
            st.markdown(f"**2. Why It Happened**\n\n{story.why_it_happened}")
            st.markdown(f"**3. Business Impact**\n\n{story.business_impact}")
        with c2:
            st.markdown(f"**4. Key Risks**\n\n{story.risks}")
            st.markdown(f"**5. Opportunities**\n\n{story.opportunities}")
            st.markdown(f"**6. Immediate Next Steps**\n\n{story.next_steps}")

        st.divider()
        st.subheader("Verified Insights & Ranked Root Causes")
        ic1, ic2 = st.columns(2)
        with ic1:
            for item in insights.insights:
                st.success(
                    f"**[{item.impact_level}] {item.title}**\n\n{item.business_insight}\n\n*Evidence: {item.raw_finding}*"
                )
        with ic2:
            for rc in causes.root_causes:
                st.warning(
                    f"**Rank #{rc.rank}: {rc.primary_driver} ({rc.dimension_analyzed})**\n\n{rc.supporting_evidence} (Impact Weight: {rc.impact_weight_pct}%)"
                )

        st.subheader("Actionable Recommendations")
        for rec in recs.recommendations:
            st.info(
                f"**[{rec.tier} - Priority #{rec.priority}] {rec.title}**\n\n{rec.action} — *Expected Impact: {rec.expected_impact}*"
            )

    with tabs[2]:
        st.subheader("Data Quality Audit & Autonomous Cleaning Log")
        st.write(quality.summary)
        st.dataframe([i.model_dump() for i in quality.issues], use_container_width=True)
        st.subheader("Executed Cleaning Plan")
        st.dataframe(
            [
                {
                    "Column": log.operation.column,
                    "Issue": log.operation.issue,
                    "Action": log.operation.action.value,
                    "Affected Rows": log.affected_records,
                    "Status": log.status,
                    "Duration (ms)": log.execution_time_ms,
                }
                for log in clean_rep.logs
            ],
            use_container_width=True,
        )

    with tabs[3]:
        st.subheader("AI-Generated Data Dictionary")
        st.dataframe(
            [d.model_dump() for d in biz.data_dictionary], use_container_width=True
        )
        st.subheader("Top Correlations")
        st.dataframe(
            [c.model_dump() for c in ctx.eda_report.top_correlations],
            use_container_width=True,
        )

    with tabs[4]:
        st.subheader("Ask Questions About Your Dataset (DuckDB SQL Agent)")
        question = st.text_input(
            "Example: What are the top 10 products or categories by total value?"
        )
        if st.button("Run Query") and question:
            res = orch.sql_chat_agent.answer_question(df, profile, question)
            plan = res["plan"]
            res_df = res["result_df"]
            st.code(plan.sql_query, language="sql")
            st.write(plan.explanation)
            st.dataframe(res_df.to_pandas(), use_container_width=True)
            if (
                plan.chart_type in ["bar", "line", "scatter", "histogram", "treemap"]
                and plan.x_column
            ):
                spec = ChartSpec(
                    chart_id="chat_chart",
                    title=question,
                    chart_type=ChartType(plan.chart_type),
                    x_column=plan.x_column,
                    y_column=plan.y_column,
                    rationale="Generated from Data Chat",
                )
                st.plotly_chart(
                    ChartFactory.build_figure(res_df, spec), use_container_width=True
                )

    with tabs[5]:
        st.subheader("Multi-Agent Execution Telemetry")
        st.dataframe([t.model_dump() for t in ctx.traces], use_container_width=True)


if __name__ == "__main__":
    render_app()
