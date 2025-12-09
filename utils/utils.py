
from schemas.schemas import DataFrameInfo, DataFrameSummary, ColumnInfo, FigureCodeWithImage, FiguresCodeWithImage, CodesWithInsights, CodeWithInsights, AllCodesWithInsights
from crewai.tools import tool
import time

import base64
import pandas as pd
import plotly.express as px
import plotly.io as pio

from config import InsightsLLMConfig

@tool
def create_dataframe_info(file_path: str, include_full_df: bool = True) -> DataFrameInfo:
    """
    Create a detailed DataFrameInfo object from a CSV file.

    This function loads a CSV file into a Pandas DataFrame and generates a 
    structured representation of the dataset using the DataFrameInfo Pydantic model.
    The returned object contains general dataset statistics, per-column metadata, 
    and optional raw data for downstream analysis or storytelling.

    The generated metadata includes:
        - Overall dataset shape (number of rows and columns) 
        - List of column names
        - Data types for each column
        - Count of missing values per column
        - Per-column details (unique values count, sample values, dtype, missing count)
        - A preview of the first 5 rows
        - (Optional) The full dataset in JSON-serializable format

    Args:
        file_path (str):
            Path to the CSV file to be read into a DataFrame.
        include_full_df (bool, optional):
            Whether to include the entire DataFrame as a JSON-serializable list 
            in the `raw_dataframe` field. 
            Defaults to False to reduce memory usage.

    Returns:
        DataFrameInfo:
            A validated Pydantic object containing dataset-level and per-column 
            information, ready for use in other agents or storage.

    Raises:
        ValueError:
            If the loaded DataFrame is empty, indicating an invalid or empty CSV file.
        FileNotFoundError:
            If the provided file_path does not exist or cannot be accessed.
        pandas.errors.ParserError:
            If the CSV file is malformed and cannot be parsed.

    Example:
        >>> df_info = create_dataframe_info("data/sales.csv", include_full_df=False)

    """
    # Load the DataFrame
    df = pd.read_csv(file_path)
    
    if df.empty:
        raise ValueError("The DataFrame is empty. Please provide a valid CSV file.")

    # Create summary
    summary = DataFrameSummary(
        num_rows=df.shape[0],
        num_columns=df.shape[1],
        columns=list(df.columns),
        dtypes=df.dtypes.astype(str).to_dict(),
        missing_values=df.isnull().sum().to_dict()
    )

    # Detailed column info
    columns_info = []
    for col in df.columns:
        col_info = ColumnInfo(
            name=col,
            dtype=str(df[col].dtype),
            num_missing=int(df[col].isnull().sum()),
            num_unique=int(df[col].nunique()),
            sample_values=df[col].dropna().unique()[:3].tolist()  # 3 sample values
        )
        columns_info.append(col_info)

    # Prepare DataFrameInfo
    df_info = DataFrameInfo(
        file_path=file_path,
        summary=summary,
        columns_info=columns_info,
        sample_data=df.head(5).to_dict(orient="records"),
        raw_dataframe=df.to_dict(orient="records") if include_full_df else None
    )

    return df_info


def figure_to_base64(fig) -> str:
    """
    Convert a Plotly figure to a base64-encoded PNG string.

    Args:
        fig (plotly.graph_objs._figure.Figure):
            A Plotly figure object.

    Returns:
        str: Base64 encoded PNG image.
    """
    try:
        img_bytes = pio.to_image(fig, format="png")
        return base64.b64encode(img_bytes).decode("utf-8")
    except Exception as e:
        return base64.b64encode(
            f"Image export failed: {str(e)}".encode("utf-8")
        ).decode("utf-8")


def extract_plotly_base64_from_code(code: str, csv_path: str) -> FigureCodeWithImage:
    """
    Executes a given Plotly code snippet, loads a dataset from a CSV file into `data`,
    and extracts the resulting figure as a base64-encoded image.
    """

    # Load dataset into variable `data`
    data = pd.read_csv(csv_path)
    globals_vars = {"pd": pd, "data": data, "px": px}

    try:
        exec(code, globals_vars)
    except Exception as e:
        return FigureCodeWithImage(
            code=code,
            figure_img_base64=base64.b64encode(
                f"Code execution failed: {str(e)}".encode("utf-8")
            ).decode("utf-8")
        )

    # Find the first Plotly Figure object
    fig = None
    for var in globals_vars.values():
        if "Figure" in str(type(var)):
            fig = var
            break

    if not fig:
        return FigureCodeWithImage(
            code=code,
            figure_img_base64=base64.b64encode(
                b"No Plotly Figure found"
            ).decode("utf-8")
        )

    return FigureCodeWithImage(
        code=code,
        figure_img_base64=figure_to_base64(fig)
    )


