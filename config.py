from dataclasses import dataclass



 

@dataclass
class LLMConfig:

    model_name:str = "gemini/gemini-2.0-flash"
    api_key: str = "your-gemini-api"
    max_iter = 3
    max_rpm = 10

    plotly_light_theme_command = 'use plotly light theme for all plots'
    plotly_dark_theme_command = 'use plotly dark theme for all plots'

@dataclass
class InsightsLLMConfig:
    model_name: str = "gemini/gemini-2.0-flash"
    api_key: str = "your-gemini-api"
    insights_command: str = (
    "Turn this graph into a short narrative of insights. Highlight only the most impactful trends, "
    "patterns, and anomalies, showing what they mean rather than just describing numbers. "
    "Each insight should feel like a mini-story with technical clarity, concise wording, and clear implications. "
    "Keep it simple, actionable, and under 100 words, focusing on meaning over detail. "
    "Write the insights directly without introductions or filler."
)


    time_to_sleep_between_requests: int = 15
     
    retry_upon_fall = False
    max_retries = 3
    time_to_sleep_between_retries = 30
  




@dataclass
class ReportConfig:
    light_theme_file_path: str = "./templates/report_light_theme.html"
    dark_theme_file_path: str = "./templates/report_dark_theme.html"
    block_file_path: str = "./templates/page_block.html"
    output_file: str = "styled_report.html"
    dark_theme: bool = False


