import asyncio

from automas import AgentNode, PipelineBuilder
from examples.utils import get_data_file


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="ExcelAnalyzer",
            instructions="""You are an Excel spreadsheet analysis assistant.
            When asked to analyze Excel files, use the document server tools to process them.""",
            mcp_tools=["document-server"],
        )
    )

    # Create pipeline
    pipeline = builder.build()

    excel_path = get_data_file("7cc4acfa-63fd-4acc-a1a1-e8e529e0a97f.xlsx")

    # Test query - analyze sample Excel
    query = f"""The attached spreadsheet contains the sales of menu items
    for a regional fast-food chain. Which city had the greater
    total sales: Wharvton or Algrimand?

    File path: {excel_path}"""

    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print("-" * 60)
    print("Ground truth: Wharvton")


if __name__ == "__main__":
    asyncio.run(main())
