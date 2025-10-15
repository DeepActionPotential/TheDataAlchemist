import os
import sys
import html
import traceback
from datetime import datetime
from typing import Iterable, List, Tuple

import plotly.express as px
import pandas as pd

from schemas.schemas import AllCodesWithInsights, CodesWithInsights, CodeWithInsights

try:
    import markdown as md
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


class ReportFileCreator:
    """
    Generates a styled HTML report from Plotly visualizations and insights.

    The report is composed of:
      - A wrapper theme file (global structure, CSS, and {{blocks}} placeholder)
      - A reusable block template (used for each visualization/insight pair)

    Responsibilities:
      - Execute provided Plotly code safely to produce figures
      - Render insights (Markdown if available, fallback to HTML escaping)
      - Insert generated blocks into the wrapper template
      - Write the final report as an HTML file
    """

    # ---------- Internal helpers ----------

    def _exec_code_and_get_fig(self, code_str: str):
        """
        Execute Python code containing Plotly figure creation logic.

        Args:
            code_str (str): Python code expected to define a `fig` object.

        Returns:
            plotly.graph_objects.Figure: A Plotly figure (dark-themed, fixed size).
        """
        local_ns, global_ns = {}, {"px": px, "pd": pd, "datetime": datetime}
        try:
            exec(code_str, global_ns, local_ns)
            fig = local_ns.get("fig") or global_ns.get("fig")
            if fig is None:
                raise RuntimeError("No 'fig' object found in executed code.")

            fig.update_layout(template="plotly_dark", width=600, height=400)
            return fig
        except Exception:
            traceback.print_exc(file=sys.stderr)
            # fallback placeholder chart
            df = px.data.iris()
            return px.scatter(
                df,
                x="sepal_width",
                y="sepal_length",
                color="species",
                title="(placeholder) Iris Sepal Plot",
                width=600,
                height=400,
                template="plotly_dark",
            )

    def _insights_to_html(self, insights_md: str) -> str:
        """
        Convert insights into HTML (Markdown if available, else escaped HTML).

        Args:
            insights_md (str): Raw insight text.

        Returns:
            str: HTML-rendered insights.
        """
        if HAS_MARKDOWN:
            return md.markdown(insights_md)
        escaped = html.escape((insights_md or "").strip())
        return "<p>" + escaped.replace("\n\n", "</p><p>").replace("\n", "<br/>") + "</p>"

    def _render_chart_block(
        self,
        block_template: str,
        code: str,
        insights: str,
        index: int,
        section: str,
        report_title: str,
        footer_text: str,
    ) -> str:
        """
        Render one chart + insights block.

        Args:
            block_template (str): HTML block template with placeholders.
            code (str): Python code string generating a Plotly figure.
            insights (str): Insights text (MD or plain).
            index (int): Block index.
            section (str): Section label (e.g. "Simple Analysis").
            report_title (str): Report title for placeholders.
            footer_text (str): Footer text to insert.

        Returns:
            str: Rendered HTML block.
        """
        fig = self._exec_code_and_get_fig(code)

        fig_title = None
        try:
            if hasattr(fig, "layout") and fig.layout.title.text:
                fig_title = fig.layout.title.text
        except Exception:
            pass

        title = html.escape(fig_title or f"Data Visualization {index}")
        insights_html = self._insights_to_html(insights or "")
        chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})

        rendered = block_template
        for key, value in {
            "{{title}}": title,
            "{{chart}}": chart_html,
            "{{insights}}": insights_html,
            "{{footer_text}}": footer_text,
            "{{report_title}}": html.escape(report_title),
            "{{section}}": html.escape(section or ""),
            "{{index}}": str(index),
        }.items():
            rendered = rendered.replace(key, value)

        return rendered

    def _iter_items(self, payload: AllCodesWithInsights) -> Iterable[Tuple[str, CodeWithInsights]]:
        """
        Yield (section_name, CodeWithInsights) pairs from AllCodesWithInsights.

        Args:
            payload (AllCodesWithInsights): Structured dataset.

        Yields:
            Tuple[str, CodeWithInsights]: Section label and visualization/insight object.
        """
        section_map = {
            "Simple Analysis": getattr(payload, "simple", None),
            "Intermediate Analysis": getattr(payload, "intermediate", None),
            "Advanced Analysis": getattr(payload, "advanced", None),
        }
        for section, cwi in section_map.items():
            if cwi and getattr(cwi, "codes_with_insights", None):
                for item in cwi.codes_with_insights:
                    yield (section, item)

    # ---------- Public API ----------

    def create_report(
        self,
        data: AllCodesWithInsights,
        theme_file_path: str,
        block_file_path: str,
        output_file: str = "styled_report_dark.html",
        report_title: str = "Report",
        page_title: str = "Dark Styled Report",
        footer_text: str = "Generated By Me",
    ) -> None:
        """
        Build and save the full HTML report.

        Args:
            data (AllCodesWithInsights): Dataset containing visualization code & insights.
            theme_file_path (str): Path to wrapper HTML file (must include {{blocks}}).
            block_file_path (str): Path to block template HTML file.
            output_file (str): Path to save the generated report.
            report_title (str): Title used inside the report.
            page_title (str): HTML <title> value.
            footer_text (str): Footer text injected into each block.
        """
        if not os.path.exists(theme_file_path):
            raise FileNotFoundError(f"Wrapper file not found: {theme_file_path}")
        if not os.path.exists(block_file_path):
            raise FileNotFoundError(f"Block file not found: {block_file_path}")

        with open(theme_file_path, "r", encoding="utf-8") as f:
            wrapper_html = f.read()
        with open(block_file_path, "r", encoding="utf-8") as f:
            block_template = f.read()

        blocks: List[str] = []
        for idx, (section, item) in enumerate(self._iter_items(data), start=1):
            block_html = self._render_chart_block(
                block_template=block_template,
                code=item.code,
                insights=item.insights,
                index=idx,
                section=section,
                report_title=report_title,
                footer_text=footer_text,
            )
            blocks.append(block_html)

        final_html = wrapper_html
        final_html = final_html.replace("{{blocks}}", "\n".join(blocks))
        final_html = final_html.replace("{{page_title}}", html.escape(page_title))
        final_html = final_html.replace("{{report_title}}", html.escape(report_title))

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_html)

        print(f"✅ Report saved to: {os.path.abspath(output_file)}")

        return output_file
