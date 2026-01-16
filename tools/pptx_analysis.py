import asyncio

from automas import AgentNode, PipelineBuilder
from examples.utils import get_data_file


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="PPTXAnalyzer",
            instructions="""You are a PowerPoint presentation analysis assistant.
            When asked to analyze PPTX presentations, use the document server tools to process them.""",
            mcp_tools=["document-server"],
        )
    )

    pipeline = builder.build()

    pptx_path = get_data_file("a3fbeb63-0e8c-4a11-bff6-0e3b484c3e9c.pptx")

    query = f""""How many slides in this PowerPoint presentation mention crustaceans?"

    File path: {pptx_path}"""

    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print("-" * 60)
    print("Ground truth: 4")


if __name__ == "__main__":
    asyncio.run(main())
