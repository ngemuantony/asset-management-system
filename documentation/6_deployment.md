# Deployment Guide

## System Requirements

- Python 3.12+
- Django 5.1.3
- PostgreSQL (Production)
- Redis (Optional, for caching)
- Nginx (Web Server)
- Gunicorn (WSGI Server)
- SSL Certificate

## Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-repo/sph-asset-management.git
   cd sph-asset-management
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create `.env` file:
   ```env
   DEBUG=False
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=your-domain.com
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

## Production Setup

1. **Gunicorn Configuration**
   Create `/etc/systemd/system/gunicorn.service`:
   ```ini
   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=your-user
   Group=www-data
   WorkingDirectory=/path/to/project
   ExecStart=/path/to/venv/bin/gunicorn config.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

2. **Nginx Configuration**
   Create `/etc/nginx/sites-available/your-site`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /path/to/project;
       }

       location /media/ {
           root /path/to/project;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/run/gunicorn.sock;
       }
   }
   ```

3. **SSL Configuration**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

4. **Start Services**
   ```bash
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   sudo systemctl restart nginx
   ```

## Security Checklist

1. **Django Settings**
   - Set DEBUG = False
   - Configure ALLOWED_HOSTS
   - Use strong SECRET_KEY
   - Enable CSRF protection
   - Configure secure cookies

2. **Database Security**
   - Use strong passwords
   - Restrict database access
   - Regular backups
   - Enable SSL for database connections

3. **File Permissions**
   - Secure media uploads
   - Restrict file access
   - Set proper ownership

4. **Monitoring Setup**
   - Configure logging
   - Setup error reporting
   - Monitor system resources
   - Setup alerts

## Maintenance

1. **Backup Strategy**
   ```bash
   # Database backup
   pg_dump dbname > backup.sql

   # Media files backup
   rsync -av /path/to/media/ /backup/location/
   ```

2. **Update Process**
   ```bash
   # Pull updates
   git pull origin main

   # Activate virtual environment
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Apply migrations
   python manage.py migrate

   # Collect static files
   python manage.py collectstatic

   # Restart services
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

3. **Monitoring**
   - Check error logs
   - Monitor disk space
   - Check system resources
   - Review security updates

## Troubleshooting

1. **Common Issues**
   - Permission errors
   - Static files not serving
   - Database connection issues
   - Email sending problems

2. **Debug Steps**
   - Check error logs
   - Verify configurations
   - Test database connection
   - Check file permissions

3. **Performance Issues**
   - Enable caching
   - Optimize database queries
   - Configure rate limiting
   - Monitor resource usage 