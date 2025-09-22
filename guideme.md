# MineFlow Deployment Guide

This guide will help you deploy the MineFlow mining operations management system to production using Render (backend) and Hostinger (frontend).

## Prerequisites

- GitHub repository with your code
- Render account (free tier available)
- Hostinger account with hosting plan
- Domain name (optional but recommended)

## Part 1: Backend Deployment on Render

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Verify these files exist in your repository**:
   - `Procfile` (for Render)
   - `requirements.txt` (with gunicorn)
   - `backend/settings.py` (updated with env variables)
   - `env.example` (environment variables template)

### Step 2: Deploy on Render

1. **Go to [Render.com](https://render.com)** and sign up/login

2. **Create a New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your MineFlow repository

3. **Configure the Service**:
   - **Name**: `mineflow-backend` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT`

4. **Set Environment Variables**:
   Click "Advanced" and add these environment variables:
   ```
   SECRET_KEY=your-super-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com,your-domain.com
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   DB_PORT=3306
   CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
   JWT_ACCESS_TOKEN_LIFETIME_DAYS=1
   JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)
   - Note your backend URL: `https://your-app-name.onrender.com`

### Step 3: Run Database Migrations

1. **Access Render Shell**:
   - Go to your service dashboard
   - Click "Shell" tab
   - Run these commands:
   ```bash
   python manage.py migrate
   python manage.py create_admin
   ```

2. **Verify Deployment**:
   - Visit `https://your-app-name.onrender.com/api/`
   - You should see Django REST Framework API root

## Part 2: Frontend Deployment on Hostinger

### Step 1: Prepare Frontend for Production

1. **Create production environment file**:
   ```bash
   cd frontend
   cp env.example .env.production
   ```

2. **Update `.env.production`**:
   ```env
   REACT_APP_API_URL=https://your-app-name.onrender.com/api
   REACT_APP_APP_NAME=MineFlow
   REACT_APP_VERSION=1.0.0
   ```

3. **Build the application**:
   ```bash
   npm run build
   ```

4. **Verify build folder**:
   - Check that `frontend/build/` folder was created
   - Ensure `.htaccess` file is in `frontend/build/`

### Step 2: Deploy to Hostinger

#### Option A: File Manager Upload

1. **Access Hostinger File Manager**:
   - Login to Hostinger control panel
   - Go to "File Manager"
   - Navigate to `public_html` folder

2. **Upload Files**:
   - Delete existing files in `public_html` (if any)
   - Upload all contents from `frontend/build/` folder
   - Ensure `.htaccess` file is uploaded

3. **Set Permissions**:
   - Right-click `.htaccess` → "Permissions" → Set to 644

#### Option B: FTP Upload

1. **Get FTP Credentials**:
   - Go to Hostinger control panel
   - Find FTP credentials in "Advanced" section

2. **Use FTP Client** (FileZilla, WinSCP, etc.):
   - Connect using FTP credentials
   - Navigate to `public_html` folder
   - Upload all contents from `frontend/build/`

### Step 3: Configure Domain (Optional)

1. **Point Domain to Hostinger**:
   - Update DNS records to point to Hostinger nameservers
   - Wait for DNS propagation (up to 24 hours)

2. **Update CORS Settings**:
   - Go back to Render dashboard
   - Update environment variable:
   ```
   CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
   ```

## Part 3: Post-Deployment Configuration

### Step 1: Update Frontend API URL

1. **If using custom domain**:
   - Update `.env.production` with your domain
   - Rebuild and redeploy frontend

2. **If using Hostinger subdomain**:
   - Update CORS settings in Render
   - Rebuild and redeploy frontend

### Step 2: Test the Application

1. **Test Backend**:
   - Visit `https://your-app-name.onrender.com/api/`
   - Test login: `https://your-app-name.onrender.com/api/auth/login/`

2. **Test Frontend**:
   - Visit your domain or Hostinger URL
   - Try logging in with admin credentials
   - Test all major features

### Step 3: Set Up SSL (Automatic)

- **Render**: SSL is automatically provided
- **Hostinger**: SSL is usually auto-configured, check in control panel

