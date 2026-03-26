# Use Ubuntu as base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    OPENCLAW_HOME=/opt/openclaw \
    DATA_DIR=/data

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (if OpenClaw uses Node)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

// Create directories
RUN mkdir -p ${OPENCLAW_HOME} ${DATA_DIR}

# Copy app files
COPY package.json ${OPENCLAW_HOME}/
COPY server.js ${OPENCLAW_HOME}/

# Copy data directory (configs, logs, etc.)
COPY . ${DATA_DIR}/

# Install Node dependencies for the gateway app
RUN cd ${OPENCLAW_HOME} \
    && npm install --omit=dev

# Set working directory for the app
WORKDIR ${OPENCLAW_HOME}

# Expose ports
# 8080 - Main OpenClaw service
# 11434 - Ollama (if running locally)
EXPOSE 8080 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start lightweight gateway server (serves dashboard and health)
CMD ["node", "server.js"]
