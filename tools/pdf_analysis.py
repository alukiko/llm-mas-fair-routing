import asyncio

from automas import AgentNode, PipelineBuilder
from examples.utils import get_data_file


async def main():
    builder = PipelineBuilder()

    # Create a node that uses the PDF processing MCP tools
    builder.add_node(
        AgentNode(
            name="PDFAnalyzer",
            instructions="""You are a PDF document analysis assistant.
            When asked to analyze PDF documents, use the document server tools to process them.
            When extracting images is requested or seems relevant, use the extract_images parameter.
            Be thorough and informative about the analysis results.""",
            mcp_tools=["document-server"],
        )
    )

    pipeline = builder.build()

    pdf_path = get_data_file("366e2f2b-8632-4ef2-81eb-bc3877489217.pdf")

    query = f"""Analyze the PDF document thoroughly. Extract both text content and any images contained within.

    The file contains information about accommodations in the resort town of Seahorse Island.
    Based on the information in this file, which seems like the better available place to stay
    for a family that enjoys swimming and wants a full house?

    Please extract images from the PDF if any are present and analyze them along with the text content.

    File path: {pdf_path}"""

    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print("-" * 60)

    print("Ground truth: Shelley's place")


if __name__ == "__main__":
    asyncio.run(main())
