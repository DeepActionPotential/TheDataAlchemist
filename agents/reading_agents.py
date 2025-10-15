from crewai import Agent

class DataReaderAgent:
    """
    Agent responsible for reading a CSV dataset and generating detailed DataFrame information.

    This agent uses a provided language model (llm) and a DataFrame info service
    to create an agent capable of loading a dataset and producing structured metadata
    using the CreateDataFrameInfo tool.

    Attributes:
        llm: The language model to be used by the agent.
        dataframe_info_service: Service providing the CreateDataFrameInfo tool.
    """

    def __init__(self, llm, tools=[]):
        """
        Initialize the DataReaderAgent.

        Args:
            llm: The language model instance to use.
            tools: tools used to create the agent.
        """
        self.llm = llm
        self.tools = tools


    def make_agent(self):
        """
        Create and return a configured Agent for reading CSV data and extracting DataFrame details.

        Returns:
            Agent: An instance of the Agent class configured for DataFrame analysis.
        """
        return Agent(
            role="Data Reader Agent",
            goal="Load a CSV file and produce a structured DataFrameInfo object using the CreateDataFrameInfo tool.",
            backstory=(
                "You are a data analysis assistant specialized in reading CSV datasets "
                "and extracting detailed structured information about them. "
                "You leverage the CreateDataFrameInfo tool to generate validated metadata, "
                "including dataset shape, column details, missing values, and sample data."
            ),
            tools=self.tools,  # Must include CreateDataFrameInfo
            verbose=True,
            llm=self.llm
        )



