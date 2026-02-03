# Contributing to FACTLY

Thank you for your interest in contributing to FACTLY! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Report security vulnerabilities responsibly

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/factly.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Follow the setup instructions in [README.md](README.md)

## Development Workflow

### Backend (Python/Django)

1. Navigate to backend: `cd backend`
2. Create virtual environment: `python -m venv venv`
3. Activate venv: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` from `.env.example` and configure API keys
6. Run migrations: `python manage.py migrate`
7. Start dev server: `python manage.py runserver`

### Frontend (React/Node)

1. Navigate to frontend: `cd frontend`
2. Install dependencies: `npm install`
3. Start dev server: `npm start`
4. Open http://localhost:3000

## Code Standards

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where possible
- Write docstrings for functions and classes
- Maximum line length: 100 characters

### JavaScript/React
- Use ESLint configuration (`npm run lint`)
- Use meaningful variable and function names
- Write JSDoc comments for complex components
- Maximum line length: 100 characters

### General
- Keep functions small and focused
- DRY principle (Don't Repeat Yourself)
- Write tests for new features
- Update documentation with changes

## Commit Messages

Use conventional commit format:

```
type(scope): description

Optional body with more details.

Fixes #issue-number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without changing functionality
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `security`: Security-related fixes

**Example:**
```
feat(url-extraction): add SSRF protection for private IP ranges

Blocks requests to localhost, private IPs (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
and reserved ranges. Validates hostnames against DNS resolution.

Fixes #42
```

## Testing

### Backend
```bash
cd backend
python -m pytest  # Run all tests
python -m pytest tests/test_url_extraction.py  # Specific test file
```

### Frontend
```bash
cd frontend
npm test
```

## Security

- Never commit API keys, secrets, or credentials
- Use `.env.example` for configuration templates
- Report security vulnerabilities to: [security contact info]
- Review security guidelines in [SECURITY.md](SECURITY.md) if it exists

## Pull Request Process

1. Update documentation and docstrings
2. Add/update tests for new functionality
3. Ensure all tests pass
4. Create a clear, descriptive PR title and description
5. Reference any related issues: "Fixes #123"
6. Wait for review and address feedback

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test the changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No security issues introduced
```

## Reporting Issues

### Bug Reports
Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots/logs if applicable
- System information (OS, Python/Node version, etc.)

### Feature Requests
Include:
- Use case and motivation
- Proposed solution (if any)
- Alternatives considered

## Questions?

- Open a GitHub Discussion
- Check existing issues and documentation
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to FACTLY!
