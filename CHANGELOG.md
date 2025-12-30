# Changelog

All notable changes to the Root Beer Review App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-XX

### Added
- Initial release of Root Beer Review App
- Admin authentication system with session-based auth
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
- Comprehensive documentation

### Features
- **Structured Data Model**: Separation of objective facts, structured sensory ratings, and subjective opinions
- **Three-Tier Carbonation Model**: Sensory carbonation bite (1-5), qualitative level (low/medium/high), optional CO₂ volumes
- **Flavor Note Taxonomy**: Predefined categories with admin-extensible list
- **Data Visualization**: Radar charts for sensory dimensions
- **Audit Trails**: Creation and update tracking with timestamps and user information

### Technical
- FastAPI backend with async MongoDB operations
- Pydantic models for validation
- Jinja2 server-side rendering
- Responsive design with Tailwind CSS
- Chart.js for data visualization
- Environment-based configuration
- `uv` package management support

## [Unreleased]

### Planned
- Public commenting system
- Multi-user authentication
- Advanced comparison tools
- Personal taste profiling
- Recommendation engine
- PWA support for mobile

