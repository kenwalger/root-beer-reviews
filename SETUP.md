# Setup Guide

This guide will help you get the Root Beer Review App up and running.

## Quick Start

1. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   # or
   pip install -r requirements.txt
   ```

2. **Create `.env` file**:
   
   First, generate a secure secret key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   Then create your `.env` file:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/rootbeer_reviews?retryWrites=true&w=majority
   DATABASE_NAME=rootbeer_reviews
   SECRET_KEY=<paste-generated-key-here>
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=change-this-password
   ENVIRONMENT=development
   ```
   
   See `SECRET_KEY_GENERATION.md` for more options.

3. **Run the app**:
   
   With `uv` (recommended):
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   
   Or if using a virtual environment:
   ```bash
   # Activate venv first (if using traditional venv)
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   uvicorn app.main:app --reload
   ```

4. **Access**:
   - Public: http://localhost:8000
   - Admin: http://localhost:8000/admin/login

## MongoDB Setup

### Option 1: MongoDB Atlas (Recommended for Production)

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Create a database user
4. Whitelist your IP address (or use 0.0.0.0/0 for development)
5. Get your connection string and add it to `.env` as `MONGODB_URI`

### Option 2: Local MongoDB

1. Install MongoDB locally
2. Start MongoDB service
3. Use connection string: `mongodb://localhost:27017/rootbeer_reviews`

## Initial Setup

On first run, the app will automatically:
- Create the admin user from environment variables (if it doesn't exist)
- Seed default data (flavor notes, colors, serving contexts) if collections are empty
- Set up database collections as needed

**Note:** Once the admin user is created in MongoDB, the `ADMIN_PASSWORD` in your `.env` file is only used for initial account creation. You can change your password later through the admin interface at `/admin/account`. The password stored in MongoDB takes precedence after the initial setup.

### Default Data

The app automatically seeds default data on startup (only if collections are empty):
- **20 Flavor Notes**: Sassafras, Vanilla, Cinnamon, and more from the planning documents
- **5 Colors**: Amber, Brown, Dark Brown, Black, Mahogany
- **5 Serving Contexts**: Bottle, Can, Tap, Fountain, Growler

You can add more options through the admin interface at `/admin/flavor-notes` and `/admin/metadata`.

## Default Collections

The app uses these MongoDB collections:
- `rootbeers` - Root beer product information
- `reviews` - Review data
- `flavor_notes` - Flavor note tags
- `admin_users` - Admin user accounts
- `colors` - Color options for root beers
- `serving_contexts` - Serving context options

## Troubleshooting

### Connection Issues
- Verify your MongoDB URI is correct
- Check network connectivity
- Ensure IP is whitelisted (for Atlas)

### Authentication Issues
- Verify `SECRET_KEY` is set
- Check admin email/password in `.env`
- Clear cookies and try logging in again

### Import Errors
- Ensure all dependencies are installed
- Check Python version (3.12+)
- Verify virtual environment is activated

## Next Steps

1. Log in to admin panel at `/admin/login`
2. **Default data is already seeded!** You'll find:
   - 20 flavor notes ready to use
   - 5 colors and 5 serving contexts
   - You can add more through the admin interface
3. Create your first root beer entry
4. Write your first review!

## Progressive Web App (PWA)

The app is configured as a PWA and can be installed on mobile devices and desktop browsers:

- **Mobile**: Open in Safari/Chrome → Share → "Add to Home Screen"
- **Desktop**: Look for install icon in Chrome/Edge address bar

See [PWA_SETUP.md](PWA_SETUP.md) for detailed instructions and icon setup.

