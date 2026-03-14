# This file is for testing the railtracks library and its functionality.

import asyncio

# Load the .env file
from dotenv import load_dotenv
load_dotenv()

# Import the railtracks library
import railtracks as rt

print("\n🚂 Railtracks is ready!")
print(f" Example LLMs: {[x for x in dir(rt.llm) if 'LLM' in x]}")

# I. Build first agent
# Step 1: Define your agent
assistant = rt.agent_node(
    llm=rt.llm.GeminiLLM("gemini-2.5-flash"),        # swap LLM anytime (see Section 6)
    system_message="You are an enthusiastic hackathon mentor. Keep answers to 2 sentences.",
)


async def main():
    # Step 2: Call it
    result = await rt.call(assistant, "What's the most important thing to build a winning hackathon project?")
    # Step 3: Print the response
    print(result.text)

    # Helper agent with tools — get sentence from user
    user_sentence = input("\nEnter a sentence to analyze (word count, etc.): ").strip()
    if not user_sentence:
        user_sentence = "How many words does this sentence have?"
    result = await rt.call(helper_agent, user_sentence)
    print(result.text)

    # Structured output: idea generator
    result = await rt.call(
        idea_generator,
        "Generate a hackathon project idea that uses AI to help university students.",
    )
    idea = result.structured
    print(f"💡 {idea.title}")
    print(f"   {idea.description}")
    print(f"   Tech stack: {', '.join(idea.tech_stack)}")
    print(f"   Difficulty: {idea.difficulty}")
    print(f"   Wow factor: {idea.wow_factor}")

    # Multi-agent: project coach delegates to brainstormer + reviewer
    with rt.Session(context={"hack name": "genAI"}, name="Hack Coach") as session:
        result = await rt.call(
            project_coach,
            "Our team is interested in sustainability and machine learning. Help us pick a project! Mention Hackathon name.",
        )
    print(result.text)

    # Streaming: storyteller (tokens appear as they're generated)
    print("📖 Streaming story (tokens appear as they're generated):\n")
    result = await rt.call(storyteller, "Write a micro-story about a developer who built an AI agent at a hackathon.")
    for chunk in result:
        print(chunk, end="", flush=True)
    print("\n\n✅ Stream complete!")

    # RAG: ask hackathon knowledge base
    rag_questions = [
        "What time does the hackathon end?",
        "How will projects be judged?",
        "Where can I get food?",
    ]
    for q in rag_questions:
        result = await rt.call(rag_agent, q)
        print(f"❓ {q}")
        print(f"   {result.text}\n")

# II. Add tools with @rt.function_node
# Tool 1: Word counter
@rt.function_node
def count_words(text: str) -> dict:
    """Count the number of words, characters, and sentences in a piece of text.

    Args:
        text (str): The text to analyze.
    """
    print(f"Count function invoked with input: \"{text}\"")
    words = text.split()
    sentences = [s for s in text.split(".") if s.strip()]
    return {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": len(sentences),
        "avg_word_length": round(sum(len(w) for w in words) / len(words), 1) if words else 0,
    }

# Tool 2: Random Number generator
@rt.function_node
def random_number(min_value: int, max_value: int) -> int:
    """Generate a random integer between min_value and max_value."""
    import random
    return random.randint(min_value, max_value)


# Wire tools into an agent
helper_agent = rt.agent_node(
    name="Helpful Assistant",
    tool_nodes=[count_words, random_number],  # add as many tools as you like!
    llm=rt.llm.GeminiLLM("gemini-2.5-flash"),
)

# III. Structured output with Pydantic
from pydantic import BaseModel, Field
from typing import List, Literal


# Define the shape of the response you want
class HackathonIdea(BaseModel):
    title: str = Field(description="A catchy project name")
    description: str = Field(description="What the project does in 2-3 sentences")
    tech_stack: List[str] = Field(description="List of technologies/frameworks to use")
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        description="Estimated difficulty level"
    )
    wow_factor: str = Field(description="The single most impressive thing about this project")


# Agent that returns a HackathonIdea object
idea_generator = rt.agent_node(
    llm=rt.llm.GeminiLLM("gemini-2.5-flash"),
    system_message="You generate creative, practical hackathon project ideas. Be specific and realistic.",
    output_schema=HackathonIdea,   # <── pass your Pydantic model here
)

