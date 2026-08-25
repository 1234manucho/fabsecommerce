# FABS Trading Content Architecture

## Purpose

The website separates retail discovery, B2B procurement and corporate assurance into page families. Each page has one primary audience and one primary next action.

| Page family | Principal audience | Purpose | Primary action |
| --- | --- | --- | --- |
| Games | Retail and corporate digital buyers | Discover titles and understand delivery | View product / add to cart |
| Commodities | Procurement and project teams | Define an industrial requirement | Submit RFQ |
| Industries, Logistics, Quality | Technical and operational buyers | Explain scope and controls | Open RFQ |
| Company pages | Board, partners and stakeholders | Present governance and operating model | Contact FABS |
| Newsroom | Buyers and decision-makers | Educate and build commercial confidence | Read briefing |
| Support and legal | Customers, compliance and counsel | Explain service and policy boundaries | Contact / self-service |

## Media strategy

- Images use remote Unsplash delivery URLs with responsive crop parameters.
- Videos use remote Pexels MP4 assets, autoplay only when muted, looped and `playsinline`.
- The hero network uses NASA Blue Marble imagery as its factual Earth visual, surrounded by real commerce photography.
- Every video includes a still poster so the page remains visually complete when video is unavailable or data-saving settings apply.
- Product imagery is stored on the catalogue record and rendered dynamically on cards and detail pages.
- Media never replaces the product specification, compatibility statement, contract or policy text.

Before production, approve each asset for licence, brand fit, accessibility and long-term delivery. Approved assets can be copied to an organisation-controlled CDN while retaining the existing templates.

## Interaction layer

- Responsive navigation with a mobile menu
- Site search overlay with Escape and `/` keyboard handling
- Catalogue search and platform filters
- Accessible disclosure components for help content
- Bank-hosted checkout handoff with no raw card-data collection in FABS
- Animated content reveals implemented as progressive enhancement
- Pointer-responsive global hero with an explicit pause control
- Continuous product-image rails with hover pause and reduced-motion fallbacks

## Content governance

Assign an owner and review interval to product, commercial, compliance, corporate and policy content. Newsroom dates and claims should pass editorial approval before publishing. Technical specifications and transaction documents always override general website descriptions.
