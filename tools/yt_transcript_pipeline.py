import asyncio

from automas import AgentNode, PipelineBuilder


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="VideoAnalyzer",
            instructions="""You are a video analysis assistant.
            When given a YouTube URL, use the youtube-transcript tools to get the transcript.

            Be brief about the analysis results.""",
            mcp_tools=["youtube-transcript"],
        )
    )

    pipeline = builder.build()

    query = """Get the transcript from this YouTube video: https://www.youtube.com/watch?v=5j-S448XC8k&list=RDGJb_02HU0mw&index=3

    Summarize the main topics discussed in the video."""

    print(f"\nQuery: {query}")
    print("\nExecuting video analysis pipeline...")
    print("-" * 60)

    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
