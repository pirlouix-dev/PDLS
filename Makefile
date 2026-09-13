# Makefile for Plat de la Semaine (PDLS)

PROJECT_DIR      := $(CURDIR)
VENV_LOCAL       ?= $(PROJECT_DIR)/venv
VENV_MAC         ?= $(VENV_LOCAL)
WINE_PYINSTALLER ?= $(HOME)/.wine/drive_c/Program\ Files\ \(x86\)/Python38/Scripts/pyinstaller.exe
CREATE_DMG       ?= create-dmg

SHELL := /bin/bash

.PHONY: all build build-macos build-windows images ui clean

all: build

build: build-macos build-windows

build-macos: images
	@echo "Building macOS application..."
	$(VENV_MAC)/bin/pyinstaller --clean --noconfirm PDLS\ Mac.spec
	@echo "Creating DMG installer..."
	rm -rf /tmp/pdls-dmg
	mkdir -p /tmp/pdls-dmg
	cp -R "dist/Plat de la Semaine.app" /tmp/pdls-dmg/
	$(CREATE_DMG) \
		--volname "Plat de la Semaine" \
		--volicon "Icon.icns" \
		--window-pos 200 120 \
		--window-size 600 400 \
		--icon-size 100 \
		--icon "Plat de la Semaine.app" 175 120 \
		--app-drop-link 425 120 \
		--overwrite \
		"PDLS-MacOS.dmg" \
		/tmp/pdls-dmg/
	rm -rf /tmp/pdls-dmg

build-windows: images
	@echo "Building Windows application..."
	wine $(WINE_PYINSTALLER) --clean --noconfirm PDLS\ windows.spec

ui:
	@echo "Compiling .ui files with pyuic5..."
	for f in ui/*.ui; do \
		echo "  $$f -> src/$$(basename "$${f%.ui}").py"; \
		$(VENV_LOCAL)/bin/pyuic5 "$$f" -o "src/$$(basename "$${f%.ui}").py"; \
	done

images:
	@echo "Compiling resources with pyrcc5..."
	$(VENV_LOCAL)/bin/pyrcc5 -o src/Images_rc.py Images.qrc

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist build PDLS-MacOS.dmg PDLS-Windows.exe src/Images_rc.py
