from crewai import Agent


class CodesToInsightsAgent:
    """
    Agent responsible for converting raw Plotly code snippets into CodesWithInsights
    using the convert_codes_to_insights tool and Gemini multimodal LLM.
    """

    def __init__(self, llm, tools=[]):
        """
        Initialize the CodesToInsightsAgent.

        Args:
            llm: The language model instance to use (passed through CrewAI).
            tools (list, optional): Additional tools to attach to this agent.
        """
        self.llm = llm
        self.tools = tools

    def make_agent(self):
        """
        Create and return a configured Agent for converting Plotly code snippets
        into CodesWithInsights with storytelling-driven insights.

        The agent:
            - Accepts a list of code snippets + CSV path.
            - Automatically generates figures.
            - Extracts narrative insights using Gemini multimodal.
        """
        return Agent(
            role="Code Insight Narrator",
            goal=(
                "Transform Plotly code snippets into meaningful, structured insights "
                "by first generating figures from the code, then analyzing them with "
                "a multimodal LLM. The output should be a CodesWithInsights object "
                "that blends accuracy with narrative storytelling."
            ),
            backstory=(
                "You are an expert data storyteller who thrives on transforming raw code "
                "into insights that feel alive. You not only execute the code to render "
                "charts but also interpret the visuals, uncover hidden trends, and narrate "
                "the findings in an engaging way. Every dataset becomes a story, and every "
                "chart a chapter in that story."
            ),
            verbose=True,
            llm=self.llm,
            tools=self.tools
        )




class InsightsOrganizerAgent:
    def __init__(self, llm, tools=[]):
        self.llm = llm
        self.tools = tools

    def make_agent(self):
        return Agent(
            role="Insights Organizer",
            goal="Organize all CodesWithInsights (simple, intermediate, advanced) into one structured AllCodesWithInsights object.",
            backstory=(
                "This agent receives three separate CodesWithInsights objects and consolidates them "
                "into a single AllCodesWithInsights for easier consumption and further use."
            ),
            llm=self.llm,
            verbose=True,
            tools=self.tools
        )
    
    