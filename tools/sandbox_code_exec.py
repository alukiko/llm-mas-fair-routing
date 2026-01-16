"""
Example pipeline using E2B sandbox for code execution and programming tasks
"""

import asyncio

from dotenv import load_dotenv

from automas import AgentNode, PipelineBuilder

load_dotenv()


async def main():
    builder = PipelineBuilder()

    # Create a programmer agent that uses E2B sandbox
    builder.add_node(
        AgentNode(
            name="PythonProgrammer",
            instructions="""You are an expert Python programmer and code executor.
                When asked to solve programming problems or execute code, use the sandbox tools.

                Your workflow should be:
                1. Analyze the programming task or problem
                2. Write appropriate Python code to solve it
                3. Execute the code in a secure sandbox
                4. Debug and fix any issues if needed
            """,
            mcp_tools=["e2b-sandbox"],
        )
    )

    # Create pipeline
    pipeline = builder.build()

    # Test query - solve a mathematical programming problem
    query = """Execute this python code and return the result:
        rows = 5
        for i in range(1, rows + 1):
            print(" " * (rows - i) + "*" * (2 * i - 1))
    """

    print(f"\nQuery: {query}")
    print("\nExecuting programming pipeline...")
    print("-" * 60)

    result = await pipeline.ainvoke(query)

    print(result)
    print("Programming pipeline completed!")


if __name__ == "__main__":
    # Run main programming example
    asyncio.run(main())
