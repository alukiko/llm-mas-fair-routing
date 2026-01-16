import asyncio

from automas import AgentNode, PipelineBuilder
from examples.utils import get_data_file


async def main():
    builder = PipelineBuilder()

    builder.add_node(
        AgentNode(
            name="AudioTranscriber",
            instructions="""You are an audio transcription assistant.
            When asked to process audio files, use the audio tools to transcribe them.

            Be brief about the transcription results.""",
            mcp_tools=["media-analysis"],
        )
    )

    pipeline = builder.build()

    sample_audio = get_data_file("1f975693-876d-457b-a649-393859e79bf3.mp3")
    audio_path = str(sample_audio)

    query = f"""Hi, I was out sick from my classes on Friday, so I'm trying to
    figure out what I need to study for my Calculus mid-term next week.
    My friend from class sent me an audio recording of Professor Willowbrook
    giving out the recommended reading for the test, but my headphones are
    broken :(\n\nCould you please listen to the recording for me and tell me
    the page numbers I'm supposed to go over? I've attached a file called
    Homework.mp3 that has the recording. Please provide just the page numbers
    as a comma-delimited list. And please provide the list in ascending order.

    File path: {audio_path}"""

    result = await pipeline.ainvoke(query)

    print(f"\nFinal Result:\n{'-' * 60}")
    print(result)
    print("-" * 60)

    print("Gt: 132, 133, 134, 197, 245")


if __name__ == "__main__":
    asyncio.run(main())
