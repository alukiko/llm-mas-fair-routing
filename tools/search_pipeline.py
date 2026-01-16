import asyncio

from automas import AgentNode, PipelineBuilder


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="WebResearcher",
            instructions="""You are a web research assistant
            Be thorough and informative about your research results.""",
            mcp_tools=["web-search"],
        )
    )

    pipeline = builder.build()

    query = """
    What was the volume in m^3 of the fish bag that was calculated in the University of Leicester paper "Can Hiccup Supply Enough Fish to Maintain a Dragon’s Diet?
    """

    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print(f"Usage: {pipeline.cost}")


if __name__ == "__main__":
    asyncio.run(main())
