# Introspection System

**Status:** Documentation skeleton - to be filled

## Overview

Screenshot capture, wireframes, video recording, and meta-analysis of player learning state.

### Table of Contents
- Introspection Architecture
- Screenshot & Wireframe System
- Video Recording & Mosaics
- TAS (Tool-Assisted Learning) System
- Discovery Primitives
- State Capture & Analysis

### Key Components
- `lmsp/introspection/screenshot.py` - Instant capture + metadata
- `lmsp/introspection/wireframe.py` - Mental wireframe (AST + state)
- `lmsp/introspection/video.py` - Strategic recording
- `lmsp/introspection/mosaic.py` - WebP mosaic generation

### Dependencies
- Screen capture library
- Image processing (PIL)
- AST parsing
- WebP encoding

### Testing Strategy
- Unit tests for capture logic
- Image generation validation
- Metadata correctness tests

## To Be Completed

- [ ] Screenshot system specification
- [ ] Wireframe format documentation
- [ ] Video recording parameters
- [ ] Mosaic composition algorithm
- [ ] TAS command reference
- [ ] Discovery primitive unlock levels
- [ ] Claude vision optimization
