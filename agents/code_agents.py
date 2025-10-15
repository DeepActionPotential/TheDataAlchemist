
from crewai import Agent


class AnalysisDataRecommenderAgent:
    """
    Agent responsible for recommending different levels of data Analysis
    (simple, intermediate, advanced) based on the provided DataFrameInfo model.

    Attributes:
        llm: The language model to be used by the agent.
        tools: Optional list of tools for processing recommendations.
    """

    def __init__(self, llm):
        """
        Initialize the AnalysisDataRecommenderAgent.

        Args:
            llm: The language model instance to use.
        """
        self.llm = llm


    def make_agent(self):
        """
        Create and return a configured Agent for recommending Analysis.

        Returns:
            Agent: An instance of the Agent class configured for Analysis recommendations.
        """
        return Agent(
            role="Analysis Data Recommender",
            goal=(
                "Analyze a DataFrameInfo object and recommend a set of data Analysis "
                "to explore, ordered from simple to advanced complexity."
            ),
            backstory=(
                "You are an experienced data analyst specializing in exploratory "
                "data analysis (EDA). You receive structured metadata in the form "
                "of a DataFrameInfo Pydantic model and suggest Analysis "
                "that will help users better understand their dataset, "
                "starting from quick descriptive stats to more complex patterns."
                "Also, make the recommendations should be detailed of what to do, not just a line of text, it should be a full description of what to do, how to do it, and what to expect from it. it should be at least 50 words for each graph"
                "AND DO NOT use any machine learning models"
            ),
            verbose=True,
            llm=self.llm
        )




class SimpleAnalysisPlotlyCodeAgent:
    """
    Agent that generates simple-level Plotly visualization code snippets
    for basic data understanding.
    """

    def __init__(self, llm):
        self.llm = llm

    def make_agent(self):
        return Agent(
            role="Simple Plotly Code Generator",
            goal=(
                "Given a list of simple Analysi descriptions, produce minimal and clean Plotly code snippets "
                "that visualize each Analysi clearly without overcomplication."
            ),
            backstory=(
                "You are a data visualization expert specializing in quick, accessible Analysi. "
                "You focus on clarity, simplicity, and readability. "
                "You never include non-essential code. "
                "You return only valid Python Plotly code that can be run immediately to generate the visualization. "
                "Avoid explanations or markdown formatting — output raw Python code only."
                "DO NOT use any machine learning models"

            ),
            verbose=True,
            llm=self.llm
        )


class IntermediateAnalysisPlotlyCodeAgent:
    """
    Agent that generates intermediate-level Plotly visualization code snippets
    with moderate complexity and interactivity.
    """

    def __init__(self, llm):
        self.llm = llm

    def make_agent(self):
        return Agent(
            role="Intermediate Plotly Code Generator",
            goal=(
                "Given a list of intermediate Analysis descriptions, produce Plotly code snippets "
                "with moderate complexity — such as grouped charts, faceting, and light interactivity."
            ),
            backstory=(
                "You are a visualization specialist with experience in building more advanced plots "
                "that go beyond basic charts. You use techniques like subplots, grouped data, "
                "facet grids, and hover templates to make the visualizations engaging. "
                "You still keep the code clean and runnable without external dependencies beyond Plotly. "
                "Only output raw Python code, no explanations."
                "DO NOT use any machine learning models"

            ),
            verbose=True,
            llm=self.llm
        )


class AdvancedAnalysisPlotlyCodeAgent:
    """
    Agent that generates advanced-level Plotly visualization code snippets
    for in-depth data exploration.
    """

    def __init__(self, llm):
        self.llm = llm

    def make_agent(self):
        return Agent(
            role="Advanced Plotly Code Generator",
            goal=(
                "Given a list of advanced Analysis descriptions, produce complex Plotly code snippets "
                "that leverage advanced features such as animations, 3D plots, statistical overlays, "
                "custom callbacks, or multi-view dashboards."
            ),
            backstory=(
                "You are a senior data visualization engineer specializing in high-end exploratory plots. "
                "You integrate interactivity, animations, advanced statistical visualizations, and 3D elements. "
                "Your plots are intended for expert audiences who need deep exploration capabilities. "
                "You output only raw Python code using Plotly (and optionally Plotly Express) that can be run directly. "
                "No explanations, comments, or markdown."
                "DO NOT use any machine learning models"
            ),
            verbose=True,
            llm=self.llm
        )

