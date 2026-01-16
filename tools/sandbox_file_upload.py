"""
Example pipeline testing E2B sandbox file upload and processing
"""

import asyncio

from dotenv import load_dotenv

from automas import AgentNode, PipelineBuilder
from examples.utils import get_data_file

load_dotenv()


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="DataAnalyst",
            instructions="""You are a data analyst that works with files in a sandbox.
             You can install and use Pandas or NumPy to analyze the file.

            Your workflow:
            1. Create a new sandbox
            2. Upload the file to the sandbox
            3. Write Python code to analyze the file
            4. Execute the code and return results
            """,
            mcp_tools=["e2b-sandbox"],
        )
    )

    pipeline = builder.build()

    # Get sample CSV file
    csv_file = get_data_file("test_data.csv")

    query = f"""Upload the CSV file at {csv_file} to a sandbox and analyze it.
    Calculate the average score and find the person with the highest score."""

    print(f"\nQuery: {query}")
    print("\nExecuting sandbox file upload test...")
    print("-" * 60)

    result = await pipeline.ainvoke(query)
    print(result)
    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(main())
