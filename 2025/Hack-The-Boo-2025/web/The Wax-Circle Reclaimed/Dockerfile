FROM node:18

# Install CouchDB, Nginx and dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    supervisor \
    nginx \
    && curl -fsSL https://couchdb.apache.org/repo/keys.asc | gpg --dearmor -o /usr/share/keyrings/couchdb-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/couchdb-archive-keyring.gpg] https://apache.jfrog.io/artifactory/couchdb-deb/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/couchdb.list \
    && apt-get update \
    && echo "couchdb couchdb/mode select standalone" | debconf-set-selections \
    && echo "couchdb couchdb/mode seen true" | debconf-set-selections \
    && echo "couchdb couchdb/bindaddress string 0.0.0.0" | debconf-set-selections \
    && echo "couchdb couchdb/bindaddress seen true" | debconf-set-selections \
    && echo "couchdb couchdb/cookie string elixir" | debconf-set-selections \
    && echo "couchdb couchdb/cookie seen true" | debconf-set-selections \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y couchdb \
    && rm -rf /var/lib/apt/lists/*

# Configure CouchDB directories and permissions
RUN mkdir -p /opt/couchdb/data /opt/couchdb/etc/local.d /opt/couchdb/var/log \
    && chown -R couchdb:couchdb /opt/couchdb \
    && chmod -R 0770 /opt/couchdb/data /opt/couchdb/etc /opt/couchdb/var

# Configure admin user in local.ini
RUN echo "[admins]" >> /opt/couchdb/etc/local.ini \
    && echo "admin = waxcircle2025" >> /opt/couchdb/etc/local.ini \
    && echo "" >> /opt/couchdb/etc/local.ini \
    && echo "[chttpd]" >> /opt/couchdb/etc/local.ini \
    && echo "bind_address = 0.0.0.0" >> /opt/couchdb/etc/local.ini \
    && chown couchdb:couchdb /opt/couchdb/etc/local.ini

# Create app directory
WORKDIR /app

# Copy package files first for better caching
COPY html/package*.json ./

# Install dependencies
RUN npm install --production

# Copy application files
COPY html/ ./

# Create supervisor configuration directory
RUN mkdir -p /etc/supervisor/conf.d

# Copy configuration files
COPY scripts/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY scripts/nginx.conf /etc/nginx/sites-available/default

# Copy flag
COPY flag.txt /flag.txt

# Set permissions
RUN chown -R couchdb:couchdb /app

# Expose ports
EXPOSE 80

# Start supervisord directly
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