# IV. Multi-Agent Composition - Built Agent Teams
# Specialist 1: Idea Generator
brainstormer = rt.agent_node(
    name="Idea Generator",
    llm=rt.llm.GeminiLLM("gemini-2.5-flash"),
    system_message=(
        "You are a creative hackathon idea generator for {hack name} hackathon."
        "When asked for a project idea, propose ONE specific, original idea in 3-4 bullet points."
    ),
    manifest=rt.ToolManifest(
        description="Generates a creative hackathon project idea based on a theme or domain.",
        parameters=[
            rt.llm.Parameter(
                name="theme",
                param_type="string",
                description="The theme or domain for the project idea (e.g., 'healthcare', 'education', 'climate')."
            )
        ],
    ),
)

# Specialist 2: Feasibility Reviewer 
reviewer = rt.agent_node(
    name="Feasibility Reviewer",
    llm=rt.llm.GeminiLLM("gemini-2.5-flash"),
    system_message=(
        "You are a pragmatic hackathon mentor for {hack name} hackathon. When given a project idea, "
        "assess its feasibility in 24 hours. Point out 2 risks and 1 quick win. Be concise."
    ),
    manifest=rt.ToolManifest(
        description="Reviews the feasibility of a hackathon project idea within a 24-hour time constraint.",
        parameters=[
            rt.llm.Parameter(
                name="project_idea",
                param_type="string",
                description="The project idea to evaluate."
            )
        ],
    ),
)

# Coordinator: delegates to both specialists 
project_coach = rt.agent_node(
    name="Project Coach",
    tool_nodes=[brainstormer, reviewer],   # 🔑 agents are just tools!
    llm=rt.llm.GeminiLLM("gemini-2.5-flash"),
    system_message=(
        "You are a hackathon project coach for {hack name} hackathon. When a team tells you their interests, "
        "ask the Idea Generator for an idea, then get the Feasibility Reviewer to evaluate it. "
        "Synthesize both into a short, encouraging project brief."
    ),
)

# V. Streaming responses - real-time output
storyteller = rt.agent_node(
    llm=rt.llm.GeminiLLM("gemini-2.5-flash", stream=True),   # ← just add stream=True
    system_message="You are a creative storyteller. Write vivid, engaging micro-stories under 80 words.",
)

# VI. Visualizer - see inside your agents
import importlib, subprocess, sys, time

if importlib.util.find_spec("railtracks_cli") is None:
    print("⚠️  railtracks-cli is not installed. Run the Setup cell again.")
