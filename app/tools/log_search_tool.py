import os
import time
import requests
from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import datetime

class LogSearchSchema(BaseModel):
    applications: List[str] = Field(description="List of application names to search in")
    query: str = Field(description="Search query string")
    start_time: str = Field(description="Start time in milliseconds since epoch", default=str(int((datetime.datetime.now() - datetime.timedelta(hours=1)).timestamp() * 1000)))
    end_time: str = Field(description="End time in milliseconds since epoch", default=str(int(datetime.datetime.now().timestamp() * 1000)))

class LogSearchTool(BaseTool):
    name: str = "log_search"
    description: str = "Search application logs. Input must be a dictionary with properties: 'applications', 'query', 'start_time' (optional), 'end_time' (optional)."
    args_schema: Type[BaseModel] = LogSearchSchema

    def _run(self, applications: List[str], query: str, start_time: str, end_time: str):
        log_search_api_host = os.getenv("LOG_SEARCH_API_HOST")
        log_search_api_key = os.getenv("LOG_SEARCH_API_KEY")

        if not all([log_search_api_host, log_search_api_key]):
            return "Error: LOG_SEARCH_API_HOST or LOG_SEARCH_API_KEY environment variables are not set."

        headers = {
            "Content-Type": "application/json",
            "x-openapi-key": log_search_api_key,
        }

        # Create search job
        job_url = f"{log_search_api_host}/openapi/v2/search/jobs"
        payload = {
            "applications": applications,
            "query": query,
            "start_time": start_time,
            "end_time": end_time,
        }
        
        try:
            response = requests.post(job_url, headers=headers, json=payload)
            response.raise_for_status()
            job_id = response.json().get("id")

            if not job_id:
                return "Failed to create log search job."

            # Get job results
            result_url = f"{job_url}/{job_id}"
            
            # Use blocking=true to wait for the result
            result_response = requests.get(result_url, headers=headers, params={"blocking": "true"})
            result_response.raise_for_status()
            
            result_data = result_response.json()
            return {
                "state": result_data.get("state"),
                "totalSize": result_data.get("totalSize"),
                "entries": result_data.get("entries", [])[:10],  # Limit to 10 entries
                "message": result_data.get("message"),
            }

        except requests.exceptions.RequestException as e:
            return f"Error during log search: {e}"
