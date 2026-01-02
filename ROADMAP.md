# Roadmap

This document outlines planned improvements and enhancements for the Root Beer Review App.

## High Priority Features

### 1. Text Search Functionality
**Status**: Not Started  
**Complexity**: Medium  
**Estimated Effort**: 4-6 hours  
**Description**: Add full-text search across root beer names, brands, and tasting notes. Currently only dropdown filters (brand/region) are available.

**Implementation Notes**:
- Add search input field on homepage
- Implement MongoDB text search or use regex queries
- Search across root beer names, brands, and review tasting notes
- Display search results with highlighting

### 2. Pagination
**Status**: Not Started  
**Complexity**: Low-Medium  
**Estimated Effort**: 3-4 hours  
**Description**: Implement pagination for root beer lists and reviews. Currently loading all items at once (1000 limit).

**Implementation Notes**:
- Add pagination controls to homepage and admin lists
- Use MongoDB skip/limit for efficient querying
- Display page numbers and "next/previous" navigation
- Default to 20-50 items per page

### 3. Root Beer Comparison Tool
**Status**: Not Started  
**Complexity**: High  
**Estimated Effort**: 8-12 hours  
**Description**: Allow users to compare multiple root beers side-by-side with overlapping radar charts.

**Implementation Notes**:
- Add "Compare" button/checkbox on root beer pages
- Comparison page with side-by-side data
- Multi-dataset radar chart showing all selected root beers
- Compare up to 3-5 root beers at once

### 4. Image Uploads
**Status**: ✅ Completed  
**Complexity**: High  
**Estimated Effort**: 6-10 hours (S3) or 8-12 hours (Cloudinary)  
**Description**: Allow admins to upload photos of root beer bottles/cans.

**Implementation Notes**:
- ✅ **Storage**: Implemented AWS S3 integration
- ✅ Add image upload field to root beer creation/edit forms
- ✅ Store image URLs in MongoDB (not files themselves)
- ✅ Display images on root beer detail pages with gallery view
- ✅ Support multiple images per root beer with primary image selection
- ✅ File validation (type, size) on server
- ✅ Automatic S3 deletion when images are removed
- ⏳ **S3**: Image optimization with Pillow (future enhancement)
- ⏳ **S3**: Optional CloudFront CDN (future enhancement)
- See [S3_SETUP.md](S3_SETUP.md) for setup instructions

## Medium Priority Features

### 5. Advanced Filtering
**Status**: Not Started  
**Complexity**: Medium  
**Estimated Effort**: 5-7 hours  
**Description**: Enhanced filtering options beyond brand/region.

**Implementation Notes**:
- Filter by flavor notes (multi-select)
- Filter by score ranges (e.g., 8+ overall score)
- Filter by date ranges for reviews
- Filter by carbonation level, color, etc.
- Combine multiple filters

### 6. Admin Dashboard Enhancements
**Status**: Not Started  
**Complexity**: Medium-High  
**Estimated Effort**: 8-10 hours  
**Description**: Add charts, statistics, and analytics to the admin dashboard.

**Implementation Notes**:
- Charts showing review trends over time
- Statistics: most reviewed brands, average scores, etc.
- Flavor note frequency analysis
- Score distribution charts
- Activity timeline

### 7. Export Functionality
**Status**: Not Started  
**Complexity**: Low-Medium  
**Estimated Effort**: 4-6 hours  
**Description**: Allow admins to export data in various formats.

**Implementation Notes**:
- Export root beers and reviews to CSV
- Export to JSON for backup/restore
- Export filtered results
- Scheduled exports (future)

### 8. Duplicate Detection
**Status**: Not Started  
**Complexity**: Medium  
**Estimated Effort**: 4-6 hours  
**Description**: Warn admins when creating duplicate root beers.

**Implementation Notes**:
- Check for similar names/brands before creation
- Fuzzy matching algorithm
- Show potential duplicates with option to merge
- Prevent accidental duplicates

## Lower Priority Features

### 9. REST API Endpoints
**Status**: Not Started  
**Complexity**: Medium  
**Estimated Effort**: 6-8 hours  
**Description**: Provide JSON API for programmatic access to data.

**Implementation Notes**:
- FastAPI already supports this - add JSON response endpoints
- API authentication (API keys)
- Rate limiting
- API documentation (OpenAPI/Swagger)

### 10. Social Features
**Status**: Not Started  
**Complexity**: Low-Medium  
**Estimated Effort**: 3-5 hours  
**Description**: Add social sharing and feeds.

**Implementation Notes**:
- Social sharing buttons (Twitter, Facebook, etc.)
- RSS feed for new reviews
- XML sitemap for SEO
- Open Graph meta tags

### 11. Bulk Operations
**Status**: Not Started  
**Complexity**: Medium-High  
**Estimated Effort**: 6-10 hours  
**Description**: Allow admins to perform bulk actions.

**Implementation Notes**:
- Bulk edit root beers
- Bulk delete (with confirmation)
- Bulk import from CSV
- Bulk tag assignment

### 12. Enhanced Error Pages
**Status**: Not Started  
**Complexity**: Low  
**Estimated Effort**: 2-3 hours  
**Description**: Create custom, user-friendly error pages.

**Implementation Notes**:
- Custom 404 page
- Custom 500 error page
- Better error messages
- Helpful navigation from error pages

### 13. Review Editing Improvements
**Status**: Partial  
**Complexity**: Low-Medium  
**Estimated Effort**: 2-4 hours  
**Description**: Enhance the review editing experience in admin.

**Implementation Notes**:
- Verify full editing capabilities exist
- Improve form UX
- Add review history/changelog
- Better validation feedback

### 14. Statistics and Analytics
**Status**: Not Started  
**Complexity**: Medium-High  
**Estimated Effort**: 8-12 hours  
**Description**: Add comprehensive statistics and trend analysis.

**Implementation Notes**:
- Trend analysis over time
- "Most reviewed" lists
- Score distributions
- Flavor note frequency analysis
- Regional comparisons

### 15. Mobile UX Improvements
**Status**: Partial  
**Complexity**: Low-Medium  
**Estimated Effort**: 3-5 hours  
**Description**: Enhance mobile user experience.

**Implementation Notes**:
- ✅ Hamburger menu (implemented)
- Improve touch targets
- Better mobile forms
- Swipe gestures (future)
- Better mobile charts

## Completed Features

- ✅ Admin authentication with JWT cookies
- ✅ Root beer CRUD operations
- ✅ Review CRUD operations
- ✅ Flavor notes management
- ✅ Metadata management (colors, serving contexts)
- ✅ Public browsing with filtering and sorting
- ✅ Radar charts for sensory dimensions
- ✅ PWA support (manifest, service worker)
- ✅ Default data seeding
- ✅ Admin navigation on public site
- ✅ Account management (password change)
- ✅ Dynamic copyright year
- ✅ Responsive mobile navigation (hamburger menu)
- ✅ PWA install button
- ✅ S3 image uploads with multiple images per root beer
- ✅ Image gallery display in admin and public views
- ✅ Primary image selection
- ✅ Automatic S3 deletion when images are removed

## Future Considerations

- Multi-user authentication (beyond single admin)
- Public commenting system
- Personal taste profiling
- Recommendation engine
- Advanced comparison tools
- Integration with external APIs (nutrition data, etc.)

---

**Note**: This roadmap is subject to change based on user feedback and priorities. Features are listed in approximate priority order, but actual implementation order may vary.

