from agents.reading_agents import (
    DataReaderAgent,
 
)

from agents.code_agents import (
    SimpleAnalysisPlotlyCodeAgent,
    IntermediateAnalysisPlotlyCodeAgent,
    AdvancedAnalysisPlotlyCodeAgent,
    AnalysisDataRecommenderAgent
    )

from agents.insights_agents import (
    CodesToInsightsAgent
)


from schemas.schemas import (
    AnalysisCode, CSVFilePath, DataFrameInfo, AnalysisRecommendation,
    CodesWithInsights, AllCodesWithInsights
)
from utils.utils import convert_codes_to_insights, create_dataframe_info
from config import LLMConfig

from crewai import Crew, Task, LLM


class DatasetAnalysesMaker:
    """
    Orchestrates the end-to-end analysis workflow for a CSV dataset using CrewAI agents and tasks.

    This class sets up agents for reading data, recommending analyses, generating Plotly code,
    and converting code to insights. It then builds a Crew workflow to process the dataset
    and returns structured insights for simple, intermediate, and advanced analyses.

    Attributes:
        llm (LLM): The language model instance used by agents.
        llm_config (LLMConfig): Configuration for agent iteration and rate limits.
        data_reader_agent (Agent): Agent for reading and summarizing the CSV dataset.
        analysis_recommender_agent (Agent): Agent for recommending analyses.
        simple_analysis_code_agent (Agent): Agent for generating simple Plotly code.
        intermediate_analysis_code_agent (Agent): Agent for generating intermediate Plotly code.
        advanced_analysis_code_agent (Agent): Agent for generating advanced Plotly code.
        codes_to_insights_agent (Agent): Agent for converting Plotly code to insights.
    """

    def __init__(self, llm: LLM, llm_config: LLMConfig,):
        """
        Initializes the DatasetAnalysisMaker with the required agents and configuration.

        Args:
            llm (LLM): The language model instance to use for all agents.
            llm_config (LLMConfig): Configuration object specifying agent iteration and rate limits.
        """
        self.llm = llm

        self.data_reader_agent = DataReaderAgent(llm=self.llm, tools=[create_dataframe_info]).make_agent()
        self.analysis_recommender_agent = AnalysisDataRecommenderAgent(self.llm).make_agent()
        self.simple_analysis_code_agent = SimpleAnalysisPlotlyCodeAgent(self.llm).make_agent()
        self.intermediate_analysis_code_agent = IntermediateAnalysisPlotlyCodeAgent(self.llm).make_agent()
        self.advanced_analysis_code_agent = AdvancedAnalysisPlotlyCodeAgent(self.llm).make_agent()
        self.codes_to_insights_agent = CodesToInsightsAgent(self.llm, [convert_codes_to_insights]).make_agent()

        for agent in [
            self.simple_analysis_code_agent,
            self.intermediate_analysis_code_agent,
            self.advanced_analysis_code_agent,
            self.data_reader_agent,
            self.analysis_recommender_agent
        ]:
            agent.max_iter = llm_config.max_iter
            agent.max_rpm = llm_config.max_rpm

    def turn_csv_dataset_into_analysis(self, csv_path: str, number_of_analyses: int, dark_theme: bool = False, callback_func:any = None) -> AllCodesWithInsights:
        """
        Runs the full CrewAI workflow to analyze a CSV dataset and generate insights.

        This function:
        - Reads and summarizes the CSV file.
        - Recommends analyses (simple, intermediate, advanced).
        - Generates Plotly code for each analysis category.
        - Converts code to insights using multimodal reasoning.
        - Returns all insights in a structured AllCodesWithInsights object.

        Args:
            csv_path (str): Path to the CSV file to analyze.
            number_of_analyses (int): Total number of analyses to generate (split across categories).
            dark_theme_command (str, optional): Command to apply dark theme to all plots. Defaults to None.

        Returns:
            AllCodesWithInsights: Structured insights for simple, intermediate, and advanced analyses.
        """

        dark_theme_command = LLMConfig.plotly_dark_theme_command if dark_theme else LLMConfig.plotly_light_theme_command
        number_of_analyses_per_category = int(number_of_analyses // 3)

        dataframe_info_task = Task(
            description=f"Load CSV '{csv_path}' and summarize metadata, columns, and samples.",
            expected_output="DataFrameInfo object",
            agent=self.data_reader_agent,
            input_pydantic=CSVFilePath,
            output_pydantic=DataFrameInfo,
            callback=callback_func if callback_func else None,
        )

        recommending_analysis_task = Task(
            description=(
                "Analyze the provided DataFrameInfo object and recommend 60 possible data analyses that can be performed on the dataset. "
                "Classify each recommendation into 'simple', 'intermediate', or 'advanced' categories. "
                "Each recommendation should be a detailed description (at least 50 words) explaining what to do, how to do it, and what insights to expect. "
                "Do not use any machine learning models."
                "Also include sns if needed,"
                "Also do use column and labels names if needed, I mean do not use 0 for female and 1 for male, instead use male and female as a lables (this is just an example)."
                "Make Sure you do not generate slashes '/' in the generated output"
            ),
            expected_output=(
                "An AnalysisRecommendation object with three lists: simple, intermediate, and advanced. "
                "Each list contains detailed analysis descriptions (minimum 50 words each) suitable for visualization."
                "Make Sure you do not generate slashes '/' in the generated output"
            ),
            agent=self.analysis_recommender_agent,
            input_pydantic=DataFrameInfo,
            output_pydantic=AnalysisRecommendation,
            context=[dataframe_info_task],
            callback=callback_func if callback_func else None,

            
        )

        simple_analysis_code_task = Task(
            description=(
                f"Generate {number_of_analyses_per_category} Python Plotly code snippets for the 'simple' analysis recommendations. "
                "Each code should be minimal, clean, and runnable, visualizing the described analysis using the provided CSV data. "
                "Do not include explanations, markdown, or use machine learning models."
                "Do Not use any print statements"
                "Make Sure you do not generate slashes '/' in the generated output"
                "Each analysis code should include at the end ONLY ONE Plotly figure object creation and should be self-contained. with the variable name as 'fig'"
                "Do NOT include fig.show() function"
                "Do Not include non-original datasets if there are no context"
                f"{dark_theme_command}"
            ),
            expected_output=(
                f"An AnalysisCode object containing a list of Python code strings for simple analyses and the CSV file path used. ('{csv_path}')"
                "Make Sure you do not generate slashes '/' in the generated output"
            ),
            agent=self.simple_analysis_code_agent,
            input_pydantic=AnalysisRecommendation,
            output_pydantic=AnalysisCode,
            context=[recommending_analysis_task, dataframe_info_task],
            # output_file='./1simple_analysis_code.txt',
            callback=callback_func if callback_func else None,

        )

        intermediate_analysis_code_task = Task(
            description=(
                f"Generate {number_of_analyses_per_category} Python Plotly code snippets for the 'intermediate' analysis recommendations. "
                "Codes should include moderate complexity such as grouped charts, faceting, or light interactivity. "
                "Do not include explanations, markdown, or use machine learning models."
                "Do Not use any print statements"
                "Make Sure you do not generate slashes '/' in the generated output"
                "Each analysis code should include at the end ONLY ONE Plotly figure object creation and should be self-contained. with the variable name as 'fig'"
                "Do NOT include fig.show() function"
                "Do Not include non-original datasets if there are no context"

                f"{dark_theme_command}"

            ),
            expected_output=(
                f"An AnalysisCode object containing a list of Python code strings for intermediate analyses and the CSV file path used. ('{csv_path}')"
                "Make Sure you do not generate slashes '/' in the generated output"
            ),
            agent=self.intermediate_analysis_code_agent,
            input_pydantic=AnalysisRecommendation,
            output_pydantic=AnalysisCode,
            context=[recommending_analysis_task, dataframe_info_task],
            # output_file='./1intermediate_analysis_code.txt',
            callback=callback_func if callback_func else None,

        )

        advanced_analysis_code_task = Task(
            description=(
                f"Generate {number_of_analyses_per_category} Python Plotly code snippets for the 'advanced' analysis recommendations. "
                "Codes should leverage advanced Plotly features such as animations, 3D plots, statistical overlays, or dashboards. "
                "Do not include explanations, markdown, or use machine learning models."
                "Do Not use any print statements"
                "Make Sure you do not generate slashes '/' in the generated output"
                "Each analysis code should include at the end ONLY ONE Plotly figure object creation and should be self-contained. with the variable name as 'fig'"
                "Do NOT include fig.show() function"
                "Do Not include non-original datasets if there are no context"

                f"{dark_theme_command}"

            ),
            expected_output=(
                f"An AnalysisCode object containing a list of Python code strings for advanced analyses and the CSV file path used. ('{csv_path}')"
                "Make Sure you do not generate slashes '/' in the generated output"
            ),
            agent=self.advanced_analysis_code_agent,
            input_pydantic=AnalysisRecommendation,
            output_pydantic=AnalysisCode,
            context=[recommending_analysis_task, dataframe_info_task],
            # output_file='./1advanced_analysis_code.txt',
            callback=callback_func if callback_func else None,

        )

        simple_codes_to_insights_task = Task(
            description="Convert the simple analysis Plotly code snippets into CodesWithInsights using Gemini multimodal reasoning."
            "Make Sure you do not generate slashes '/' in the generated output"
            "If the insights fails and get an error, do not include it",
            expected_output="CodesWithInsights object containing insights for each simple analysis. "
            "Make Sure you do not generate slashes '/' in the generated output",
            agent=self.codes_to_insights_agent,
            input_pydantic=AnalysisCode,
            output_pydantic=CodesWithInsights,
            context=[simple_analysis_code_task, dataframe_info_task],
            # output_file='./1simple_insights.txt',
            callback=callback_func if callback_func else None,

        )

        intermediate_codes_to_insights_task = Task(
            description="Convert the intermediate analysis Plotly code snippets into CodesWithInsights using Gemini multimodal reasoning."
            "Make Sure you do not generate slashes '/' in the generated output"
            "If the insights fails and get an error, do not include it",
            expected_output="CodesWithInsights object containing insights for each intermediate analysis."
            "Make Sure you do not generate slashes '/' in the generated output",
            agent=self.codes_to_insights_agent,
            input_pydantic=AnalysisCode,
            output_pydantic=CodesWithInsights,
            context=[intermediate_analysis_code_task, dataframe_info_task],
            # output_file='./1intermediate_insights.txt',
            callback=callback_func if callback_func else None,

        )

        advanced_codes_to_insights_task = Task(
            description="Convert the advanced analysis Plotly code snippets into CodesWithInsights using Gemini multimodal reasoning."
            "Make Sure you do not generate slashes '/' in the generated output"
            "If the insights fails and get an error, do not include it",
            expected_output="CodesWithInsights object containing insights for each advanced analysis."
            "Make Sure you do not generate slashes '/' in the generated output",
            agent=self.codes_to_insights_agent,
            input_pydantic=AnalysisCode,
            output_pydantic=CodesWithInsights,
            context=[advanced_analysis_code_task, dataframe_info_task],
            # output_file='./1advanced_insights.txt',
            callback=callback_func if callback_func else None,

        )

        crew = Crew(
            agents=[
                self.data_reader_agent,
                self.analysis_recommender_agent,
                self.simple_analysis_code_agent,
                self.intermediate_analysis_code_agent,
                self.advanced_analysis_code_agent,
                self.codes_to_insights_agent,
            ],
            tasks=[
                dataframe_info_task,
                recommending_analysis_task,
                simple_analysis_code_task,
                intermediate_analysis_code_task,
                advanced_analysis_code_task,
                simple_codes_to_insights_task,
                intermediate_codes_to_insights_task,
                advanced_codes_to_insights_task,
            ],
            verbose=True,
        )

        result = crew.kickoff(inputs={"file_path": csv_path})

        return AllCodesWithInsights(
            simple=simple_codes_to_insights_task.output.pydantic,
            intermediate=intermediate_codes_to_insights_task.output.pydantic,
            advanced=advanced_codes_to_insights_task.output.pydantic
        )
