#!/bin/bash
# detect-devices.sh - Raspberry Pi Camera Device Detection Helper
# Helps identify which devices exist on your system for docker-compose.yml configuration

set -e

echo "🔍 motion-in-ocean - Camera Device Detection"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: Not running on Raspberry Pi hardware"
    echo "This script is designed for Raspberry Pi systems."
    echo ""
fi

# Check for required core devices
echo "📋 Core Devices (Required):"
echo ""

check_device() {
    local device=$1
    local description=$2
    if [ -e "$device" ]; then
        echo "  ✓ $device - $description"
        ls -l "$device" | awk '{print "    Permissions:", $1, "Owner:", $3":"$4}'
        return 0
    else
        echo "  ✗ $device - $description (NOT FOUND)"
        return 1
    fi
}

# Core devices
if [ -d "/dev/dma_heap" ]; then
    echo "  ✓ /dev/dma_heap - Memory management for libcamera (directory)"
    ls -l /dev/dma_heap/ 2>/dev/null | grep -E '^[c|l]' | awk '{print "    " $0}'
elif [ -e "/dev/dma_heap" ]; then
    check_device "/dev/dma_heap" "Memory management for libcamera"
else
    echo "  ✗ /dev/dma_heap - Memory management for libcamera (NOT FOUND)"
fi
check_device "/dev/vchiq" "VideoCore Host Interface"

echo ""
echo "� Media Controller Devices (Required for libcamera):"  
echo ""

media_devices=$(ls -1 /dev/media* 2>/dev/null || true)
if [ -z "$media_devices" ]; then
    echo "  ✗ No /dev/media* devices found"
    echo ""
    echo "  Troubleshooting:"
    echo "  1. Ensure camera is enabled: sudo raspi-config"
    echo "  2. Check if camera driver is loaded: lsmod | grep bcm2835"
    echo "  3. Reboot after enabling camera"
else
    for device in $media_devices; do
        echo "  ✓ $device"
        ls -l "$device" | awk '{print "    Permissions:", $1, "Owner:", $3":"$4}'
    done
fi

echo ""
echo "�📹 Video Devices (Camera Nodes):"
echo ""

video_devices=$(ls -1 /dev/video* 2>/dev/null || true)
if [ -z "$video_devices" ]; then
    echo "  ✗ No /dev/video* devices found"
    echo ""
    echo "  Troubleshooting:"
    echo "  1. Ensure camera is enabled: sudo raspi-config"
    echo "  2. Check camera connection and reboot"
    echo "  3. Test with: rpicam-hello --list-cameras"
else
    for device in $video_devices; do
        echo "  ✓ $device"
        ls -l "$device" | awk '{print "    Permissions:", $1, "Owner:", $3":"$4}'
    done
fi

echo ""
echo "🔧 Recommended docker-compose.yml Configuration:"
echo ""
echo "devices:"
echo "  - /dev/dma_heap:/dev/dma_heap"
echo "  - /dev/vchiq:/dev/vchiq"

if [ -n "$media_devices" ]; then
    for device in $media_devices; do
        echo "  - $device:$device"
    done
fi

if [ -n "$video_devices" ]; then
    for device in $video_devices; do
        echo "  - $device:$device"
    done
fi

echo ""
echo "📝 Alternative: Use device_cgroup_rules (automatically allows all matching devices):"
echo ""
echo "device_cgroup_rules:"
echo "  - 'c 253:* rmw'  # /dev/dma_heap/* (char device 253)"
echo "  - 'c 511:* rmw'  # /dev/vchiq"
echo "  - 'c 81:* rmw'   # /dev/video*"
echo "  - 'c 250:* rmw'  # /dev/media* (media controllers)"
echo ""

# Check camera functionality
echo "🎥 Camera Test:"
echo ""
if command -v rpicam-hello &> /dev/null; then
    echo "Testing camera with rpicam-hello..."
    if timeout 3 rpicam-hello --list-cameras 2>/dev/null; then
        echo "  ✓ Camera detected and working!"
    else
        echo "  ✗ Camera test failed - check camera connection"
    fi
else
    echo "  ⚠️  rpicam-hello not found (install with: sudo apt install libcamera-apps)"
fi

echo ""
echo "✅ Detection complete!"
echo ""
echo "Next steps:"
echo "1. Update docker-compose.yml with the devices shown above"
echo "2. Or use device_cgroup_rules for automatic device access"
echo "3. Run: docker compose up -d"
