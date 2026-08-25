# FABS Trading — Global Sapphire Interface System

## Design objective

Global Sapphire combines the confidence of an international trade institution with the energy of a modern digital marketplace. The interface uses dark cinematic surfaces for discovery and product media, while transaction, documentation and corporate-reading areas use bright pearl surfaces for clarity and trust.

## Core palette

| Role | Colour | Hex | Primary use |
| --- | --- | --- | --- |
| Midnight navy | FABS Ink | `#071426` | Navigation, heroes, footer and premium dark sections |
| Royal sapphire | FABS Primary | `#176BFF` | Primary actions, active controls and status emphasis |
| Electric cyan | Games Accent | `#20C9FF` | Gaming previews, digital links and interactive focus states |
| Refined bronze | Trade Accent | `#C58A3A` | Commodities, RFQs, technical documents and trade calls to action |
| Pearl | Commerce Surface | `#F6F8FC` | Catalogues, forms, corporate content and checkout surfaces |
| Silver | Interface Border | `#DCE3EC` | Light card borders, dividers and input outlines |
| Graphite | Primary Copy | `#111827` | Main text on pearl and white surfaces |
| Slate | Secondary Copy | `#64748B` | Supporting copy, metadata and form guidance |
| Emerald | Positive Status | `#10B981` | Availability, successful payment and verified states |

## Division logic

- **FABS Games:** midnight navy, sapphire and cyan. Motion, video and preview controls use cyan sparingly to signal interaction.
- **FABS Commodities:** pearl, graphite and bronze. Bronze identifies trade workflows without weakening the main corporate brand.
- **Corporate and checkout:** pearl and white surfaces with sapphire actions. This improves readability and supports trust-sensitive decisions.

## Accessibility rules

- Pearl surfaces use graphite or slate text; dark surfaces use pearl-white text.
- Interactive keyboard focus uses a visible cyan outline.
- Colour never carries status meaning alone; text labels remain present.
- Remote photography retains dark or light overlays so headings meet practical contrast requirements.
- Primary actions remain sapphire across the system; bronze is reserved for industrial trade actions.

## Implementation

The final override layer is `static/css/global-sapphire.css`. It loads after the base, premium, immersive and game-store styles, allowing the palette to be maintained without changing the application’s structural templates.
