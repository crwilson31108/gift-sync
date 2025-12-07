#!/bin/bash
# Install Playwright browsers for Railway deployment

echo "Installing Playwright browsers..."
python -m playwright install chromium
python -m playwright install-deps chromium

echo "Playwright browsers installed successfully"
