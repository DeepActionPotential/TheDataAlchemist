from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Tuple


# Schemas

class CSVFilePath(BaseModel):    
    file_path: str = Field(..., description="Path to the CSV file to be read into a DataFrame.")




class ColumnInfo(BaseModel):
    name: str
    dtype: str
    num_missing: int
    num_unique: int
    sample_values: List[Any] = Field(default_factory=list)

class DataFrameSummary(BaseModel):
    num_rows: int
    num_columns: int
    columns: List[str]
    dtypes: Dict[str, str]
    missing_values: Dict[str, int]

class DataFrameInfo(BaseModel):
    file_path: str
    summary: DataFrameSummary
    columns_info: List[ColumnInfo]
    sample_data: List[Dict[str, Any]] = Field(default_factory=list)
    raw_dataframe: Optional[List[Dict[str, Any]]] 

    class Config:
        arbitrary_types_allowed = True  # Allow pandas types if needed



class AnalysisRecommendation(BaseModel):
    simple: List[str]
    intermediate: List[str]
    advanced: List[str]

    def to_dict(self) -> Dict[str, List[str]]:
        """
        Convert the AnalysisRecommendation to a dictionary format.
        
        Returns:
            Dict[str, List[str]]: Dictionary with keys 'simple', 'intermediate', 'advanced'.
        """
        return {
            "simple": self.simple,
            "intermediate": self.intermediate,
            "advanced": self.advanced
        }


    
    

class AnalysisCode(BaseModel):
    codes: List[str] = Field(..., description="List of Python code strings for visualizations. Each code should be a valid visualization script.")

    csv_path: str = Field(
        ..., 
        description="Path to the CSV file used in the code snippets. This is included for context and reproducibility.")




class FigureCodeWithImage(BaseModel):
    code: str = Field(
        ..., 
        description="The Python code used to generate the figure"
    )
    
    figure_img_base64: str = Field(
        ...,
        description="Base64 encoded image data representing the figure"
    )


class FiguresCodeWithImage(BaseModel):
    figures: List[FigureCodeWithImage] = Field(
        ...,
        description="List of figures with their corresponding code and base64 image data."
    )




class CodeWithInsights(BaseModel):
    code: str = Field(..., description="Raw Python code string that generates a Plotly figure.")
    insights: str



class CodesWithInsights(BaseModel):
    codes_with_insights: List[CodeWithInsights] = Field(..., description="List of Insgihts with raw code.")



class AllCodesWithInsights(BaseModel):
    simple: CodesWithInsights = Field(..., description="List of simple Insgihts with raw code.")
    intermediate: CodesWithInsights = Field(..., description="List of intermediate Insgihts with raw code.")
    advanced: CodesWithInsights = Field(..., description="List of advanced Insgihts with raw code.")

