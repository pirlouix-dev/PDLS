# Makefile for Plat de la Semaine (PDLS)

PROJECT_DIR      := $(CURDIR)
VENV_MAC         ?= $(HOME)/PDLS
VENV_LOCAL       ?= $(PROJECT_DIR)/venv
WINE_PYINSTALLER ?= $(HOME)/.wine/drive_c/Program\ Files\ \(x86\)/Python38/Scripts/pyinstaller.exe
CREATE_DMG       ?= create-dmg

SHELL := /bin/bash

.PHONY: all build build-macos build-windows images clean

all: build

build: build-macos build-windows

build-macos:
	@echo "Building macOS application..."
	source $(VENV_MAC)/bin/activate && pyinstaller --clean PDLS.spec
	@echo "Creating DMG installer..."
	$(CREATE_DMG) --overwrite dist/Plat\ de\ la\ Semaine.app .

build-windows:
	@echo "Building Windows application..."
	wine $(WINE_PYINSTALLER) --clean PDLS\ windows.spec

images:
	@echo "Compiling resources with pyrcc5..."
	$(VENV_LOCAL)/bin/pyrcc5 -o src/Images_rc.py Images.qrc

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist build *.dmg
