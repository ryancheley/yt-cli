# YouTrack Article Reordering Implementation Plan

## Overview

Based on extensive research into YouTrack's REST API capabilities, this document outlines specific approaches to implement article reordering functionality, working within the constraints of the read-only `ordinal` field.

## Approach 1: Enhanced Preview with Manual Guidance (Immediate Implementation)

### Current State
- CLI has `yt articles reorder` command that shows preview only
- Displays proposed ordering but cannot apply changes
- Users must manually reorder in web interface

### Proposed Enhancements

#### 1. Network Request Monitoring Tool
```bash
yt articles capture-reorder-requests --article-id PARENT-123
```

**Implementation:**
- Launch embedded browser or WebDriver
- Navigate to YouTrack article page
- Monitor network traffic during manual reordering
- Extract actual API calls made by frontend
- Generate reproducible API call sequence

#### 2. Enhanced Manual Instructions
```bash
yt articles reorder --sort-by title --generate-guide
```

**Output:**
- Step-by-step reordering instructions
- Direct links to YouTrack pages
- Optimal drag-and-drop sequence
- Before/after screenshots (if possible)

#### 3. Browser Automation Script Generation
```bash
yt articles reorder --sort-by title --export-automation selenium-script.py
```

**Generated Script:**
- Selenium/Playwright automation script
- Logs into YouTrack
- Performs drag-and-drop operations
- Includes error handling and verification

## Approach 2: Parent-Child Relationship Manipulation (Medium Risk)

### Concept
Use the ability to modify `parentArticle` relationships to achieve reordering through restructuring.

### Implementation Strategy

#### 1. Temporary Restructuring
```python
# Pseudo-code for parent-child manipulation
async def reorder_via_restructuring(articles, desired_order):
    # Step 1: Remove all from parent (make them root-level)
    for article in articles:
        await update_article(article.id, parentArticle=None)

    # Step 2: Re-add in desired order
    for i, article in enumerate(desired_order):
        if i == 0:
            # First article stays as root
            continue
        else:
            # Make subsequent articles children of first
            await update_article(article.id, parentArticle=desired_order[0].id)

    # Step 3: Flatten back to original structure if needed
    await restore_original_hierarchy()
```

#### 2. Hierarchical Reordering
```bash
yt articles reorder-hierarchy --parent-id ROOT-123 --sort-by title --apply
```

**Process:**
1. Fetch all child articles of specified parent
2. Temporarily move all to different parent
3. Re-add articles to original parent in sorted order
4. Monitor ordinal field changes during process

### Risks and Mitigations
- **Risk:** Disrupts article hierarchy
- **Mitigation:** Create full backup before operation
- **Risk:** Changes permissions/visibility
- **Mitigation:** Verify permissions remain unchanged
- **Risk:** Breaks internal links
- **Mitigation:** Track and update article references

## Approach 3: Custom Field Ordering System (Recommended)

### Concept
Create a parallel ordering system using custom fields that can be programmatically controlled.

### Implementation Steps

#### 1. Setup Custom Ordering Field
```bash
yt articles setup-custom-order --project-id PRJ-123 --field-name "DisplayOrder"
```

**Process:**
- Create integer custom field "DisplayOrder"
- Apply to all articles in project
- Initialize with current ordinal values

#### 2. Programmatic Ordering
```bash
yt articles apply-custom-order --sort-by title --project-id PRJ-123
```

**Process:**
- Sort articles by specified criteria
- Update DisplayOrder field values (10, 20, 30, etc.)
- Provide gaps for future insertions

#### 3. Hybrid Display
```bash
yt articles list --order-by custom-field --project-id PRJ-123
yt articles list --order-by youtrack-native --project-id PRJ-123
```

**Features:**
- Show articles ordered by custom field
- Compare with YouTrack native ordering
- Highlight discrepancies

#### 4. Migration Tools
```bash
yt articles sync-custom-order --from youtrack --to custom-field
yt articles sync-custom-order --from custom-field --to manual-guide
```

### Custom Field API Implementation
```python
async def setup_custom_ordering_field(project_id: str) -> bool:
    """Create DisplayOrder custom field for project."""
    field_data = {
        "name": "DisplayOrder",
        "fieldType": {
            "$type": "SimpleProjectCustomField",
            "field": {
                "fieldType": {
                    "$type": "IntegerFieldType"
                }
            }
        }
    }

    # Add field to project
    response = await api_client.post(
        f"/api/admin/projects/{project_id}/customFields",
        json=field_data
    )
    return response.status_code == 200

async def update_article_order(article_id: str, order_value: int) -> bool:
    """Update article's DisplayOrder custom field."""
    update_data = {
        "customFields": [
            {
                "name": "DisplayOrder",
                "value": order_value
            }
        ]
    }

    response = await api_client.post(
        f"/api/articles/{article_id}",
        json=update_data
    )
    return response.status_code == 200
```

## Approach 4: Experimental Undocumented API Discovery

### Browser Network Monitoring
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