def convert_analysis_to_figures(codes: list[str], csv_path: str) -> FiguresCodeWithImage:
    """
    Converts a list of code snippets into base64-encoded Plotly figure images.
    """
    codes_figures = [extract_plotly_base64_from_code(code, csv_path) for code in codes]

    print("------------------------------------------------------------------------")
    print(f"Extracted {len(codes_figures)} figures from {len(codes)} code snippets.")
    print("------------------------------------------------------------------------")

    return FiguresCodeWithImage(figures=codes_figures)




from litellm import completion
from schemas.schemas import CodeWithInsights, CodesWithInsights

def convert_figure_to_insights(figure: FigureCodeWithImage, retries: int = 0) -> CodeWithInsights:
    """
    Converts a single FigureCodeWithImage to insights using Gemini multimodal LLM.
    Retries insight generation upon failure, up to max_retries.
    """
    api_key = InsightsLLMConfig.api_key
    model_name = InsightsLLMConfig.model_name
    insights_command = InsightsLLMConfig.insights_command

    retry_upon_fall = InsightsLLMConfig.retry_upon_fall
    max_retries = InsightsLLMConfig.max_retries
    time_to_sleep_between_retries = InsightsLLMConfig.time_to_sleep_between_retries

    img_base64 = figure.figure_img_base64

    try:
        response = completion(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": insights_command},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                    ]
                }
            ],
            api_key=api_key,
        )
        insights_text = response["choices"][0]["message"]["content"]


    except Exception as e:
        if retry_upon_fall and retries < max_retries:
            print('retrying', retries, e)
            time.sleep(time_to_sleep_between_retries)
            return convert_figure_to_insights(figure, retries=retries + 1)
        # insights_text = f"Insight generation failed: {str(e)}"
        insights_text = ""
    

    return CodeWithInsights(
                code=figure.code,
                insights=insights_text
            )
        
    


def convert_figures_to_insights(figures: FiguresCodeWithImage) -> CodesWithInsights:
    """
    Converts a collection of Plotly figures (serialized as code + base64 images) into
    human-readable insights using a multimodal Gemini LLM.

    Workflow:
        1. Iterates over each `FigureCodeWithImage` object in the input.
        2. For each figure, calls `convert_figure_to_insights`, which sends the figure’s
           code and base64-encoded image to the Gemini model.
        3. Collects the returned insights (wrapped as `CodeWithInsights`) for all figures.
        4. Aggregates them into a single `CodesWithInsights` object.

    Args:
        figures (FiguresCodeWithImage):
            A container holding multiple figures, where each figure has:
                - `code`: The original Plotly code snippet that produced the figure.
                - `figure_img_base64`: A base64-encoded PNG representation of the figure.
        

    Returns:
        CodesWithInsights:
            An object containing a list of `CodeWithInsights`, where each entry links
            the original Plotly code with generated textual insights from the LLM.

    Notes:
        - If any figure fails during insight generation, the returned insight will
          contain the error message instead of analysis.
    """

    all_codes_with_insights = []

    n = 0

    for figure in figures.figures:
        time.sleep(InsightsLLMConfig.time_to_sleep_between_requests)
        result = convert_figure_to_insights(figure)
      
        if not result.insights:
            continue

        all_codes_with_insights.append(result)
        print(f"Processed figure with code: {figure.code[:50]}... | Insights: {result.insights[:100]}...")
        n += 1 
        print(f"Total processed so far: {n} figures")
    

    return CodesWithInsights(codes_with_insights=all_codes_with_insights)


@tool
def convert_codes_to_insights(codes: list[str], csv_path: str) -> CodesWithInsights:
    """
    Converts a list of Plotly code snippets into structured insights using the Gemini multimodal LLM.
    
    Workflow:
        1. Takes user-provided Plotly code snippets.
        2. Executes the snippets on the given CSV dataset to generate Plotly figures.
        3. Converts each figure into a base64-encoded image.
        4. Sends each image to the Gemini multimodal model to extract 4–6 narrative-style insights.
        5. Returns all insights combined into a CodesWithInsights object.

    Args:
        codes (list[str]): A list of Python code snippets that generate Plotly figures.
        csv_path (str): The path to the CSV dataset that the code snippets depend on.

    Returns:
        CodesWithInsights:
            A structured object containing the original code snippets and
            their corresponding narrative-driven insights, suitable for
            reporting, dashboards, or storytelling use cases.

    Raises:
        ValueError: If no code snippets are provided or if the CSV path is invalid.
    """
    if not codes:
        raise ValueError("No code snippets provided for conversion into insights.")
    if not csv_path:
        raise ValueError("CSV path must be provided.")

    # Step 1: Convert code snippets into figures with base64 images
    figures = convert_analysis_to_figures(codes, csv_path)

    # Step 2: Convert those figures into insights using Gemini multimodal
    return convert_figures_to_insights(figures)


