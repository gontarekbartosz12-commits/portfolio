# "Mrok Otchłani" — single-file HTML5/Canvas ARPG

A top-down, Diablo-like action-RPG that runs from **one HTML file** with
**zero dependencies and no build step**.

## Features
- WASD movement + mouse aim, real-time combat.
- **Procedurally generated pixel-art** — sprites and tiles drawn in code, no image assets.
- **Paper-doll system** — equipped gear changes the character's on-screen appearance.
- Entity system for enemies, loot and projectiles; collision + simple enemy AI.

## Engineering
- `requestAnimationFrame` game loop with a clean update/render split.
- All state managed in vanilla JS — no framework, no libraries.
- Shipped **v0.1, reviewed with 0 blocker bugs**; a v2 rebuild is in progress.

## Stack
JavaScript (ES6) · HTML5 Canvas · 0 dependencies

## Run
Open `index.html` in any modern browser. That's it.

> Game source lives in `C:\Users\gonta\pixel-arpg\` (and `pixel-arpg-v2\`).