## Environment Variables Reference

### Backend (Render)

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-super-secret-key-here` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `your-app.onrender.com,your-domain.com` |
| `DB_ENGINE` | Database engine | `django.db.backends.mysql` |
| `DB_NAME` | Database name | `your_database_name` |
| `DB_USER` | Database user | `your_database_user` |
| `DB_PASSWORD` | Database password | `your_database_password` |
| `DB_HOST` | Database host | `your_database_host` |
| `DB_PORT` | Database port | `3306` |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins | `https://your-domain.com` |

### Frontend (Hostinger)

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `https://your-app.onrender.com/api` |
| `REACT_APP_APP_NAME` | Application name | `MineFlow` |
| `REACT_APP_VERSION` | Application version | `1.0.0` |

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Check `CORS_ALLOWED_ORIGINS` in Render
   - Ensure frontend URL is included

2. **Database Connection Issues**:
   - Verify database credentials in Render
   - Check if database allows external connections

3. **Build Failures**:
   - Check Node.js version compatibility
   - Ensure all dependencies are installed

4. **404 Errors on Frontend**:
   - Verify `.htaccess` file is uploaded
   - Check file permissions

5. **Static Files Not Loading**:
   - Run `python manage.py collectstatic` in Render shell
   - Check static files configuration

### Debug Commands

**In Render Shell**:
```bash
# Check Django configuration
python manage.py check

# Run migrations
python manage.py migrate

# Create superuser
python manage.py create_admin

# Collect static files
python manage.py collectstatic --noinput
```

**Local Frontend**:
```bash
# Install dependencies
npm install

# Build for production
npm run build

# Test production build locally
npx serve -s build
```

## Security Considerations

1. **Environment Variables**:
   - Never commit `.env` files to git
   - Use strong, unique secret keys
   - Rotate credentials regularly

2. **Database Security**:
   - Use strong database passwords
   - Limit database access by IP if possible
   - Regular backups

3. **HTTPS**:
   - Always use HTTPS in production
   - Update CORS settings for HTTPS only

## Monitoring and Maintenance

1. **Render Monitoring**:
   - Check Render dashboard for service status
   - Monitor logs for errors
   - Set up alerts for downtime

2. **Hostinger Monitoring**:
   - Check hosting control panel
   - Monitor disk space and bandwidth
   - Regular backups

3. **Application Monitoring**:
   - Monitor API response times
   - Check error logs
   - User feedback and bug reports

## Scaling Considerations

1. **Database**:
   - Consider database optimization
   - Implement caching (Redis)
   - Regular maintenance

2. **Backend**:
   - Monitor Render usage limits
   - Consider upgrading plan if needed
   - Implement CDN for static files

3. **Frontend**:
   - Optimize bundle size
   - Implement lazy loading
   - Use CDN for assets

## Support and Updates

1. **Regular Updates**:
   - Keep dependencies updated
   - Security patches
   - Feature updates

2. **Backup Strategy**:
   - Database backups
   - Code repository backups
   - Environment configuration backups

3. **Documentation**:
   - Keep deployment guide updated
   - Document any custom configurations
   - Maintain troubleshooting notes

---

## Quick Deployment Checklist

### Backend (Render)
- [ ] Repository pushed to GitHub
- [ ] Procfile created
- [ ] requirements.txt updated
- [ ] Environment variables set
- [ ] Service deployed
- [ ] Migrations run
- [ ] Admin user created
- [ ] API tested

### Frontend (Hostinger)
- [ ] Environment variables configured
- [ ] Application built
- [ ] .htaccess file created
- [ ] Files uploaded to Hostinger
- [ ] Domain configured (if applicable)
- [ ] CORS settings updated
- [ ] Application tested

### Post-Deployment
- [ ] SSL certificates active
- [ ] All features working
- [ ] Performance optimized
- [ ] Monitoring set up
- [ ] Documentation updated

---

**Need Help?** 
- Check the troubleshooting section above
- Review Render and Hostinger documentation
- Contact support if issues persist

**Last Updated**: September 22, 2025
**Version**: 1.0.0
