"""
Example pipeline using download MCP server
"""

import asyncio

from automas import AgentNode, PipelineBuilder


async def main():
    builder = PipelineBuilder()

    # Create a node that uses the download MCP tool
    builder.add_node(
        AgentNode(
            name="FileDownloader",
            instructions="""You are a file download assistant.
            When asked to download files, use the download tools to save them locally.

            Always provide:
            1. A summary of what you downloaded
            2. File paths where files were saved
            3. File sizes and types if available
            4. Any errors encountered

            Be helpful and informative about the download process.""",
            mcp_tools=["download-url-content"],  # This will use our download MCP server
        )
    )

    # Create pipeline
    pipeline = builder.build()

    # Test query - download a sample file
    query = """Please download this sample JSON file:
    https://jsonplaceholder.typicode.com/posts/1

    Save it to a folder called 'test_downloads' in your downloads directory."""

    print(f"\nQuery: {query}")
    print("\nExecuting download pipeline...")
    print("-" * 60)

    try:
        result = await pipeline.ainvoke(query)

        print(f"\nFinal Result:\n{'-' * 60}")
        print(result)
        print("-" * 60)

    except Exception as e:
        print(f"\nError during execution: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Download pipeline completed!")


async def batch_download_example():
    """Example of batch downloading multiple files"""
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="BatchDownloader",
            instructions="""You are a batch file download assistant.
            When given multiple URLs, download all of them efficiently.

            Provide a detailed summary including:
            - Total files attempted
            - Successful downloads
            - Failed downloads with reasons
            - File locations and sizes

            Use the batch download functionality when possible.""",
            mcp_tools=["download-server"],
        )
    )

    pipeline = builder.build()

    # Multiple file download example
    query = """Please download these sample files:
    1. https://jsonplaceholder.typicode.com/posts/1 (save as 'post1.json')
    2. https://jsonplaceholder.typicode.com/users/1 (save as 'user1.json')
    3. https://httpbin.org/json (save as 'sample.json')

    Save them all to a 'batch_downloads' folder."""

    print("\n\nBatch Download Example:")
    print(f"Query: {query}")
    print("\nExecuting batch download pipeline...")
    print("-" * 60)

    try:
        result = await pipeline.ainvoke(query)

        print(f"\nBatch Download Result:\n{'-' * 60}")
        print(result)
        print("-" * 60)

    except Exception as e:
        print(f"\nError during batch download: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run single file download example
    asyncio.run(main())

    # Run batch download example
    asyncio.run(batch_download_example())
