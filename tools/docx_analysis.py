import asyncio

from automas import AgentNode, PipelineBuilder
from examples.utils import get_data_file


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="DOCXAnalyzer",
            instructions="""You are a Word document analysis assistant.
            When asked to analyze DOCX documents, use the document server tools to process them.""",
            mcp_tools=["document-server"],
        )
    )

    # Create pipeline
    pipeline = builder.build()

    docx_path = get_data_file("cffe0e32-c9a6-4c52-9877-78ceb4aaa9fb.docx")

    query = f"""An office held a Secret Santa gift exchange where each of its
    twelve employees was assigned one other employee in the group to present
    with a gift. Each employee filled out a profile including three
    likes or hobbies. On the day of the gift exchange, only eleven gifts were
    given, each one specific to one of the recipient's interests.
    Based on the information in the document, who did not give a gift?

    File path: {docx_path}"""

    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print("-" * 60)
    print("Ground truth: Fred")


if __name__ == "__main__":
    asyncio.run(main())
