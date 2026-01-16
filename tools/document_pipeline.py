import asyncio

from automas import AgentNode, PipelineBuilder


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="DocumentAnalyzer",
            instructions="""You are a document analysis assistant.
            When asked to analyze files, use the document processing tools to read and analyze them.""",
            mcp_tools=["document-server"],
            model="openai/gpt-5-mini",
        )
    )

    # Create pipeline
    pipeline = builder.build()

    # Test query - analyze project configuration files
    query = """Что изображено на картинке в данном документе?
    Если это код, то на каком языке?
    File path: /home/glhf/Downloads/68ccf11a-bcd3-41e5-a5ee-3e29253449e9.docx"""

    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
