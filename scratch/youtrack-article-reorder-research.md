# YouTrack Article Reordering Research Report

## Executive Summary

This research investigates various approaches to programmatically reorder YouTrack knowledge base articles through the REST API. The current CLI implementation includes a `reorder` command that provides a preview-only functionality, acknowledging that YouTrack's API doesn't support direct article reordering.

## Key Findings

### 1. Current API Limitations

**Ordinal Field Status:**
- Articles have an `ordinal` field that represents position in the tree hierarchy
- The `ordinal` field is documented as "Read-only" in the API documentation
- The field exists and can be retrieved: `articles?fields=id,summary,content,parentArticle(id),ordinal`
- Current CLI implementation recognizes this field but doesn't attempt to modify it

**Available Article Operations:**
- `GET /api/articles/{articleID}` - Read article
- `POST /api/articles/{articleID}` - Update article (content, summary, parentArticle)
- `DELETE /api/articles/{articleID}` - Delete article
- Child article operations: `/api/articles/{articleID}/childArticles/{articleID}`

### 2. Potential Workaround Approaches

#### A. Parent-Child Relationship Manipulation
**Method:** Modify article hierarchy to achieve desired ordering
**Implementation:**
- Change `parentArticle` relationships to restructure the tree
- Use DELETE operations to remove parent-child links
- Re-establish relationships in desired order

**Risks:**
- May disrupt existing article structure
- Could affect article visibility and permissions
- Users might lose track of original organization

#### B. Undocumented API Endpoint Investigation
**Method:** Inspect browser network requests during manual drag-and-drop operations
**Approach:**
1. Open YouTrack web interface
2. Navigate to knowledge base
3. Perform manual article reordering
4. Capture network requests in browser dev tools
5. Identify potential hidden endpoints

**Considerations:**
- JetBrains warns against using undocumented APIs
- Such endpoints may change without notice
- Could break with YouTrack updates

#### C. Batch Operations via Workflow Automation
**Method:** Use YouTrack's workflow system for bulk operations
**Capabilities:**
- Can process 100-300 articles per minute
- Supports `muteUpdateNotifications` to avoid spam
- Doesn't modify `updated` timestamps
- Can be scheduled automatically

**Limitations:**
- Workflows primarily designed for issues, not articles
- May not have access to ordinal field modification

### 3. Alternative Organization Strategies

#### A. Custom Field Approach
**Method:** Create custom fields to control ordering
**Implementation:**
1. Add custom number field "Display Order" to articles
2. Use this field for programmatic sorting
3. Implement CLI commands to modify this field
4. Sort articles by custom field value

**Benefits:**
- Fully controllable through API
- Maintains original YouTrack ordering intact
- Can implement complex sorting logic

#### B. Naming Convention Strategy
**Method:** Use systematic naming conventions for ordering
**Implementation:**
1. Prefix article titles with sortable identifiers (01-, 02-, etc.)
2. Sort articles alphabetically by title
3. Programmatically update titles to reorder

**Benefits:**
- Simple to implement
- Works with existing API
- Visual ordering in title

**Drawbacks:**
- Affects article titles
- May not be suitable for all content

#### C. Tag-Based Organization
**Method:** Use tags to indicate order or grouping
**Implementation:**
1. Create tags like "order-01", "order-02", etc.
2. Use tag management API to assign order tags
3. Filter and sort by tags

**Benefits:**
- Non-intrusive to article content
- Flexible categorization possible
- Full API support available

### 4. Recommended Implementation Strategy

Based on research findings, I recommend a multi-tiered approach:

#### Tier 1: Enhanced Preview with Manual Instructions
**Immediate Implementation:**
1. Improve existing `reorder` command with better output
2. Include current ordinal values in preview
3. Generate step-by-step manual reordering instructions
4. Provide direct web interface links

#### Tier 2: Custom Field Implementation
**Medium-term Solution:**
1. Add commands to create/manage "Display Order" custom field
2. Implement programmatic ordering using custom field
3. Provide migration tools to establish initial ordering
4. Create hybrid display showing both YouTrack and custom ordering

#### Tier 3: Network Request Investigation
**Advanced Research:**
1. Create tool to monitor network requests during manual reordering
2. Identify any hidden API endpoints
3. Implement experimental reordering (with warnings)
4. Document findings for community benefit

### 5. Specific Command Enhancements

#### Enhanced Reorder Command
```bash
# Current command (preview only)
yt articles reorder --sort-by title --project-id PRJ

# Proposed enhancements:
yt articles reorder --sort-by title --project-id PRJ \
  --export-script reorder.sh \
  --include-web-links \
  --show-ordinals
```

#### New Custom Field Commands
```bash
# Set up custom ordering field
yt articles setup-custom-order --project-id PRJ

# Apply custom ordering
yt articles apply-order --sort-by title --use-custom-field

# Sync custom field with current YouTrack order
yt articles sync-order --project-id PRJ
```

#### Network Investigation Tool
```bash
# Experimental feature with warnings
yt articles investigate-reorder --capture-requests --article-id ART-123
```

### 6. Implementation Priority

1. **High Priority:** Enhance existing preview functionality
2. **Medium Priority:** Custom field approach implementation
3. **Low Priority:** Network request investigation tool
4. **Research Priority:** Investigate bulk operations and workflow approaches

### 7. Alternative Solutions to Explore

#### A. YouTrack Plugin Development
- Create YouTrack plugin for enhanced article management
- Could potentially access internal APIs
- Requires Java/Kotlin development skills

#### B. Database Direct Access
- For self-hosted YouTrack instances
- Direct database manipulation (high risk)
- Requires database access and backup procedures

#### C. Export/Import Approach
- Export articles to external format
- Reorder externally
- Re-import in desired order
- Requires careful handling of IDs and relationships

### 8. Testing Strategy

For any implementation:

1. **Test Environment:** Use dedicated YouTrack instance
2. **Backup Strategy:** Export all articles before testing
3. **Progressive Testing:** Start with simple parent-child modifications
4. **User Acceptance:** Test manual workaround effectiveness
5. **Performance Testing:** Measure impact on large knowledge bases

### 9. Community Engagement

1. **Feature Request:** Submit enhancement request to JetBrains
2. **Community Forum:** Share findings and gather feedback
3. **Documentation:** Contribute to YouTrack API documentation
4. **Open Source:** Share tools and scripts with community

## Conclusion

While YouTrack's REST API doesn't currently support direct article reordering due to the read-only nature of the `ordinal` field, several workaround approaches exist. The most practical immediate solution is enhancing the preview functionality while implementing custom field-based ordering for programmatic control. Long-term solutions may emerge from community feedback and potential API enhancements by JetBrains.

The current CLI implementation correctly identifies this limitation and provides a useful preview. The recommended enhancement path balances practical utility with technical feasibility while maintaining user expectations about API limitations.
