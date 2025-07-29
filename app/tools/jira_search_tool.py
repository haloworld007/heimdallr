import os
from crewai.tools import BaseTool
from jira import JIRA
from typing import Type
from pydantic import BaseModel, Field

class JiraSearchSchema(BaseModel):
    issue_key: str = Field(description="The Jira issue key, e.g. PROJ-123")

class JiraSearchTool(BaseTool):
    name: str = "jira_search"
    description: str = "Search and retrieve details of a Jira issue by its key."
    args_schema: Type[BaseModel] = JiraSearchSchema

    def _run(self, issue_key: str):
        try:
            jira_server = os.getenv("JIRA_SERVER")
            jira_access_token = os.getenv("JIRA_ACCESS_TOKEN")

            if not all([jira_server, jira_access_token]):
                return "Error: JIRA_SERVER or JIRA_ACCESS_TOKEN environment variables are not set."

            # Use Bearer token authentication with access token
            headers = JIRA.DEFAULT_OPTIONS["headers"].copy()
            headers["Authorization"] = f"Bearer {jira_access_token}"
            
            jira = JIRA(server=jira_server, options={"headers": headers})
            issue = jira.issue(issue_key)
            
            return {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": issue.fields.description,
                "status": issue.fields.status.name,
                "priority": issue.fields.priority.name if issue.fields.priority else "None",
            }
        except Exception as e:
            return f"Error fetching Jira issue: {e}"

