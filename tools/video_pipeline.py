import asyncio

from automas import AgentNode, PipelineBuilder


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="VideoAnalyzer",
            instructions="""You are an video analysis assistant.
            When asked to analyze videos, use the video tools to process them.

            Be brief about the analysis results.""",
            mcp_tools=["media-analysis"],
        )
    )

    pipeline = builder.build()

    query = """In the video https://www.youtube.com/watch?v=L1vXCYZAYYM, what is the highest number of bird species to be on camera simultaneously?"""
    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
