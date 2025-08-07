# 🚀 Deployment Guide for Ensemble Management Dashboard

Comprehensive guide for deploying the Ensemble Management Dashboard in institutional environments.

## 📋 Table of Contents

- [Overview](#overview)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Deployment Options](#deployment-options)
- [Security Configuration](#security-configuration)
- [Performance Optimization](#performance-optimization)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This guide provides step-by-step instructions for deploying the Ensemble Management Dashboard in production environments. The dashboard is designed to be scalable, secure, and maintainable for institutional use.

### Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │───▶│  Web Server     │───▶│  Application    │
│   (Optional)    │    │  (Nginx/Apache) │    │  (Streamlit)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  Data Storage   │
                                              │  (JSON/CSV)     │
                                              └─────────────────┘
```

## ✅ Pre-Deployment Checklist

### System Requirements

- [ ] **Python 3.8+** installed
- [ ] **Git** for version control
- [ ] **Virtual environment** setup
- [ ] **Dependencies** installed
- [ ] **Data files** prepared and validated
- [ ] **SSL certificates** (for HTTPS)
- [ ] **Domain name** configured (optional)

### Security Checklist

- [ ] **Environment variables** configured
- [ ] **Firewall rules** updated
- [ ] **Access controls** implemented
- [ ] **Data backup** strategy in place
- [ ] **Monitoring** tools configured
- [ ] **Logging** enabled

### Performance Checklist

- [ ] **Resource limits** defined
- [ ] **Caching** configured
- [ ] **CDN** setup (optional)
- [ ] **Database** optimization (if applicable)
- [ ] **Load testing** completed

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Recommended for Quick Start)

#### Prerequisites
- GitHub account
- Streamlit Cloud account
- Repository with dashboard code

#### Steps

1. **Prepare Repository**
   ```bash
   # Ensure all files are committed
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure Environment Variables**
   ```bash
   # In Streamlit Cloud dashboard
   STREAMLIT_SERVER_PORT=8501
   STREAMLIT_SERVER_ADDRESS=0.0.0.0
   ```

#### Advantages
- ✅ Zero server management
- ✅ Automatic HTTPS
- ✅ Built-in monitoring
- ✅ Easy scaling

#### Disadvantages
- ❌ Limited customization
- ❌ Vendor lock-in
- ❌ Data privacy concerns

### Option 2: Docker Deployment

#### Prerequisites
- Docker installed
- Docker Compose (optional)
- Server with Docker support

#### Dockerfile
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 streamlit
RUN chown -R streamlit:streamlit /app
USER streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  ensemble-dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ensemble-dashboard
    restart: unless-stopped
```

#### Deployment Commands
```bash
# Build and run with Docker
docker build -t ensemble-dashboard .
docker run -d -p 8501:8501 --name ensemble-dashboard ensemble-dashboard

# Or use Docker Compose
docker-compose up -d
```

### Option 3: Traditional Server Deployment

#### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- Nginx or Apache
- SSL certificates

#### Server Setup

1. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx
   ```

2. **Deploy Application**
   ```bash
   # Clone repository
   git clone <repository-url> /opt/ensemble-dashboard
   cd /opt/ensemble-dashboard

   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Create systemd service
   sudo nano /etc/systemd/system/ensemble-dashboard.service
   ```

3. **Systemd Service Configuration**
   ```ini
   [Unit]
   Description=Ensemble Management Dashboard
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/ensemble-dashboard
   Environment=PATH=/opt/ensemble-dashboard/venv/bin
   ExecStart=/opt/ensemble-dashboard/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

4. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name your-domain.com;

       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

5. **Start Services**
   ```bash
   # Enable and start services
   sudo systemctl enable ensemble-dashboard
   sudo systemctl start ensemble-dashboard
   sudo systemctl reload nginx

   # Setup SSL
   sudo certbot --nginx -d your-domain.com
   ```

### Option 4: Cloud Platform Deployment

#### AWS Deployment

1. **EC2 Instance Setup**
   ```bash
   # Launch EC2 instance
   # Install dependencies
   sudo yum update -y
   sudo yum install python3 python3-pip git -y

   # Deploy application
   git clone <repository-url>
   cd ensemble-dashboard
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Security Group Configuration**
   - Allow HTTP (80)
   - Allow HTTPS (443)
   - Allow SSH (22)

3. **Load Balancer Setup**
   - Create Application Load Balancer
   - Configure target groups
   - Setup SSL certificates

#### Google Cloud Platform

1. **App Engine Deployment**
   ```yaml
   # app.yaml
   runtime: python39
   entrypoint: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0

   env_variables:
     STREAMLIT_SERVER_PORT: "8080"
   ```

2. **Deploy Command**
   ```bash
   gcloud app deploy
   ```

## 🔒 Security Configuration

### Environment Variables

```bash
# Production environment variables
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
export STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true
```

### Authentication (Optional)

For additional security, implement authentication:

```python
# Add to app.py
import streamlit_authenticator as stauth

# Configure authentication
names = ['Admin User']
usernames = ['admin']
passwords = ['hashed_password']

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    'ensemble_dashboard', 'auth_key', cookie_expiry_days=30)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
elif authentication_status:
    # Main application code here
    pass
```

### Data Security

1. **File Permissions**
   ```bash
   # Secure data files
   chmod 600 data/*.json
   chown www-data:www-data data/
   ```

2. **Backup Strategy**
   ```bash
   # Automated backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   cp data/ensemble_data.json backups/ensemble_data_$DATE.json
   ```

## ⚡ Performance Optimization

### Caching Configuration

```python
# Add to app.py
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    # Data loading code
    pass

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def process_data(df):
    # Data processing code
    pass
```

### Resource Limits

```python
# Add to app.py
import psutil
import gc

# Monitor memory usage
def check_memory_usage():
    memory = psutil.virtual_memory()
    if memory.percent > 80:
        gc.collect()
        st.warning("High memory usage detected")

# Call periodically
if st.button("Check System Status"):
    check_memory_usage()
```

### Database Optimization (if applicable)

```python
# For large datasets, consider using a database
import sqlite3

def create_database():
    conn = sqlite3.connect('ensemble_data.db')
    df.to_sql('ensembles', conn, if_exists='replace', index=False)
    conn.close()
```

## 📊 Monitoring & Maintenance

### Health Checks

```python
# Add health check endpoint
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }
```

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ensemble_dashboard.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Monitoring Tools

1. **Application Monitoring**
   - New Relic
   - DataDog
   - Sentry

2. **Server Monitoring**
   - Prometheus + Grafana
   - Nagios
   - Zabbix

3. **Log Management**
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Splunk
   - Graylog

### Maintenance Schedule

#### Daily Tasks
- [ ] Check application logs
- [ ] Monitor system resources
- [ ] Verify data file integrity
- [ ] Review error reports

#### Weekly Tasks
- [ ] Update dependencies
- [ ] Backup data files
- [ ] Review performance metrics
- [ ] Update documentation

#### Monthly Tasks
- [ ] Security updates
- [ ] Performance optimization
- [ ] User feedback review
- [ ] Feature planning

## 🔧 Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check logs
journalctl -u ensemble-dashboard -f

# Check port availability
netstat -tulpn | grep 8501

# Restart service
sudo systemctl restart ensemble-dashboard
```

#### 2. High Memory Usage
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Restart application
sudo systemctl restart ensemble-dashboard
```

#### 3. Data Loading Issues
```bash
# Check file permissions
ls -la data/

# Validate JSON format
python3 -m json.tool data/ensemble_data.json

# Check file size
du -h data/ensemble_data.json
```

#### 4. Performance Issues
```bash
# Check CPU usage
top

# Check disk space
df -h

# Check network connectivity
ping google.com
```

### Debug Mode

```bash
# Run in debug mode
STREAMLIT_DEBUG=true streamlit run app.py

# Enable verbose logging
STREAMLIT_LOG_LEVEL=debug streamlit run app.py
```

### Support Resources

- **Documentation**: Check README.md and inline comments
- **Logs**: Review application and system logs
- **Community**: Streamlit community forums
- **GitHub Issues**: Report bugs and feature requests

## 📞 Support & Contact

For deployment support:
- **Email**: [your-email@institution.edu]
- **Phone**: [your-phone]
- **Department**: Music Department
- **Institution**: [Your Institution]

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Compatibility**: Python 3.8+, Streamlit 1.32.0+ 