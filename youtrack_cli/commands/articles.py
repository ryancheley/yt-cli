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
    help="Maximum number of articles to return",
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
@click.pass_context
def list_articles(
    ctx: click.Context,
    project_id: Optional[str],
    parent_id: Optional[str],
    fields: Optional[str],
    top: Optional[int],
    query: Optional[str],
    format: str,
) -> None:
    """List articles with filtering."""
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print("📚 Fetching articles...", style="blue")

    try:
        result = asyncio.run(
            article_manager.list_articles(
                project_id=project_id,
                parent_id=parent_id,
                fields=fields,
                top=top,
                query=query,
            )
        )

        if result["status"] == "success":
            articles = result["data"]

            if format == "table":
                article_manager.display_articles_table(articles)
                console.print(f"\n[dim]Total: {result['count']} articles[/dim]")
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
                query="visibility:private",
            )
        )

        if result["status"] == "success":
            articles = result["data"]

            if format == "table":
                article_manager.display_articles_table(articles)
                console.print(f"\n[dim]Total drafts: {result['count']} articles[/dim]")
            else:
                import json

                console.print(json.dumps(articles, indent=2))
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
                "To actually reorder articles in YouTrack, use the web interface's drag-and-drop functionality.",
                style="dim",
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


@articles.command()
@click.argument("article_ids", nargs=-1)
@click.option(
    "--sort-by",
    type=click.Choice(["title", "id", "friendly-id"], case_sensitive=False),
    required=True,
    help="Sort articles by title, ID, or friendly ID",
)
@click.option(
    "--reverse",
    is_flag=True,
    help="Reverse the sort order",
)
@click.option(
    "--project-id",
    "-p",
    help="Limit reordering to articles within a specific project",
)
@click.option(
    "--parent-id",
    help="Reorder only child articles of a specific parent",
)
@click.option(
    "--recursive",
    is_flag=True,
    help="Apply reordering to entire article hierarchy",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=True,
    help="Preview changes without execution (default behavior)",
)
@click.option(
    "--live",
    is_flag=True,
    help="Actually perform the reordering (overrides --dry-run)",
)
@click.option(
    "--method",
    type=click.Choice(["custom-field", "parent-manipulation"], case_sensitive=False),
    default="custom-field",
    help="Method to use for reordering (custom-field is safer, parent-manipulation is experimental)",
)
@click.option(
    "--custom-field-name",
    default="DisplayOrder",
    help="Name of custom field to use for ordering (only with custom-field method)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompts",
)
@click.option(
    "--case-sensitive",
    is_flag=True,
    help="Use case-sensitive title sorting",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def reorder(
    ctx: click.Context,
    article_ids: tuple[str, ...],
    sort_by: str,
    reverse: bool,
    project_id: Optional[str],
    parent_id: Optional[str],
    recursive: bool,
    dry_run: bool,
    live: bool,
    method: str,
    custom_field_name: str,
    force: bool,
    case_sensitive: bool,
    format: str,
) -> None:
    """Reorder articles based on specified sorting criteria.

    By default, this command provides a preview of how articles would be ordered.
    Use --live flag to actually perform the reordering using available methods.

    Examples:
        # Preview sorting all articles in project by title
        yt articles reorder --project-id PRJ-123 --sort-by title

        # ACTUALLY reorder specific articles by ID using custom field method
        yt articles reorder ART-1 ART-5 ART-3 --sort-by id --live --method custom-field

        # ACTUALLY reorder with experimental parent manipulation method
        yt articles reorder --parent-id ART-ROOT --sort-by title --live --method parent-manipulation

        # Use custom field name for ordering
        yt articles reorder --project-id PRJ-123 --sort-by title --live --custom-field-name "SortOrder"

        # JSON output for automation
        yt articles reorder --sort-by title --format json --project-id PRJ-123
    """
    from ..articles import ArticleManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    # Determine if we're doing live reordering
    is_live = live and not dry_run

    if is_live:
        console.print("🚀 [bold green]LIVE REORDERING MODE[/bold green]", style="bold green")
        console.print(f"Method: {method}", style="blue")
        if method == "custom-field":
            console.print(f"Custom field: {custom_field_name}", style="blue")
        elif method == "parent-manipulation":
            console.print(
                "⚠️  [yellow]WARNING: Experimental method that may disrupt article hierarchy[/yellow]", style="yellow"
            )

        if not force:
            console.print("\n🔥 [bold red]This will ACTUALLY modify your YouTrack articles![/bold red]")
            if not click.confirm("Are you sure you want to proceed with live reordering?"):
                console.print("Reordering cancelled.", style="yellow")
                return
    else:
        # Show API limitation warning for preview mode
        console.print("📋 [blue]PREVIEW MODE[/blue] - No changes will be made", style="blue")
        if not live:
            console.print("💡 Use --live flag to actually perform reordering", style="dim")

    console.print(
        f"\n🔄 {'Executing' if is_live else 'Analyzing'} article ordering (sort by: {sort_by})...", style="blue"
    )

    try:
        result = asyncio.run(
            _reorder_articles(
                article_manager=article_manager,
                article_ids=article_ids,
                sort_by=sort_by,
                reverse=reverse,
                project_id=project_id,
                parent_id=parent_id,
                recursive=recursive,
                dry_run=dry_run,
                is_live=is_live,
                method=method,
                custom_field_name=custom_field_name,
                force=force,
                case_sensitive=case_sensitive,
                format=format,
                console=console,
            )
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to analyze article ordering")

    except Exception as e:
        console.print(f"❌ Error analyzing article ordering: {e}", style="red")
        raise click.ClickException("Failed to analyze article ordering") from e


async def _reorder_articles(
    article_manager,
    article_ids: tuple[str, ...],
    sort_by: str,
    reverse: bool,
    project_id: Optional[str],
    parent_id: Optional[str],
    recursive: bool,
    dry_run: bool,
    is_live: bool,
    method: str,
    custom_field_name: str,
    force: bool,
    case_sensitive: bool,
    format: str,
    console,
) -> dict[str, str]:
    """Handle the article reordering logic."""
    # Fetch articles based on parameters
    articles_to_sort = []

    if article_ids:
        # Get specific articles
        for article_id in article_ids:
            result = await article_manager.get_article(article_id)
            if result["status"] == "success":
                articles_to_sort.append(result["data"])
            else:
                console.print(f"⚠️  Could not fetch article {article_id}: {result['message']}", style="yellow")
    else:
        # Get articles from project or parent
        result = await article_manager.list_articles(
            project_id=project_id,
            parent_id=parent_id,
        )

        if result["status"] == "success":
            articles_to_sort = result["data"]
        else:
            return {"status": "error", "message": f"Failed to fetch articles: {result['message']}"}

    if not articles_to_sort:
        return {"status": "error", "message": "No articles found to reorder"}

    # Store original order for comparison
    original_articles = articles_to_sort.copy()

    # Sort articles based on criteria
    sorted_articles = _sort_articles(articles_to_sort, sort_by, reverse, case_sensitive)

    if is_live:
        # Perform actual reordering
        console.print(f"\n🔥 Executing live reordering using {method} method...", style="bold red")

        if method == "custom-field":
            reorder_result = await article_manager.reorder_articles_via_custom_field(sorted_articles, custom_field_name)
        elif method == "parent-manipulation":
            reorder_result = await article_manager.reorder_articles_via_parent_manipulation(sorted_articles)
        else:
            return {"status": "error", "message": f"Unknown reordering method: {method}"}

        # Display reordering results
        if format == "json":
            import json

            console.print(json.dumps(reorder_result, indent=2))
        else:
            _display_live_reorder_results(console, reorder_result, sorted_articles)

        return reorder_result
    else:
        # Display preview results
        _display_reorder_results(
            console=console,
            original_articles=original_articles,
            sorted_articles=sorted_articles,
            sort_by=sort_by,
            reverse=reverse,
            format=format,
        )

        # Show helpful next steps
        _show_reorder_instructions(console, project_id, parent_id)

        return {"status": "success", "message": f"Article ordering preview completed (sorted by {sort_by})"}


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
        elif sort_by == "id":
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


def _display_reorder_results(
    console,
    original_articles: list[dict],
    sorted_articles: list[dict],
    sort_by: str,
    reverse: bool,
    format: str,
) -> None:
    """Display the reordering results."""
    # Show summary
    order_text = "descending" if reverse else "ascending"
    console.print(f"\n📊 Reordering Preview: {len(sorted_articles)} articles sorted by {sort_by} ({order_text})")

    if format == "json":
        import json

        output_data = {
            "sort_criteria": {
                "sort_by": sort_by,
                "reverse": reverse,
            },
            "original_order": [
                {
                    "id": art.get("id"),
                    "idReadable": art.get("idReadable"),
                    "title": art.get("summary"),
                    "ordinal": art.get("ordinal"),
                }
                for art in original_articles
            ],
            "new_order": [
                {
                    "id": art.get("id"),
                    "idReadable": art.get("idReadable"),
                    "title": art.get("summary"),
                    "ordinal": art.get("ordinal"),
                }
                for art in sorted_articles
            ],
        }
        console.print(json.dumps(output_data, indent=2))
    else:
        # Show table format
        from rich.table import Table

        table = Table(title="Proposed Article Order")
        table.add_column("Position", style="cyan", justify="right")
        table.add_column("ID", style="blue")
        table.add_column("Title", style="green")
        table.add_column("Current Ordinal", style="yellow")
        table.add_column("Change", style="magenta")

        # Create position mapping for original order
        original_positions = {art.get("id"): idx for idx, art in enumerate(original_articles)}

        for new_pos, article in enumerate(sorted_articles, 1):
            article_id = article.get("id")
            original_pos = original_positions.get(article_id, -1) + 1

            # Determine change indicator
            if original_pos == new_pos:
                change_indicator = "="
            elif original_pos < new_pos:
                change_indicator = f"↓ ({original_pos}→{new_pos})"
            else:
                change_indicator = f"↑ ({original_pos}→{new_pos})"

            table.add_row(
                str(new_pos),
                article.get("idReadable", article.get("id", "N/A")),
                article.get("summary", "Untitled")[:50],
                str(article.get("ordinal", "N/A")),
                change_indicator,
            )

        console.print(table)


def _display_live_reorder_results(console, reorder_result: dict, sorted_articles: list[dict]) -> None:
    """Display the results of live reordering."""
    from rich.table import Table

    status = reorder_result.get("status", "unknown")
    method = reorder_result.get("method", "unknown")
    message = reorder_result.get("message", "No message")
    data = reorder_result.get("data", [])

    # Show overall status
    if status == "success":
        console.print(f"\n✅ [bold green]{message}[/bold green]")
    elif status == "partial":
        console.print(f"\n⚠️  [bold yellow]{message}[/bold yellow]")
    else:
        console.print(f"\n❌ [bold red]{message}[/bold red]")

    if method == "custom-field":
        field_name = reorder_result.get("field_name", "DisplayOrder")
        console.print(f"Custom field used: [blue]{field_name}[/blue]")
    elif method == "parent-manipulation":
        warning = reorder_result.get("warning", "")
        if warning:
            console.print(f"⚠️  [yellow]{warning}[/yellow]")

    # Show detailed results table
    if data and isinstance(data, list):
        table = Table(title="Reordering Results")
        table.add_column("Article ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Status", style="blue")

        if method == "custom-field":
            table.add_column("New Order Value", style="yellow")
            table.add_column("Position", style="magenta")
        elif method == "parent-manipulation":
            table.add_column("New Position", style="yellow")

        for item in data:
            status_text = item.get("status", "unknown")
            status_color = "green" if status_text == "success" else "red" if status_text == "error" else "yellow"

            row_data = [
                item.get("article_id", "N/A"),
                (item.get("article_title", "Unknown"))[:40],
                f"[{status_color}]{status_text}[/{status_color}]",
            ]

            if method == "custom-field":
                row_data.extend([str(item.get("new_order", "N/A")), str(item.get("position", "N/A"))])
            elif method == "parent-manipulation":
                row_data.append(str(item.get("new_position", "N/A")))

            table.add_row(*row_data)

        console.print(table)

    # Show next steps
    console.print("\n💡 [blue]Next Steps:[/blue]")
    if method == "custom-field":
        field_name = reorder_result.get("field_name", "DisplayOrder")
        console.print(f"• Articles now have {field_name} custom field values for ordering")
        console.print("• You can sort by this field in YouTrack's web interface")
        console.print(f"• Use this field in queries: 'order by: {field_name}'")
    elif method == "parent-manipulation":
        console.print("• Articles have been reordered using parent-child manipulation")
        console.print("• Check YouTrack web interface to verify the new order")
        console.print("• Native YouTrack ordinal values should now reflect the new order")

    if status == "partial":
        console.print("⚠️  [yellow]Some articles failed to reorder - check the table above for details[/yellow]")


def _show_reorder_instructions(
    console,
    project_id: Optional[str],
    parent_id: Optional[str],
) -> None:
    """Show instructions for actual reordering."""
    console.print("\n💡 [blue]To Apply This Ordering:[/blue]")
    console.print("1. Open YouTrack in your web browser")
    console.print("2. Navigate to the Knowledge Base section")

    if project_id:
        console.print(f"3. Find project '{project_id}' articles")
    elif parent_id:
        console.print(f"3. Find parent article '{parent_id}' and its children")
    else:
        console.print("3. Find the relevant articles")

    console.print("4. Use drag-and-drop to reorder articles manually")
    console.print("5. The ordinal field will be updated automatically")

    console.print("\n🔗 [dim]Alternative: Consider using custom fields or tags for programmatic ordering[/dim]")