else:
    # Run 'railtracks init' first (downloads UI assets — only needed once)
    print("🔧 Running 'railtracks init'...")
    init_result = subprocess.run(
        [sys.executable, "-m", "railtracks_cli", "init"],
        capture_output=True, text=True
    )
    if init_result.returncode == 0:
        print("   ✅ Init complete!")
    else:
        # init may print warnings but still succeed; show output for debugging
        print(f"   Init output: {init_result.stdout or init_result.stderr}")

    # Launch 'railtracks viz' as a background process so the notebook stays responsive
    print("🚀 Launching visualizer in the background...")
    viz_proc = subprocess.Popen(
        [sys.executable, "-m", "railtracks_cli", "viz"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)  # give the server a moment to start

    if viz_proc.poll() is None:
        print("   ✅ Visualizer is running at http://localhost:8000")
        print("   Open that URL in your browser to see your agent runs in real-time.")
        print()
        print("   To stop the server later, run:  viz_proc.terminate()")
    else:
        print("   ⚠️  Server exited early. Check that port 8000 is free and try again.")

# VII. RAG as a Tool - give your agent long-term memory
from openai import OpenAI

# Install chromadb via: pip install chromadb (add to requirements.txt if needed)
from railtracks.vector_stores import ChromaVectorStore, Chunk

# 1. Embedding function (Use your custom choice) 
_openai_client = OpenAI()  # uses OPENAI_API_KEY from .env

def embedding_function(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings using OpenAI text-embedding-3-small."""
    response = _openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]


# 2. Choose a store type (pick one, others are commented out)
# Option A: Temporary / in-RAM (resets when the kernel restarts — great for demos)
store = ChromaVectorStore(
    collection_name="hackathon_kb",
    embedding_function=embedding_function,
)

# Option B: Persistent local ChromaDB (survives restarts, data saved to disk)
# store = ChromaVectorStore(
#     collection_name="hackathon_kb",
#     embedding_function=embedding_function,
#     path="./chroma_db",          # relative path works fine
# )

# Option C: Remote ChromaDB server
# store = ChromaVectorStore(
#     collection_name="hackathon_kb",
#     embedding_function=embedding_function,
#     host="chroma.example.local",
#     port=8000,
# )


# 3. Build Chunk objects from your documents 
# Each Chunk has: content (required), document, metadata (optional)
articles_data = [
    {"content": "The hackathon runs for 24 hours, starting Friday 6 PM and ending Saturday 6 PM.",
     "document": "schedule.txt", "title": "Schedule", "author": "Organizers", "date": "2026-03-11"},
    {"content": "Teams must have between 2 and 5 members. Solo participation is not allowed.",
     "document": "rules.txt", "title": "Team Rules", "author": "Organizers", "date": "2026-03-11"},
    {"content": "Projects must be original work created during the hackathon. No pre-built codebases.",
     "document": "rules.txt", "title": "Originality Rule", "author": "Organizers", "date": "2026-03-11"},
    {"content": "The prize for 1st place is $5,000 cash plus cloud credits worth $10,000.",
     "document": "prizes.txt", "title": "Prizes", "author": "Organizers", "date": "2026-03-11"},
    {"content": "Judging criteria: Innovation (30%), Technical execution (30%), Impact (20%), Presentation (20%).",
     "document": "judging.txt", "title": "Judging", "author": "Organizers", "date": "2026-03-11"},
    {"content": "Free food and drinks are available 24/7 in the main hall on Floor 2.",
     "document": "logistics.txt", "title": "Food", "author": "Organizers", "date": "2026-03-11"},
    {"content": "Mentors are available at the help desk on Floor 1 from 8 AM to midnight.",
     "document": "logistics.txt", "title": "Mentors", "author": "Organizers", "date": "2026-03-11"},
    {"content": "Project submissions are due at 5:30 PM Saturday via the DevPost portal.",
     "document": "schedule.txt", "title": "Submission Deadline", "author": "Organizers", "date": "2026-03-11"},
    {"content": "Each team gets 3 minutes to demo their project plus 2 minutes for Q&A.",
     "document": "schedule.txt", "title": "Demo Format", "author": "Organizers", "date": "2026-03-11"},
    {"content": "Railtracks is a Python-first framework for building agentic AI systems with built-in visualization.",
     "document": "railtracks.txt", "title": "About Railtracks", "author": "Railtracks Team", "date": "2026-03-11"},
]

chunks = []
for article in articles_data:
    chunk = Chunk(
        content=article["content"],
        document=article["document"],
        metadata={
            "title": article["title"],
            "author": article["author"],
            "date": article["date"],
        },
    )
    chunks.append(chunk)

# upsert() adds new chunks and updates existing ones (safe to re-run)
id_list = store.upsert(chunks)
print(f"✅ Upserted {len(id_list)} chunks into the vector store")


# 4. Wrap the search as a tool
@rt.function_node
def search_knowledge_base(query: str) -> str:
    """Search the hackathon knowledge base for rules, prizes, schedule, or logistics.

    Args:
        query (str): The question or keyword to search for (e.g., 'prize money', 'submission deadline').
    """
    results = store.search(query, top_k=3)
    if not results:
        return "No relevant information found in the knowledge base."
    # Each result is a Chunk — use .content and .metadata
    return "\n".join(
        f"- [{r.metadata.get('title', 'doc')}] {r.content}" for r in results
    )


# 5. Create a RAG-powered agent
rag_agent = rt.agent_node(
    name="Hackathon Assistant",
    tool_nodes=[search_knowledge_base],
    llm=rt.llm.GeminiLLM("gemini-2.5-flash"),
    system_message=(
        "You are a helpful hackathon assistant. Always use the search_knowledge_base tool "
        "to look up accurate information before answering. "
        "If the answer isn't in the knowledge base, say so honestly."
    ),
)

# 6. RAG questions are run from main() (see above)

if __name__ == "__main__":
    asyncio.run(main())

