# Root Beer Review App

A structured, data-driven web application for reviewing root beers. This app distinguishes between objective chemical/physical attributes, structured sensory dimensions, and subjective opinion, enabling meaningful comparison and visualization.

## Features

- **Structured Reviews**: Capture objective facts, sensory ratings (1-5 scale), and subjective opinions (1-10 scale)
- **Flavor Notes**: Tag reviews with descriptive flavor notes (vanilla, sassafras, wintergreen, etc.)
- **Data Visualization**: Radar charts for sensory dimensions using Chart.js
- **Admin Interface**: Full CRUD operations for root beers, reviews, and metadata
- **Public Interface**: Browse and filter root beers with beautiful, themed UI
- **Audit Trails**: Track creation and updates with timestamps and user information
- **Progressive Web App (PWA)**: Installable on mobile and desktop with offline support
- **Admin Navigation**: Seamless admin access from public pages when logged in
- **Default Data Seeding**: Pre-populated flavor notes, colors, and serving contexts

## Tech Stack

- **Backend**: Python 3.12+, FastAPI
- **Database**: MongoDB (via MongoDB Atlas)
- **Frontend**: Server-rendered HTML with Jinja2 templates
- **Styling**: Tailwind CSS with custom root beer theme
- **Charts**: Chart.js for radar/spider charts
- **Authentication**: JWT-based session cookies, bcrypt password hashing
- **Package Management**: `uv` (with fallback to pip)
- **Deployment**: Heroku-ready
- **PWA**: Service worker, manifest, offline support

## Project Structure

```
RootBeerReviewApp/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── database.py          # MongoDB connection
│   ├── auth.py              # Authentication utilities
│   ├── models/              # Pydantic models
│   │   ├── rootbeer.py
│   │   ├── review.py
│   │   ├── flavor_note.py
│   │   ├── admin_user.py
│   │   └── metadata.py
│   ├── routes/              # Route handlers
│   │   ├── auth.py
│   │   ├── admin.py
│   │   └── public.py
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── admin/
│   │   └── public/
│   └── static/              # Static files
│       ├── css/
│       ├── icons/           # PWA icons
│       ├── manifest.json    # PWA manifest
│       └── service-worker.js # PWA service worker
├── planning/                # Planning documents
├── pyproject.toml          # Project configuration (uv)
├── requirements.txt        # Python dependencies
├── Procfile               # Heroku deployment
├── .python-version        # Python version
└── .env                   # Environment variables (not in git)
```

## Setup

### Prerequisites

- Python 3.12+
- MongoDB Atlas account (or local MongoDB)
- `uv` package manager (recommended) or `pip`

### Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Install dependencies using `uv`**:
   ```bash
   uv pip install -r requirements.txt
   ```
   
   Or using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   
   Create a `.env` file in the root directory:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/rootbeer_reviews?retryWrites=true&w=majority
   DATABASE_NAME=rootbeer_reviews
   SECRET_KEY=your-secret-key-here-change-in-production
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=change-this-password
   ENVIRONMENT=development
   ```

4. **Run the application**:
   
   With `uv` (recommended):
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   
   Or if using a traditional virtual environment:
   ```bash
   source venv/bin/activate  # Linux/Mac
   # or venv\Scripts\activate on Windows
   uvicorn app.main:app --reload
   ```

5. **Access the application**:
   - Public site: http://localhost:8000
   - Admin login: http://localhost:8000/admin/login

## Usage

### Admin Interface

1. Log in at `/admin/login` using the credentials from your `.env` file
2. Navigate to the admin dashboard to:
   - Add/edit root beers with objective attributes
   - Create reviews with structured sensory ratings
   - Manage flavor notes, colors, and serving contexts
   - Change your password at `/admin/account`
   - View all data with audit trails
3. **Admin Navigation**: When logged in, admin navigation links appear on public pages for easy access

### Public Interface

- Browse all reviewed root beers on the homepage
- Filter by brand, region, or sort by score
- View detailed root beer pages with all reviews
- See radar charts visualizing sensory dimensions
- Read individual reviews with full tasting notes
- **Install as PWA**: Add to home screen on mobile or install on desktop for app-like experience

## Data Model

### Root Beer (Objective Facts)
- Name, brand, region, country
- Ingredients, sweetener type
- Sugar content, caffeine, alcohol
- Color, carbonation level, estimated CO₂ volumes

### Review (Structured + Subjective)
- **Sensory Ratings (1-5)**: Sweetness, carbonation bite, creaminess, acidity, aftertaste length
- **Flavor Notes**: Multi-select tags (vanilla, sassafras, etc.)
- **Subjective**: Overall score (1-10), would drink again, uniqueness score
- **Metadata**: Review date, serving context

### Flavor Notes
- Predefined list that admins can extend
- Categories: Traditional, Sweet & Creamy, Spice & Herbal, Other
- **Default Seeding**: 20 default flavor notes are automatically seeded on first run

## Deployment to Heroku

1. **Create a Heroku app**:
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables**:
   ```bash
   heroku config:set MONGODB_URI=your-mongodb-uri
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set ADMIN_EMAIL=your-email
   heroku config:set ADMIN_PASSWORD=your-password
   heroku config:set ENVIRONMENT=production
   ```

3. **Deploy**:
   ```bash
   git push heroku main
   ```

4. **Open the app**:
   ```bash
   heroku open
   ```

## Development

### Running Locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Code Style

- Follow PEP 8
- Use type hints
- Document functions and classes
- Keep functions focused and small

## Progressive Web App (PWA)

The app is fully configured as a Progressive Web App:

- **Installable**: Add to home screen on iOS/Android or install on desktop browsers
- **Offline Support**: Cached pages work without internet connection
- **App-like Experience**: Opens in standalone mode without browser UI
- **Fast Loading**: Service worker caches static assets

See [PWA_SETUP.md](PWA_SETUP.md) for detailed setup instructions, including how to create app icons.

## Future Enhancements

- Public commenting system
- Multi-user support
- Advanced filtering and comparison tools
- Personal taste profiling
- Recommendation engine

## License

See [LICENSE](LICENSE) file for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

