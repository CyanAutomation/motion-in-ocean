# ---- Builder Stage ----
FROM debian:bookworm AS builder

# Install dependencies needed for fetching RPi packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gnupg curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Add Raspberry Pi repository
RUN curl -Lfs https://archive.raspberrypi.org/debian/raspberrypi.gpg.key -o /tmp/raspberrypi.gpg.key && \
    gpg --dearmor -o /usr/share/keyrings/raspberrypi.gpg /tmp/raspberrypi.gpg.key && \
    echo "deb [signed-by=/usr/share/keyrings/raspberrypi.gpg] http://archive.raspberrypi.org/debian/ bookworm main" > /etc/apt/sources.list.d/raspi.list && \
    rm /tmp/raspberrypi.gpg.key

# Install python dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-picamera2 \
        python3-opencv \
        python3-flask && \
    rm -rf /var/lib/apt/lists/*

# ---- Final Stage ----
FROM debian:bookworm

# Copy Raspberry Pi repository and keys from builder
COPY --from=builder /usr/share/keyrings/raspberrypi.gpg /usr/share/keyrings/raspberrypi.gpg
COPY --from=builder /etc/apt/sources.list.d/raspi.list /etc/apt/sources.list.d/raspi.list

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-picamera2 \
        python3-opencv \
        python3-flask && \
    apt-get clean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the application code
COPY pi_camera_in_docker /app/pi_camera_in_docker

# Set the entry point
CMD ["python3", "/app/pi_camera_in_docker/main.py"]
