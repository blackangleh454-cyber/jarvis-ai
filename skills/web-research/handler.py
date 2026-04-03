#!/usr/bin/env python3
"""web-research - Live web research using Tavily AI."""
import sys
import os
import json
from datetime import datetime

API_KEY = "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"


def search(query, max_results=5, search_depth="basic", topic="general",
           days=None, include_domains=None, exclude_domains=None):
    """Search the web using Tavily AI."""
    if not query:
        return "No query provided"

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=API_KEY)

        kwargs = {
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "topic": topic,
            "include_answer": True,
            "include_raw_content": False,
        }

        if days:
            kwargs["days"] = days
        if include_domains:
            kwargs["include_domains"] = include_domains if isinstance(include_domains, list) else [include_domains]
        if exclude_domains:
            kwargs["exclude_domains"] = exclude_domains if isinstance(exclude_domains, list) else [exclude_domains]

        response = client.search(**kwargs)

        lines = []

        # AI answer
        if response.get("answer"):
            lines.append(f"ANSWER: {response['answer']}")
            lines.append("")

        # Results
        results = response.get("results", [])
        if not results:
            lines.append("No results found.")
            return "\n".join(lines)

        lines.append(f"SOURCES ({len(results)} results):")
        lines.append("")

        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            url = r.get("url", "")
            content = r.get("content", "")
            score = r.get("score", 0)

            lines.append(f"{i}. {title}")
            lines.append(f"   URL: {url}")
            lines.append(f"   Score: {score:.2f}")
            lines.append(f"   {content[:200]}{'...' if len(content) > 200 else ''}")
            lines.append("")

        return "\n".join(lines)

    except ImportError:
        return "tavily-python not installed. Run: pip install tavily-python"
    except Exception as e:
        return f"Search failed: {e}"


def extract(url):
    """Extract content from a URL."""
    if not url:
        return "No URL provided"

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=API_KEY)

        response = client.extract(url=url)

        results = response.get("results", [])
        if not results:
            return f"No content extracted from {url}"

        lines = [f"Content from {url}:"]
        for r in results:
            raw = r.get("raw_content", "")
            if raw:
                # Truncate if too long
                if len(raw) > 5000:
                    lines.append(raw[:5000] + f"\n\n... (truncated, total {len(raw)} chars)")
                else:
                    lines.append(raw)
            else:
                content = r.get("content", "")
                lines.append(content[:5000] if content else "No content")

        return "\n".join(lines)

    except ImportError:
        return "tavily-python not installed"
    except Exception as e:
        return f"Extract failed: {e}"


def context(query, max_results=5):
    """Get search context optimized for LLMs."""
    if not query:
        return "No query provided"

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=API_KEY)

        response = client.search_context(
            query=query,
            max_results=max_results,
            search_depth="advanced"
        )

        return response if response else "No context found"

    except ImportError:
        return "tavily-python not installed"
    except Exception as e:
        return f"Context search failed: {e}"


def summarize(url):
    """Summarize content from a webpage."""
    if not url:
        return "No URL provided"

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=API_KEY)

        # First extract content
        extract_resp = client.extract(url=url)
        results = extract_resp.get("results", [])

        if not results:
            return f"No content from {url}"

        content = results[0].get("raw_content", results[0].get("content", ""))

        if not content:
            return "No content to summarize"

        # Return the content (JARVIS LLM will summarize it)
        return f"Content to summarize from {url}:\n\n{content[:8000]}"

    except Exception as e:
        return f"Summarize failed: {e}"


def multi_search(queries, max_results=3):
    """Search multiple queries at once."""
    if not queries:
        return "No queries provided"

    if isinstance(queries, str):
        queries = [q.strip() for q in queries.split(",")]

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=API_KEY)

        all_results = []
        for q in queries[:5]:  # Max 5 queries
            response = client.search(
                query=q,
                max_results=max_results,
                search_depth="basic",
                include_answer=True
            )
            all_results.append({
                "query": q,
                "answer": response.get("answer", ""),
                "results": response.get("results", [])[:max_results]
            })

        lines = [f"Multi-query search ({len(queries)} queries):"]
        lines.append("")

        for item in all_results:
            lines.append(f"=== {item['query']} ===")
            if item["answer"]:
                lines.append(f"Answer: {item['answer']}")
            for i, r in enumerate(item["results"], 1):
                lines.append(f"  {i}. {r.get('title', '')} - {r.get('url', '')}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Multi-search failed: {e}"


def news_search(query, max_results=5, days=3):
    """Search for recent news."""
    return search(
        query=query,
        max_results=max_results,
        search_depth="basic",
        topic="news",
        days=days
    )


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    args = sys.argv[2:]

    if cmd == "search":
        if not args:
            print("Usage: search <query> [--depth basic|advanced] [--max N] [--days N] [--topic general|news|finance]")
            sys.exit(1)

        query_parts = []
        depth = "basic"
        max_r = 5
        days = None
        topic = "general"
        i = 0
        while i < len(args):
            if args[i] == "--depth" and i + 1 < len(args):
                depth = args[i + 1]
                i += 2
            elif args[i] == "--max" and i + 1 < len(args):
                max_r = int(args[i + 1])
                i += 2
            elif args[i] == "--days" and i + 1 < len(args):
                days = int(args[i + 1])
                i += 2
            elif args[i] == "--topic" and i + 1 < len(args):
                topic = args[i + 1]
                i += 2
            else:
                query_parts.append(args[i])
                i += 1

        query = " ".join(query_parts)
        print(search(query, max_results=max_r, search_depth=depth, topic=topic, days=days))

    elif cmd == "extract":
        print(extract(args[0]) if args else "Usage: extract <url>")

    elif cmd == "context":
        query = " ".join(args)
        print(context(query) if query else "Usage: context <query>")

    elif cmd == "summarize":
        print(summarize(args[0]) if args else "Usage: summarize <url>")

    elif cmd == "multi":
        queries = args if len(args) > 1 else (args[0].split(",") if args else [])
        print(multi_search(queries) if queries else "Usage: multi <q1> <q2> ...")

    elif cmd == "news":
        query = " ".join(args)
        print(news_search(query) if query else "Usage: news <query>")

    else:
        print("Commands: search, extract, context, summarize, multi, news")
