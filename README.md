# SPH Asset Management System

## Overview

SPH Asset Management System is a comprehensive solution for managing organizational assets, handling requests, and generating reports.

## Documentation

Complete documentation can be found in the [documentation folder](documentation/README.md).

Key sections:
- [System Overview](documentation/1_system_overview.md)
- [API Reference](documentation/8_api_reference.md)
- [Development Guide](documentation/7_development.md)
- [Deployment Guide](documentation/6_deployment.md)

## Quick Start

1. Clone the repository
```bash
git clone https://github.com/your-repo/sph-asset-management.git
cd sph-asset-management
```

2. Install dependencies
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. Setup database
```bash
python manage.py migrate
python manage.py createsuperuser
```

4. Run development server
```bash
python manage.py runserver
```

## Features

- User Management with Role-Based Access Control
- Asset Lifecycle Management
- Request Processing Workflow
- Reporting and Analytics
- API-First Architecture

## Contributing

Please read our [Contributing Guide](documentation/7_development.md#development-workflow) before submitting any changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.