"""Articles command group for YouTrack CLI."""

import asyncio
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from ..auth import AuthManager


@click.group()
def articles() -> None:
    """Manage knowledge base articles."""
    pass


@articles.command(name="create")
@click.argument("title")
@click.option(
    "--content",
    "-c",
    help="Article content",
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, path_type=Path),
    help="Path to markdown file containing article content",
)
@click.option(
    "--project-id",
    "-p",
    help="Project ID to associate with the article",
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
    project_id: Optional[str],
    parent_id: Optional[str],
    summary: Optional[str],
    visibility: str,
) -> None:
    """Create a new article."""
    from ..articles import ArticleManager

    console = Console()

    # Validate that either content or file is provided, but not both
    if content and file:
        console.print("❌ Cannot specify both --content and --file options", style="red")
        raise click.ClickException("Use either --content or --file, not both")

    if not content and not file:
        console.print("❌ Either --content or --file must be specified", style="red")
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

    console = Console()
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

    console = Console()
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

    console = Console()
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
@click.pass_context
def tree(
    ctx: click.Context,
    project_id: Optional[str],
    fields: Optional[str],
    top: Optional[int],
) -> None:
    """Display articles in hierarchical tree structure."""
    from ..articles import ArticleManager

    console = Console()
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

    console = Console()
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

    console = Console()
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
    "--update",
    is_flag=True,
    help="Apply changes to YouTrack after confirmation",
)
@click.pass_context
def sort(
    ctx: click.Context,
    parent_id: str,
    update: bool,
) -> None:
    """Sort child articles under a parent article."""
    from ..articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"📋 Fetching child articles for '{parent_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.list_articles(parent_id=parent_id))

        if result["status"] == "success":
            articles = result["data"]

            if not articles:
                console.print("No child articles found.", style="yellow")
                return

            console.print(f"Found {len(articles)} child articles:")
            article_manager.display_articles_table(articles)

            if update:
                console.print(
                    "\n⚠️  Article sorting functionality requires manual reordering",
                    style="yellow",
                )
                console.print(
                    "Use the YouTrack web interface to drag and drop articles to reorder them.",
                    style="blue",
                )
            else:
                console.print(
                    "\n[dim]Use --update flag to apply sorting changes[/dim]",
                    style="blue",
                )

        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to fetch child articles")

    except Exception as e:
        console.print(f"❌ Error fetching child articles: {e}", style="red")
        raise click.ClickException("Failed to fetch child articles") from e


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

    console = Console()
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

    console = Console()
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
                    table.add_row(
                        comment.get("id", "N/A"),
                        comment.get("author", {}).get("fullName", "N/A"),
                        comment.get("text", "N/A")[:100] + ("..." if len(comment.get("text", "")) > 100 else ""),
                        comment.get("created", "N/A"),
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
    console = Console()
    console.print("⚠️  Comment update functionality not yet implemented", style="yellow")
    console.print("This feature requires additional API endpoints", style="blue")


@comments.command(name="delete")
@click.argument("comment_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_comment(ctx: click.Context, comment_id: str, confirm: bool) -> None:
    """Delete a comment."""
    console = Console()

    if not confirm:
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
    console = Console()
    console.print("⚠️  File upload functionality not yet implemented", style="yellow")
    console.print("This feature requires multipart form upload implementation", style="blue")


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
    console = Console()
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

    console = Console()
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
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_attachment(ctx: click.Context, article_id: str, attachment_id: str, confirm: bool) -> None:
    """Delete an attachment from an article."""
    console = Console()

    if not confirm:
        if not click.confirm(f"Are you sure you want to delete attachment '{attachment_id}'?"):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print("⚠️  Attachment delete functionality not yet implemented", style="yellow")
    console.print("This feature requires additional API endpoints", style="blue")
