# Makefile for Plat de la Semaine (PDLS)

PROJECT_DIR      := $(CURDIR)
VENV_MAC         ?= $(HOME)/PDLS
VENV_LOCAL       ?= $(PROJECT_DIR)/venv
WINE_PYINSTALLER ?= $(HOME)/.wine/drive_c/Program\ Files\ \(x86\)/Python38/Scripts/pyinstaller.exe
CREATE_DMG       ?= create-dmg

SHELL := /bin/bash

.PHONY: all build build-macos build-windows images env clean

all: build

build: build-macos build-windows

build-macos: images env
	@echo "Building macOS application..."
	source $(VENV_MAC)/bin/activate && pyinstaller --clean PDLS\ Mac.spec
	@echo "Creating DMG installer..."
	$(CREATE_DMG) --overwrite dist/Plat\ de\ la\ Semaine.app .

build-windows: images env
	@echo "Building Windows application..."
	wine $(WINE_PYINSTALLER) --clean PDLS\ windows.spec

env:
	@if [ ! -f .env ]; then \
		echo "Creating default .env..."; \
		printf 'API_BASE_URL=https://676d02470e299dd2ddfe1998.mockapi.io/PDLS/v1\nMACOS_UPDATE_SCRIPT_URL=https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Scripts/MacOS.sh\nWINDOWS_UPDATE_SCRIPT_URL=https://raw.githubusercontent.com/pirlouix-dev/PDLS/refs/heads/main/Scripts/Windows.bat\nAPP_VERSION=3.8.1\nAPP_LINE_COUNT=3,000\nBUILD_TIMESTAMP=1749062742\n' > .env; \
		echo "Generated .env with release defaults — update before shipping a new version."; \
	fi

images:
	@echo "Compiling resources with pyrcc5..."
	$(VENV_LOCAL)/bin/pyrcc5 -o src/Images_rc.py Images.qrc

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist build *.dmg src/Images_rc.py