def capture_reorder_api_calls():
    """Capture network requests during manual article reordering."""

    # Setup browser with network logging
    options = webdriver.ChromeOptions()
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=0")

    driver = webdriver.Chrome(options=options)

    # Enable network logging
    driver.execute_cdp_cmd('Network.enable', {})
    requests = []

    def capture_request(request):
        if 'api/articles' in request['url']:
            requests.append(request)

    driver.add_cdp_listener('Network.requestWillBeSent', capture_request)

    # Navigate to YouTrack and perform manual reordering
    driver.get("https://youtrack.example.com/articles/PROJECT-123")

    # Wait for user to perform manual reordering
    input("Please reorder articles manually, then press Enter...")

    # Analyze captured requests
    for request in requests:
        if request['method'] in ['POST', 'PUT', 'PATCH']:
            print(f"Potential reorder API: {request['url']}")
            print(f"Method: {request['method']}")
            print(f"Headers: {request['headers']}")
            print(f"Body: {request.get('postData', 'No body')}")
            print("---")

    driver.quit()
    return requests
```

### API Call Analysis
```bash
yt articles investigate-api --monitor-session
```

**Features:**
- Launch instrumented browser session
- Monitor all API calls during manual operations
- Extract patterns from successful reorder operations
- Generate API call templates
- Test discovered endpoints safely

## Approach 5: Bulk Operations via Tags

### Tag-Based Ordering System
```bash
# Create order tags
yt articles create-order-tags --start 1 --end 100 --step 10

# Apply order tags based on sorting
yt articles apply-order-tags --sort-by title --parent-id ROOT-123

# Display articles by tag order
yt articles list --order-by tags --tag-pattern "order-*"
```

### Implementation
```python
async def create_order_tags(start: int, end: int, step: int):
    """Create numerical order tags."""
    for i in range(start, end + 1, step):
        tag_data = {"name": f"order-{i:03d}"}
        await api_client.post("/api/tags", json=tag_data)

async def apply_order_tags(articles: list, sort_criteria: str):
    """Apply order tags to articles based on sorting."""
    sorted_articles = sort_articles(articles, sort_criteria)

    for i, article in enumerate(sorted_articles):
        order_value = (i + 1) * 10  # 10, 20, 30, etc.
        tag_name = f"order-{order_value:03d}"

        # Remove existing order tags
        existing_tags = await get_article_tags(article.id)
        for tag in existing_tags:
            if tag['name'].startswith('order-'):
                await remove_tag_from_article(article.id, tag['id'])

        # Add new order tag
        await add_tag_to_article(article.id, tag_name)
```

## Implementation Priority and Timeline

### Phase 1 (Immediate - 1-2 weeks)
1. ✅ Enhanced preview functionality
2. ✅ Manual instruction generation
3. ✅ Web interface direct links
4. ✅ Current ordinal field display

### Phase 2 (Short-term - 2-4 weeks)
1. 🔄 Network request monitoring tool
2. 🔄 Browser automation script generation
3. 🔄 Custom field setup commands
4. 🔄 Basic custom field ordering

### Phase 3 (Medium-term - 1-2 months)
1. ⏳ Parent-child manipulation approach
2. ⏳ Tag-based ordering system
3. ⏳ Hybrid ordering displays
4. ⏳ Migration and sync tools

### Phase 4 (Long-term - 2-3 months)
1. ⏳ Undocumented API discovery
2. ⏳ Advanced automation scripts
3. ⏳ Plugin development investigation
4. ⏳ Community tool sharing

## Testing Strategy

### Test Environment Setup
```bash
# Create test project with sample articles
yt projects create TEST-REORDER --template documentation
yt articles create "Article A" --project-id TEST-REORDER --content "Test content A"
yt articles create "Article B" --project-id TEST-REORDER --content "Test content B"
yt articles create "Article C" --project-id TEST-REORDER --content "Test content C"
```

### Validation Scripts
```python
async def validate_reorder_approach(approach_name: str, test_articles: list):
    """Validate that reordering approach works correctly."""

    # Record initial state
    initial_state = await capture_article_state(test_articles)

    # Apply reordering
    success = await apply_reorder_approach(approach_name, test_articles)

    # Validate results
    final_state = await capture_article_state(test_articles)

    # Check ordering correctness
    ordering_correct = validate_order(final_state, expected_order)

    # Check data integrity
    data_intact = validate_data_integrity(initial_state, final_state)

    return {
        "approach": approach_name,
        "success": success,
        "ordering_correct": ordering_correct,
        "data_intact": data_intact,
        "side_effects": detect_side_effects(initial_state, final_state)
    }
```

## Risk Assessment and Mitigation

### High Risk Approaches
1. **Parent-child manipulation**
   - Risk: Data loss, broken hierarchy
   - Mitigation: Full backup, rollback procedures

2. **Undocumented API usage**
   - Risk: Breaking changes, instability
   - Mitigation: Version checking, fallback methods

### Low Risk Approaches
1. **Custom field ordering**
   - Risk: Additional field maintenance
   - Mitigation: Clear documentation, optional feature

2. **Enhanced preview**
   - Risk: User confusion about limitations
   - Mitigation: Clear messaging, education

## Conclusion

The most practical path forward involves:

1. **Immediate:** Enhance preview functionality with better guidance
2. **Short-term:** Implement custom field ordering system
3. **Medium-term:** Investigate network monitoring for API discovery
4. **Long-term:** Consider parent-child manipulation for specific use cases

This multi-pronged approach provides immediate value while building toward more comprehensive solutions, all while respecting YouTrack's API limitations and maintaining data integrity.
