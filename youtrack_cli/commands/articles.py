"""Articles command group for YouTrack CLI."""

import asyncio
from pathlib import Path
from typing import Optional

import click

from ..auth import AuthManager
from ..console import get_console


@click.group()
def articles() -> None:
    """Manage knowledge base articles."""
    pass


@articles.command(name="create")
@click.argument("title")
@click.option(
    "--content",
    "-c",
    help="Article content (required if --file not specified)",
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, path_type=Path),
    help="Path to markdown file containing article content (required if --content not specified)",
)
@click.option(
    "--project-id",
    "-p",
    required=True,
    help="Project ID or short name to associate with the article (required)",
)
@click.option(
    "--parent-id",
    help="Parent article ID for nested articles",
)
@click.option(
    "--summary",
    "-s",
    help="Article summary (defaults to title)",
)
@click.option(
    "--visibility",
    type=click.Choice(["public", "private", "project"]),
    default="public",
    help="Article visibility level",
)
@click.pass_context
def create(
    ctx: click.Context,
    title: str,
    content: Optional[str],
    file: Optional[Path],
    project_id: str,
    parent_id: Optional[str],
    summary: Optional[str],
    visibility: str,
) -> None:
    """Create a new article.

    Create a new knowledge base article with the specified title.
    Either --content or --file must be provided along with --project-id.

    Examples:
        # Create article with inline content
        yt articles create "Installation Guide" --content "Follow these steps..." --project-id DOCS

        # Create article from file
        yt articles create "API Reference" --file ./api-docs.md --project-id DOCS

        # Create article with visibility setting
        yt articles create "Internal Notes" --content "Team notes..." --project-id TEAM --visibility private
    """
    from ..articles import ArticleManager

    console = get_console()

    # Validate that either content or file is provided, but not both
    if content and file:
        console.print("❌ Cannot specify both --content and --file options", style="red")
        console.print("💡 Use either --content for inline text or --file for file content, not both", style="blue")
        raise click.ClickException("Use either --content or --file, not both")

    if not content and not file:
        console.print("❌ Either --content or --file must be specified", style="red")
        console.print(
            '💡 Try: yt articles create "Title" --content "Your content here" --project-id PROJECT', style="blue"
        )
        console.print('💡 Or:  yt articles create "Title" --file ./content.md --project-id PROJECT', style="blue")
        raise click.ClickException("Article content is required")

    # Read content from file if provided
    if file:
        try:
            console.print(f"📖 Reading content from '{file}'...", style="blue")
            content = file.read_text(encoding="utf-8")
            if not content.strip():
                console.print(f"❌ File '{file}' is empty", style="red")
                raise click.ClickException("File content cannot be empty")
        except UnicodeDecodeError:
            console.print(f"❌ File '{file}' is not a valid text file", style="red")
            raise click.ClickException("File must be a valid text file") from None
        except Exception as e:
            console.print(f"❌ Error reading file '{file}': {e}", style="red")
            raise click.ClickException("Failed to read file") from e

    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"📝 Creating article '{title}'...", style="blue")

    # At this point, content is guaranteed to be a string due to validation above
    assert content is not None

    try:
        result = asyncio.run(
            article_manager.create_article(
                title=title,
                content=content,
                project_id=project_id,
                parent_id=parent_id,
                summary=summary,
                visibility=visibility,
            )
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
            article = result["data"]
            console.print(f"Article ID: {article.get('id', 'N/A')}", style="blue")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to create article")

    except Exception as e:
        console.print(f"❌ Error creating article: {e}", style="red")
        raise click.ClickException("Failed to create article") from e


@articles.command()
@click.argument("article_id")
@click.option(
    "--title",
    "-t",
    help="New article title",
)
@click.option(
    "--content",
    "-c",
    help="New article content",
)
@click.option(
    "--summary",
    "-s",
    help="New article summary",
)
@click.option(
    "--visibility",
    type=click.Choice(["public", "private", "project"]),
    help="New visibility level",
)
@click.option(
    "--show-details",
    is_flag=True,
    help="Show detailed article information",
)
@click.pass_context
def edit(
    ctx: click.Context,
    article_id: str,
    title: Optional[str],
    content: Optional[str],
    summary: Optional[str],
    visibility: Optional[str],
    show_details: bool,
) -> None:
    """Edit an existing article."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    if show_details:
        console.print(f"📋 Fetching article '{article_id}' details...", style="blue")

        try:
            result = asyncio.run(article_manager.get_article(article_id))

            if result["status"] == "success":
                article_manager.display_article_details(result["data"])
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to get article details")

        except Exception as e:
            console.print(f"❌ Error getting article details: {e}", style="red")
            raise click.ClickException("Failed to get article details") from e
    else:
        if not any([title, content, summary, visibility]):
            console.print("❌ No updates specified.", style="red")
            console.print(
                "Use --title, --content, --summary, or --visibility options, "
                "or --show-details to view current article.",
                style="blue",
            )
            return

        console.print(f"✏️  Updating article '{article_id}'...", style="blue")

        try:
            result = asyncio.run(
                article_manager.update_article(
                    article_id=article_id,
                    title=title,
                    content=content,
                    summary=summary,
                    visibility=visibility,
                )
            )

            if result["status"] == "success":
                console.print(f"✅ {result['message']}", style="green")
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to update article")

        except Exception as e:
            console.print(f"❌ Error updating article: {e}", style="red")
            raise click.ClickException("Failed to update article") from e


@articles.command()
@click.argument("article_id")
@click.pass_context
def publish(ctx: click.Context, article_id: str) -> None:
    """Publish a draft article."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"🚀 Publishing article '{article_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.publish_article(article_id))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to publish article")

    except Exception as e:
        console.print(f"❌ Error publishing article: {e}", style="red")
        raise click.ClickException("Failed to publish article") from e


@articles.command(name="list")
@click.option(
    "--project-id",
    "-p",
    help="Filter by project ID",
)
@click.option(
    "--parent-id",
    help="Filter by parent article ID",
)
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of fields to return",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of articles to return (legacy, use --page-size instead)",
)
@click.option(
    "--query",
    "-q",
    help="Search query to filter articles",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.option(
    "--page-size",
    type=int,
    default=100,
    help="Number of articles per page (default: 100)",
)
@click.option(
    "--after-cursor",
    help="Start pagination after this cursor",
)
@click.option(
    "--before-cursor",
    help="Start pagination before this cursor",
)
@click.option(
    "--all",
    is_flag=True,
    help="Fetch all results using pagination",
)
@click.option(
    "--max-results",
    type=int,
    help="Maximum total number of results to fetch",
)
@click.pass_context
def list_articles(
    ctx: click.Context,
    project_id: Optional[str],
    parent_id: Optional[str],
    fields: Optional[str],
    top: Optional[int],
    query: Optional[str],
    format: str,
    page_size: int,
    after_cursor: Optional[str],
    before_cursor: Optional[str],
    all: bool,
    max_results: Optional[int],
) -> None:
    """List articles with filtering."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print("📚 Fetching articles...", style="blue")

    try:
        # Determine pagination settings
        use_pagination = bool(all or after_cursor or before_cursor or max_results)

        result = asyncio.run(
            article_manager.list_articles(
                project_id=project_id,
                parent_id=parent_id,
                fields=fields,
                top=top,
                query=query,
                page_size=page_size,
                after_cursor=after_cursor,
                before_cursor=before_cursor,
                use_pagination=use_pagination,
                max_results=max_results,
            )
        )

        if result["status"] == "success":
            articles = result["data"]

            if format == "table":
                article_manager.display_articles_table(articles)
                console.print(f"\n[dim]Total: {result['count']} articles[/dim]")

                # Display pagination info if available
                if "pagination" in result:
                    pagination = result["pagination"]
                    if pagination["has_after"] or pagination["has_before"]:
                        console.print("[dim]Pagination:[/dim]", end="")
                        if pagination["after_cursor"]:
                            console.print(f" [dim]next: --after-cursor {pagination['after_cursor']}[/dim]", end="")
                        if pagination["before_cursor"]:
                            console.print(f" [dim]prev: --before-cursor {pagination['before_cursor']}[/dim]", end="")
                        console.print()
            else:
                import json

                console.print(json.dumps(articles, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list articles")

    except Exception as e:
        console.print(f"❌ Error listing articles: {e}", style="red")
        raise click.ClickException("Failed to list articles") from e


@articles.command()
@click.option(
    "--project-id",
    "-p",
    help="Filter by project ID",
)
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of fields to return",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of articles to return",
)
@click.option(
    "--show-metadata",
    is_flag=True,
    default=True,
    help="Show metadata like authors and dates",
)
@click.option(
    "--enhanced",
    is_flag=True,
    help="Use enhanced tree display with additional metadata",
)
@click.pass_context
def tree(
    ctx: click.Context,
    project_id: Optional[str],
    fields: Optional[str],
    top: Optional[int],
    show_metadata: bool,
    enhanced: bool,
) -> None:
    """Display articles in hierarchical tree structure."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print("🌳 Fetching articles tree...", style="blue")

    try:
        result = asyncio.run(
            article_manager.list_articles(
                project_id=project_id,
                fields=fields,
                top=top,
            )
        )

        if result["status"] == "success":
            articles = result["data"]

            if enhanced:
                # Use enhanced tree display
                from ..trees import create_enhanced_articles_tree

                tree = create_enhanced_articles_tree(articles, show_metadata=show_metadata)
                console.print(tree)
            else:
                # Use original tree display
                article_manager.display_articles_tree(articles)

            console.print(f"\n[dim]Total: {result['count']} articles[/dim]")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to fetch articles tree")

    except Exception as e:
        console.print(f"❌ Error fetching articles tree: {e}", style="red")
        raise click.ClickException("Failed to fetch articles tree") from e


@articles.command(name="search")
@click.argument("query")
@click.option(
    "--project-id",
    "-p",
    help="Filter by project ID",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of results to return",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def search(
    ctx: click.Context,
    query: str,
    project_id: Optional[str],
    top: Optional[int],
    format: str,
) -> None:
    """Search articles."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"🔍 Searching articles for '{query}'...", style="blue")

    try:
        result = asyncio.run(
            article_manager.search_articles(
                query=query,
                project_id=project_id,
                top=top,
            )
        )

        if result["status"] == "success":
            articles = result["data"]

            if format == "table":
                article_manager.display_articles_table(articles)
                console.print(f"\n[dim]Found: {result['count']} articles[/dim]")
            else:
                import json

                console.print(json.dumps(articles, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to search articles")

    except Exception as e:
        console.print(f"❌ Error searching articles: {e}", style="red")
        raise click.ClickException("Failed to search articles") from e


@articles.command()
@click.option(
    "--project-id",
    "-p",
    help="Filter by project ID",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def draft(
    ctx: click.Context,
    project_id: Optional[str],
    format: str,
) -> None:
    """Manage article drafts."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print("📝 Fetching draft articles...", style="blue")

    try:
        result = asyncio.run(
            article_manager.list_articles(
                project_id=project_id,
            )
        )

        if result["status"] == "success":
            # Filter articles to show only drafts (non-published articles)
            # Published articles have visibility type "UnlimitedVisibility"
            # Draft articles should have different visibility types
            all_articles = result["data"]
            draft_articles = [
                article
                for article in all_articles
                if article.get("visibility", {}).get("$type") != "UnlimitedVisibility"
            ]

            if format == "table":
                article_manager.display_articles_table(draft_articles)
                console.print(f"\n[dim]Total drafts: {len(draft_articles)} articles[/dim]")
            else:
                import json

                console.print(json.dumps(draft_articles, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list draft articles")

    except Exception as e:
        console.print(f"❌ Error listing draft articles: {e}", style="red")
        raise click.ClickException("Failed to list draft articles") from e


@articles.command()
@click.argument("parent_id")
@click.option(
    "--sort-by",
    type=click.Choice(["title", "created", "updated"], case_sensitive=False),
    default="title",
    help="Sort child articles by title, creation date, or update date for display only",
)
@click.option(
    "--reverse",
    is_flag=True,
    help="Reverse the sort order",
)
@click.pass_context
def sort(
    ctx: click.Context,
    parent_id: str,
    sort_by: str,
    reverse: bool,
) -> None:
    """Display child articles under a parent article in sorted order.

    IMPORTANT: YouTrack does not provide an API to reorder articles automatically.
    This command displays articles in sorted order for reference only.
    To actually reorder articles, use YouTrack's web interface drag-and-drop functionality.
    """
    from ..articles import ArticleManager

    console = get_console()
    config = ctx.obj.get("config") if ctx.obj else None
    auth_manager = AuthManager(config)
    article_manager = ArticleManager(auth_manager)

    console.print(f"📋 Fetching child articles for '{parent_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.list_articles(parent_id=parent_id))

        if result["status"] == "success":
            articles = result["data"]

            if not articles:
                console.print("No child articles found.", style="yellow")
                return

            # Sort articles based on the specified criteria
            def get_title_key(x):
                return x.get("summary", "").lower()

            def get_created_key(x):
                return x.get("created", 0)

            def get_updated_key(x):
                return x.get("updated", 0)

            sort_key = None
            if sort_by == "title":
                sort_key = get_title_key
            elif sort_by == "created":
                sort_key = get_created_key
            elif sort_by == "updated":
                sort_key = get_updated_key

            if sort_key:
                articles = sorted(articles, key=sort_key, reverse=reverse)

            console.print(f"Found {len(articles)} child articles (sorted by {sort_by}):")
            article_manager.display_articles_table(articles)

            # Provide helpful information about reordering
            console.print(
                "\n💡 [blue]Note:[/blue] This view shows articles sorted for reference only.",
                style="blue",
            )
            console.print(
                "⚠️ [yellow]YouTrack API does not support automatic article reordering.[/yellow]",
                style="yellow",
            )
            console.print(
                "The 'ordinal' field that controls article position is read-only.",
                style="dim",
            )
            console.print(
                "To actually reorder articles in YouTrack, use the web interface's drag-and-drop functionality.",
                style="dim",
            )
            console.print(
                "\n💬 [blue]Please upvote this feature request to help prioritize API support:[/blue]",
                style="blue",
            )
            console.print(
                "[link]https://youtrack.jetbrains.com/issue/JT-79905/Allow-sorting-Knowledge-Base-articles-alphabetically[/link]",
                style="link",
            )

            # Get base URL for direct link
            if ctx.obj:
                config = ctx.obj.get("config", {})
                if config and isinstance(config, dict):
                    base_url = config.get("base_url", "")
                    if base_url:
                        console.print(f"[dim]Direct link: {base_url.rstrip('/')}/articles/{parent_id}[/dim]")

        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to fetch child articles")

    except Exception as e:
        console.print(f"❌ Error fetching child articles: {e}", style="red")
        raise click.ClickException("Failed to fetch child articles") from e


@articles.command(name="tag")
@click.argument("article_id")
@click.argument("tags", nargs=-1)
@click.pass_context
def tag_article(ctx: click.Context, article_id: str, tags: tuple[str, ...]) -> None:
    """Add tags to an article. If no tags provided, shows interactive selection."""
    console = get_console()

    async def _tag_article() -> None:
        from ..articles import ArticleManager

        auth_manager = AuthManager()
        article_manager = ArticleManager(auth_manager)

        # If no tags provided, show interactive selection
        if not tags:
            console.print("🔍 Fetching available tags...", style="blue")

            # Get available tags
            tags_result = await article_manager.get_available_tags()
            if tags_result["status"] != "success":
                console.print(f"❌ {tags_result['message']}", style="red")
                return

            available_tags = tags_result["data"]
            if not available_tags:
                console.print("No tags available.", style="yellow")
                return

            # Show interactive selection
            console.print("\n📋 Available tags:", style="green")
            for i, tag in enumerate(available_tags, 1):
                console.print(f"  {i}. {tag.get('name', 'Unknown')} (ID: {tag.get('id', 'N/A')})")

            # Get user selection
            console.print("\n💡 Enter tag numbers separated by spaces (e.g., 1 3 5) or 'q' to quit:")
            try:
                user_input = input().strip()
                if user_input.lower() == "q":
                    console.print("Tagging cancelled.", style="yellow")
                    return

                # Parse selected indices
                selected_indices = [int(x) - 1 for x in user_input.split()]
                selected_tags = [available_tags[i] for i in selected_indices if 0 <= i < len(available_tags)]

                if not selected_tags:
                    console.print("No valid tags selected.", style="yellow")
                    return

                # Get tag IDs
                tag_ids = [tag.get("id") for tag in selected_tags if tag.get("id")]
                tag_names = [tag.get("name") for tag in selected_tags if tag.get("name")]

                console.print(f"\n🏷️  Selected tags: {', '.join(tag_names)}", style="green")

            except (ValueError, IndexError):
                console.print("❌ Invalid selection. Please enter valid numbers.", style="red")
                return
            except KeyboardInterrupt:
                console.print("\nTagging cancelled.", style="yellow")
                return

        else:
            # Tags provided via command line, treat as tag names
            console.print("🔍 Finding tags by name...", style="blue")

            # Get available tags to map names to IDs
            tags_result = await article_manager.get_available_tags()
            if tags_result["status"] != "success":
                console.print(f"❌ {tags_result['message']}", style="red")
                return

            available_tags = tags_result["data"]
            tag_map = {tag.get("name", "").lower(): tag.get("id") for tag in available_tags}

            # Find matching tags
            tag_ids = []
            tag_names = []
            not_found = []

            for tag_name in tags:
                tag_id = tag_map.get(tag_name.lower())
                if tag_id:
                    tag_ids.append(tag_id)
                    tag_names.append(tag_name)
                else:
                    not_found.append(tag_name)

            if not_found:
                console.print(f"⚠️  Tags not found: {', '.join(not_found)}", style="yellow")

            if not tag_ids:
                console.print("❌ No valid tags found.", style="red")
                return

            console.print(f"🏷️  Found tags: {', '.join(tag_names)}", style="green")

        # Add tags to article
        console.print(f"🔄 Adding tags to article {article_id}...", style="blue")
        result = await article_manager.add_tags_to_article(article_id, tag_ids)

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        elif result["status"] == "partial":
            console.print(f"⚠️  {result['message']}", style="yellow")
        else:
            console.print(f"❌ {result['message']}", style="red")

    try:
        asyncio.run(_tag_article())
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise click.ClickException("Failed to tag article") from e


@articles.group(name="comments")
def comments() -> None:
    """Manage article comments."""
    pass


@comments.command(name="add")
@click.argument("article_id")
@click.argument("text")
@click.pass_context
def add_comment(ctx: click.Context, article_id: str, text: str) -> None:
    """Add a comment to an article."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"💬 Adding comment to article '{article_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.add_comment(article_id, text))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to add comment")

    except Exception as e:
        console.print(f"❌ Error adding comment: {e}", style="red")
        raise click.ClickException("Failed to add comment") from e


@comments.command("list")
@click.argument("article_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_comments(
    ctx: click.Context,
    article_id: str,
    format: str,
) -> None:
    """List comments on an article."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"💬 Fetching comments for article '{article_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.get_article_comments(article_id))

        if result["status"] == "success":
            comments = result["data"]

            if format == "table":
                if not comments:
                    console.print("No comments found.", style="yellow")
                    return

                from rich.table import Table

                table = Table(title="Article Comments")
                table.add_column("ID", style="cyan")
                table.add_column("Author", style="green")
                table.add_column("Text", style="blue")
                table.add_column("Created", style="yellow")

                for comment in comments:
                    # Handle created date formatting
                    created_value = comment.get("created")
                    if isinstance(created_value, int):
                        from datetime import datetime

                        formatted_created = datetime.fromtimestamp(created_value / 1000).strftime("%Y-%m-%d %H:%M")
                    else:
                        formatted_created = str(created_value) if created_value else "N/A"

                    # Handle text formatting
                    text = comment.get("text", "")
                    if text and len(str(text)) > 100:
                        formatted_text = str(text)[:100] + "..."
                    else:
                        formatted_text = str(text) if text else "N/A"

                    table.add_row(
                        str(comment.get("id", "N/A")),
                        comment.get("author", {}).get("fullName", "N/A"),
                        formatted_text,
                        formatted_created,
                    )

                console.print(table)
            else:
                import json

                console.print(json.dumps(comments, indent=2))

        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list comments")

    except Exception as e:
        console.print(f"❌ Error listing comments: {e}", style="red")
        raise click.ClickException("Failed to list comments") from e


@comments.command(name="update")
@click.argument("comment_id")
@click.argument("text")
@click.pass_context
def update_comment(ctx: click.Context, comment_id: str, text: str) -> None:
    """Update an existing comment."""
    console = get_console()
    console.print("⚠️  Comment update functionality not yet implemented", style="yellow")
    console.print("This feature requires additional API endpoints", style="blue")


@comments.command(name="delete")
@click.argument("comment_id")
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_comment(ctx: click.Context, comment_id: str, force: bool) -> None:
    """Delete a comment."""
    console = get_console()

    if not force:
        if not click.confirm(f"Are you sure you want to delete comment '{comment_id}'?"):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print("⚠️  Comment delete functionality not yet implemented", style="yellow")
    console.print("This feature requires additional API endpoints", style="blue")


@articles.group(name="attach")
def attach() -> None:
    """Manage article attachments."""
    pass


@attach.command(name="upload")
@click.argument("article_id")
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def upload(ctx: click.Context, article_id: str, file_path: str) -> None:
    """Upload a file to an article."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"📎 Uploading file '{file_path}' to article '{article_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.upload_attachment(article_id, file_path))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to upload file")

    except Exception as e:
        console.print(f"❌ Error uploading file: {e}", style="red")
        raise click.ClickException("Failed to upload file") from e


@attach.command(name="download")
@click.argument("article_id")
@click.argument("attachment_id")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path",
)
@click.pass_context
def download(ctx: click.Context, article_id: str, attachment_id: str, output: Optional[str]) -> None:
    """Download an attachment from an article."""
    console = get_console()
    console.print("⚠️  File download functionality not yet implemented", style="yellow")
    console.print("This feature requires binary file handling", style="blue")


@attach.command("list")
@click.argument("article_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_attachments(
    ctx: click.Context,
    article_id: str,
    format: str,
) -> None:
    """List attachments for an article."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"📎 Fetching attachments for article '{article_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.get_article_attachments(article_id))

        if result["status"] == "success":
            attachments = result["data"]

            if format == "table":
                if not attachments:
                    console.print("No attachments found.", style="yellow")
                    return

                from rich.table import Table

                table = Table(title="Article Attachments")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Size", style="blue")
                table.add_column("Type", style="yellow")
                table.add_column("Author", style="magenta")

                for attachment in attachments:
                    table.add_row(
                        attachment.get("id", "N/A"),
                        attachment.get("name", "N/A"),
                        str(attachment.get("size", "N/A")),
                        attachment.get("mimeType", "N/A"),
                        attachment.get("author", {}).get("fullName", "N/A"),
                    )

                console.print(table)
            else:
                import json

                console.print(json.dumps(attachments, indent=2))

        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list attachments")

    except Exception as e:
        console.print(f"❌ Error listing attachments: {e}", style="red")
        raise click.ClickException("Failed to list attachments") from e


@attach.command(name="delete")
@click.argument("article_id")
@click.argument("attachment_id")
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_attachment(ctx: click.Context, article_id: str, attachment_id: str, force: bool) -> None:
    """Delete an attachment from an article."""
    console = get_console()

    if not force:
        if not click.confirm(f"Are you sure you want to delete attachment '{attachment_id}'?"):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print("⚠️  Attachment delete functionality not yet implemented", style="yellow")
    console.print("This feature requires additional API endpoints", style="blue")


def _sort_articles(
    articles: list[dict],
    sort_by: str,
    reverse: bool,
    case_sensitive: bool,
) -> list[dict]:
    """Sort articles based on the specified criteria."""

    def get_sort_key(article: dict):
        if sort_by == "title":
            title = article.get("summary", "")
            return title if case_sensitive else title.lower()
        if sort_by == "id":
            # Use internal ID for numeric sorting
            article_id = article.get("id", "")
            try:
                # Try to extract numeric part for proper numeric sorting
                import re

                numeric_match = re.search(r"\d+", str(article_id))
                return int(numeric_match.group()) if numeric_match else 0
            except (ValueError, AttributeError):
                return str(article_id)
        elif sort_by == "friendly-id":
            # Use readable ID
            return article.get("idReadable", article.get("id", ""))
        else:
            return ""

    return sorted(articles, key=get_sort_key, reverse=reverse)
