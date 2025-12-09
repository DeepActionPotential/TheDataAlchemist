import sys

from PyQt5.QtWidgets import (
    QApplication
)

from services.csv_analyses import DatasetAnalysesMaker
from services.report_manager import ReportFileCreator
from core.dataset_manager import DatasetAnalyzer
from config import LLMConfig, ReportConfig
from crewai import LLM
from ui.main_ui import UI 

def main():
    # Initialize LLM and configuration
    llm_config = LLMConfig()
    llm = LLM(
        model=LLMConfig.model_name,
        api_key=LLMConfig.api_key,
    )

    # Set up analysis and report creation services
    analyses_maker = DatasetAnalysesMaker(
        llm=llm,
        llm_config=llm_config
    )
    report_creator = ReportFileCreator()

    # Set up dataset converter
    dataset_converter = DatasetAnalyzer(
        dataset_analyses_maker=analyses_maker,
        report_creator=report_creator,
        report_config=ReportConfig()
    )

    # Initialize Qt application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Better dark theme support

    # Pass the conversion function to the UI
    window = UI(dataset_converter.convert_dataset_to_report)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
