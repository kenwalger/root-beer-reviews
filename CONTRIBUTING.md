# Contributing to Root Beer Review App

Thank you for your interest in contributing to the Root Beer Review App! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Getting Started

1. **Fork the repository** (if applicable)
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/RootBeerReviewApp.git
   cd RootBeerReviewApp
   ```
3. **Set up your development environment**:
   - Install Python 3.12+
   - Install dependencies: `uv pip install -r requirements.txt` or `pip install -r requirements.txt`
   - Set up your `.env` file (see README.md)
   - Run the app: `uvicorn app.main:app --reload`

## Development Workflow

1. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clean, readable code
   - Follow PEP 8 style guidelines
   - Add type hints where appropriate
   - Write docstrings for functions and classes
   - Update documentation as needed

3. **Test your changes**:
   - Test locally before submitting
   - Ensure all existing functionality still works
   - Test edge cases

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```
   
   Use clear, descriptive commit messages:
   - Start with a verb (Add, Fix, Update, Remove)
   - Be specific about what changed
   - Reference issue numbers if applicable

5. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- **Python**: Follow PEP 8
- **Type Hints**: Use type hints for function parameters and return types
- **Docstrings**: Document functions, classes, and modules
- **Naming**: Use descriptive names, follow Python conventions
- **Line Length**: Keep lines under 100 characters when possible

## Project Structure

- `app/models/`: Pydantic models for data validation
- `app/routes/`: Route handlers (separated by auth, admin, public)
- `app/templates/`: Jinja2 templates
- `app/static/`: Static files (CSS, JS, images)

## Areas for Contribution

- **Bug Fixes**: Fix issues and improve stability
- **Features**: Add new functionality (see roadmap in README)
- **Documentation**: Improve docs, add examples
- **Testing**: Add unit tests, integration tests
- **UI/UX**: Improve design and user experience
- **Performance**: Optimize database queries, caching

## Pull Request Process

1. **Update documentation** if you've changed functionality
2. **Update CHANGELOG.md** with your changes
3. **Ensure your code follows the style guidelines**
4. **Test thoroughly** before submitting
5. **Write a clear description** of what your PR does and why

## Questions?

Feel free to open an issue for questions, suggestions, or discussions about the project.

Thank you for contributing! 🍺

