import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from core.models import ChartSpec, ChartType


class ChartFactory:
    @staticmethod
    def build_figure(df: pl.DataFrame, spec: ChartSpec) -> go.Figure:
        cols = set(df.columns)
        if spec.x_column not in cols and spec.chart_type != ChartType.HEATMAP:
            return go.Figure()

        template = "plotly_white"

        if spec.chart_type == ChartType.BAR and spec.y_column in cols:
            agg_df = (
                df.group_by(spec.x_column)
                .agg(pl.col(spec.y_column).sum().alias(spec.y_column))
                .sort(spec.y_column, descending=True)
                .head(15)
                .to_pandas()
            )
            return px.bar(
                agg_df,
                x=spec.x_column,
                y=spec.y_column,
                title=spec.title,
                template=template,
            )

        elif spec.chart_type == ChartType.LINE and spec.y_column in cols:
            agg_df = (
                df.group_by(spec.x_column)
                .agg(pl.col(spec.y_column).sum().alias(spec.y_column))
                .sort(spec.x_column)
                .to_pandas()
            )
            return px.line(
                agg_df,
                x=spec.x_column,
                y=spec.y_column,
                markers=True,
                title=spec.title,
                template=template,
            )

        elif spec.chart_type == ChartType.SCATTER and spec.y_column in cols:
            sample_df = df.head(2000).to_pandas()
            return px.scatter(
                sample_df,
                x=spec.x_column,
                y=spec.y_column,
                color=spec.color_column if spec.color_column in cols else None,
                title=spec.title,
                template=template,
            )

        elif spec.chart_type == ChartType.HISTOGRAM:
            sample_df = df.select(spec.x_column).drop_nulls().head(10000).to_pandas()
            return px.histogram(
                sample_df, x=spec.x_column, title=spec.title, template=template
            )

        elif spec.chart_type == ChartType.TREEMAP and spec.y_column in cols:
            agg_df = (
                df.group_by(spec.x_column)
                .agg(pl.col(spec.y_column).sum().alias(spec.y_column))
                .filter(pl.col(spec.y_column) > 0)
                .sort(spec.y_column, descending=True)
                .head(20)
                .to_pandas()
            )
            return px.treemap(
                agg_df,
                path=[spec.x_column],
                values=spec.y_column,
                title=spec.title,
                template=template,
            )

        elif spec.chart_type == ChartType.HEATMAP:
            num_cols = [c for c in df.columns if df[c].dtype.is_numeric()][:10]
            if len(num_cols) >= 2:
                corr_pdf = df.select(num_cols).to_pandas().corr()
                return px.imshow(
                    corr_pdf,
                    text_auto=".2f",
                    title=spec.title,
                    template=template,
                    aspect="auto",
                )

        return go.Figure()
