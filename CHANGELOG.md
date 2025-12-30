# Changelog

All notable changes to the Root Beer Review App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-XX

### Added
- Initial release of Root Beer Review App
- Admin authentication system with session-based auth (JWT cookies)
- Root beer CRUD operations with objective attributes
- Review CRUD operations with structured sensory ratings
- Flavor note management system
- Metadata management (colors, serving contexts)
- Public homepage with filtering and sorting
- Root beer detail pages with reviews
- Individual review pages
- Chart.js radar charts for sensory dimension visualization
- Tailwind CSS with custom root beer theme
- MongoDB integration with audit trails
- Heroku deployment configuration
- Comprehensive documentation (README, CHANGELOG, LICENSE, CONTRIBUTING, SETUP)
- Secret key generation guide
- Environment variable configuration

### Features
- **Structured Data Model**: Separation of objective facts, structured sensory ratings, and subjective opinions
- **Three-Tier Carbonation Model**: Sensory carbonation bite (1-5), qualitative level (low/medium/high), optional CO₂ volumes
- **Flavor Note Taxonomy**: Predefined categories with admin-extensible list
- **Data Visualization**: Radar charts for sensory dimensions
- **Audit Trails**: Creation and update tracking with timestamps and user information
- **Form-based Admin Interface**: Full CRUD operations via web forms
- **Public Browsing**: Filter and sort root beers by brand, region, and score

### Technical
- FastAPI backend with async MongoDB operations
- Pydantic models for validation
- Jinja2 server-side rendering
- Responsive design with Tailwind CSS
- Chart.js for data visualization
- Environment-based configuration
- `uv` package management support
- Direct bcrypt password hashing (no passlib dependency)
- Form data handling with FastAPI Form dependencies

### Fixed
- Resolved bcrypt/passlib compatibility issues by switching to direct bcrypt usage
- Fixed pyproject.toml package configuration for uv builds
- Fixed form data handling in admin routes
- Added email-validator dependency for Pydantic EmailStr validation
- Fixed authentication dependency injection pattern

## [0.2.0] - 2024-12-XX

### Added
- **Progressive Web App (PWA) Support**: Full PWA implementation with manifest, service worker, and installability
  - App can be installed on mobile devices and desktop browsers
  - Offline functionality with service worker caching
  - Standalone app-like experience
  - PWA setup guide (PWA_SETUP.md)
- **Admin Navigation on Public Site**: Logged-in admins now see admin navigation links on public pages
  - Dashboard, Manage Root Beers, Manage Reviews, Account links visible when authenticated
  - Seamless navigation between public and admin interfaces
- **Default Data Seeding**: Automatic seeding of default data on startup
  - 20 default flavor notes from planning documents (Sassafras, Vanilla, Cinnamon, etc.)
  - 5 default colors (Amber, Brown, Dark Brown, Black, Mahogany)
  - 5 default serving contexts (Bottle, Can, Tap, Fountain, Growler)
  - Only seeds if collections are empty (idempotent)
- **Admin Account Management**: In-app password change functionality
  - New `/admin/account` page for changing admin password
  - Password validation and confirmation
  - No longer requires `.env` file changes after initial setup

### Improved
- **Cookie Persistence**: Enhanced cookie settings for better cross-route persistence
  - Improved cookie domain and path configuration
  - Better logout cookie deletion handling
- **Authentication Helper**: Added `get_admin_optional()` function for non-blocking admin checks
  - Allows public routes to check admin status without raising exceptions
  - Enables conditional admin UI rendering

### Fixed
- Fixed Internal Server Error on `/admin/account` route (missing template)
- Improved login persistence across navigation between public and admin pages
- **Security**: Service worker now excludes admin routes from caching to prevent sensitive data exposure offline
  - Admin routes always fetch from network, never cached
  - Only public pages and static assets are cached
  - Proper error handling for admin routes when offline
- **Heroku Build**: Removed `requirements.txt` to use `uv` exclusively for package management
  - Heroku now uses `uv.lock` and `pyproject.toml` for dependency resolution
  - Resolves build error about multiple package manager files

### Technical
- Service worker implementation for offline support and asset caching
- PWA manifest.json with app metadata, icons, and shortcuts
- Apple-specific meta tags for iOS home screen installation
- Service worker registration in both public and admin templates

## [Unreleased]

### Planned
- Public commenting system
- Multi-user authentication
- Advanced comparison tools
- Personal taste profiling
- Recommendation engine

