import asyncio

from automas import AgentNode, PipelineBuilder


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="WebResearcher",
            instructions="""You are a web research assistant using Browser Use.
            When asked to research topics online, use the Browser Use search and reading tools.
            Be thorough and informative about your research results.""",
            mcp_tools=["browser-usage"],
        )
    )

    # Create pipeline
    pipeline = builder.build()

    # Test query - research current technology trends
    query = """
        What was the volume in m^3 of the fish bag that was calculated in the
        University of Leicester paper \"Can Hiccup Supply Enough Fish to
        Maintain a Dragon\u2019s Diet?\""""

    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print("-" * 60)
    print("Ground truth: 0.1777")


if __name__ == "__main__":
    asyncio.run(main())
