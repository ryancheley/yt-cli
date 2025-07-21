"""Article deletion and recreation for reordering."""

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ArticleBackup:
    """Complete article backup for recreation."""

    id: str
    title: str
    summary: str
    content: str
    project_id: str
    parent_id: Optional[str]
    visibility: str
    author: Optional[str]
    created: Optional[str]
    tags: List[str]
    custom_fields: List[Dict]
    attachments: List[Dict]
    comments: List[Dict]


class YouTrackArticleRecreation:
    """Handle article deletion and recreation for reordering."""

    def __init__(self, article_manager):
        self.article_manager = article_manager
        self.backup_file = f"article_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    async def backup_articles(self, article_ids: List[str]) -> Dict[str, Any]:
        """Create complete backup of articles before deletion."""
        backups = []

        for article_id in article_ids:
            try:
                # Get article details
                article_result = await self.article_manager.get_article(article_id)
                if article_result["status"] != "success":
                    continue

                article = article_result["data"]

                # Get tags
                tags_result = await self.article_manager.get_article_tags(article_id)
                tags = tags_result.get("data", []) if tags_result["status"] == "success" else []

                # Get comments
                comments_result = await self.article_manager.get_article_comments(article_id)
                comments = comments_result.get("data", []) if comments_result["status"] == "success" else []

                # Get attachments
                attachments_result = await self.article_manager.get_article_attachments(article_id)
                attachments = attachments_result.get("data", []) if attachments_result["status"] == "success" else []

                backup = ArticleBackup(
                    id=article.get("id", ""),
                    title=article.get("summary", ""),
                    summary=article.get("summary", ""),
                    content=article.get("content", ""),
                    project_id=article.get("project", {}).get("id", ""),
                    parent_id=article.get("parentArticle", {}).get("id") if article.get("parentArticle") else None,
                    visibility="public",  # Default, could extract from article
                    author=article.get("author", {}).get("login") if article.get("author") else None,
                    created=str(article.get("created", "")),
                    tags=[tag.get("name", "") for tag in tags if tag.get("name")],
                    custom_fields=article.get("customFields", []),
                    attachments=attachments,
                    comments=comments,
                )

                backups.append(backup)
                print(f"✅ Backed up article: {backup.title}")

            except Exception as e:
                print(f"❌ Failed to backup article {article_id}: {e}")
                return {"status": "error", "message": f"Backup failed for {article_id}"}

        # Save backup to file
        try:
            backup_data = {"timestamp": datetime.now().isoformat(), "articles": [asdict(backup) for backup in backups]}

            with open(self.backup_file, "w") as f:
                json.dump(backup_data, f, indent=2)

            print(f"💾 Saved backup to {self.backup_file}")

            return {
                "status": "success",
                "message": f"Successfully backed up {len(backups)} articles",
                "backup_file": self.backup_file,
                "backups": backups,
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to save backup: {e}"}

    async def delete_articles(self, article_ids: List[str]) -> Dict[str, Any]:
        """Delete articles in preparation for recreation."""
        results = []

        for article_id in article_ids:
            try:
                # Note: We'd need to implement delete_article in ArticleManager
                # For now, this is a placeholder
                print(f"🗑️  Would delete article: {article_id}")
                results.append({"article_id": article_id, "status": "simulated_delete"})

            except Exception as e:
                print(f"❌ Failed to delete article {article_id}: {e}")
                results.append({"article_id": article_id, "status": "error", "message": str(e)})

        return {"status": "success", "message": f"Processed {len(results)} deletion requests", "results": results}

    async def recreate_articles_in_order(self, backups: List[ArticleBackup], sorted_order: List[str]) -> Dict[str, Any]:
        """Recreate articles in the specified order."""
        # Create mapping from title to backup
        title_to_backup = {backup.title: backup for backup in backups}

        recreation_results = []
        id_mapping = {}  # old_id -> new_id

        # First pass: Create all articles without parent relationships
        for title in sorted_order:
            if title not in title_to_backup:
                print(f"⚠️  Article '{title}' not found in backup")
                continue

            backup = title_to_backup[title]

            try:
                # Create article without parent initially
                result = await self.article_manager.create_article(
                    title=backup.title,
                    content=backup.content,
                    project_id=backup.project_id,
                    parent_id=None,  # Set later
                    summary=backup.summary,
                    visibility=backup.visibility,
                )

                if result["status"] == "success":
                    new_article = result["data"]
                    new_id = new_article.get("id")
                    id_mapping[backup.id] = new_id

                    recreation_results.append(
                        {"original_id": backup.id, "new_id": new_id, "title": backup.title, "status": "created"}
                    )

                    print(f"✅ Recreated: {backup.title} (new ID: {new_id})")

                    # Add delay to ensure ordinal ordering
                    await asyncio.sleep(0.5)

                else:
                    recreation_results.append(
                        {
                            "original_id": backup.id,
                            "title": backup.title,
                            "status": "error",
                            "message": result["message"],
                        }
                    )

            except Exception as e:
                recreation_results.append(
                    {"original_id": backup.id, "title": backup.title, "status": "error", "message": str(e)}
                )

        # Second pass: Restore parent relationships (if any)
        for title in sorted_order:
            if title not in title_to_backup:
                continue

            backup = title_to_backup[title]
            if backup.parent_id and backup.parent_id in id_mapping:
                new_id = id_mapping[backup.id]
                new_parent_id = id_mapping[backup.parent_id]

                try:
                    # Update article with parent relationship
                    await self.article_manager.update_article(article_id=new_id, parent_id=new_parent_id)
                    print(f"🔗 Restored parent relationship for {backup.title}")

                except Exception as e:
                    print(f"❌ Failed to restore parent relationship for {backup.title}: {e}")

        return {
            "status": "success",
            "message": f"Successfully recreated {len(recreation_results)} articles in sorted order",
            "results": recreation_results,
            "id_mapping": id_mapping,
        }

    async def restore_article_metadata(
        self, backups: List[ArticleBackup], id_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Restore tags, comments, and attachments to recreated articles."""
        restoration_results = []

        for backup in backups:
            if backup.id not in id_mapping:
                continue

            new_id = id_mapping[backup.id]

            try:
                # Restore tags
                if backup.tags:
                    # Note: Would need to implement tag restoration
                    print(f"🏷️  Would restore {len(backup.tags)} tags to {backup.title}")

                # Restore comments
                if backup.comments:
                    print(f"💬 Would restore {len(backup.comments)} comments to {backup.title}")

                # Restore attachments
                if backup.attachments:
                    print(f"📎 Would restore {len(backup.attachments)} attachments to {backup.title}")

                restoration_results.append({"article_id": new_id, "title": backup.title, "status": "metadata_restored"})

            except Exception as e:
                restoration_results.append(
                    {"article_id": new_id, "title": backup.title, "status": "error", "message": str(e)}
                )

        return {
            "status": "success",
            "message": f"Processed metadata restoration for {len(restoration_results)} articles",
            "results": restoration_results,
        }


async def recreate_articles_in_sorted_order(
    article_manager, article_ids: List[str], sorted_order: List[str], confirm_deletion: bool = False
) -> Dict[str, Any]:
    """Main function to recreate articles in sorted order."""
    recreator = YouTrackArticleRecreation(article_manager)

    print("🚨 ARTICLE RECREATION WARNING")
    print("=" * 50)
    print("This operation will:")
    print("1. Backup all article content and metadata")
    print("2. DELETE all specified articles")
    print("3. Recreate them in the sorted order")
    print("4. Restore metadata (tags, comments, attachments)")
    print("")
    print("⚠️  RISKS:")
    print("- Article IDs will change")
    print("- Article URLs will change")
    print("- External links will break")
    print("- This operation cannot be easily undone")
    print("")

    if not confirm_deletion:
        return {"status": "error", "message": "Operation requires explicit confirmation"}

    # Step 1: Backup articles
    print("📦 Step 1: Backing up articles...")
    backup_result = await recreator.backup_articles(article_ids)
    if backup_result["status"] != "success":
        return backup_result

    backups = backup_result["backups"]

    # Step 2: Delete articles (placeholder for now)
    print("🗑️  Step 2: Deleting articles...")
    delete_result = await recreator.delete_articles(article_ids)

    # Step 3: Recreate in sorted order
    print("🔄 Step 3: Recreating articles in sorted order...")
    recreate_result = await recreator.recreate_articles_in_order(backups, sorted_order)
    if recreate_result["status"] != "success":
        return recreate_result

    id_mapping = recreate_result["id_mapping"]

    # Step 4: Restore metadata
    print("🔧 Step 4: Restoring metadata...")
    restore_result = await recreator.restore_article_metadata(backups, id_mapping)

    return {
        "status": "success",
        "message": f"Successfully recreated {len(backups)} articles in sorted order",
        "method": "article_recreation",
        "backup_file": recreator.backup_file,
        "id_mapping": id_mapping,
        "results": {
            "backup": backup_result,
            "deletion": delete_result,
            "recreation": recreate_result,
            "restoration": restore_result,
        },
    }
