import asyncio

from automas import AgentNode, PipelineBuilder
from examples.utils import get_data_file


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="ImageAnalyzer",
            instructions="""You are an image analysis assistant.
            When asked to analyze images, use the image tools to process them.

            Be brief about the analysis results.""",
            mcp_tools=["media-analysis"],
        )
    )

    pipeline = builder.build()

    sample_image = get_data_file("9318445f-fe6a-4e1b-acbf-c68228c9906a.png")
    image_path = str(sample_image)

    query = f"""As a comma separated list with no whitespace, using the
    provided image provide all the fractions that use / as the fraction
    line and the answers to the sample problems. Order the list by the
    order in which the fractions appear.

    File path: {image_path}"""

    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print("-" * 60)

    print("Gt: 3/4,1/4,3/4,3/4,2/4,1/2,5/35,7/21,30/5,30/5,3/4,1/15,1/3,4/9,1/8,32/23,103/170")


if __name__ == "__main__":
    asyncio.run(main())
