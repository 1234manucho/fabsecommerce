"""Idempotent catalogue seed data for FABS Trading Global E-Commerce.

Display sequence (8 products per page):
    Page 1: factory-volume tabletop and component products
    Page 2: multi-unit venue expansion products
    Page 3: MOQ-1 starter machines

Run this module inside the Flask application context. Do not execute
``python seed.py`` directly.
"""

from decimal import Decimal

from models import Commodity, Game, db


PAGE_SIZE = 8

TRAILERS = {
    "vr": "https://videos.pexels.com/video-files/7774512/7774512-uhd_3840_2160_30fps.mp4",
    "arcade": "https://videos.pexels.com/video-files/7914936/7914936-hd_1920_1080_30fps.mp4",
    "racing": "https://videos.pexels.com/video-files/4291850/4291850-hd_1920_1080_30fps.mp4",
    "tabletop": "https://videos.pexels.com/video-files/17329650/17329650-hd_1920_1080_60fps.mp4",
}


# The list order is the intended catalogue order used by pagination.
GAME_DATA = [
    # PAGE 1 — FACTORY VOLUME
    {
        "slug": "truth-dare-card-game",
        "title": "Private-Label Truth & Dare Card Game",
        "genre": "Board Game",
        "platform": "Tabletop",
        "price": 1.15,
        "compare": 1.20,
        "image": "https://image.made-in-china.com/43f34j00RdfoYpFzHwct/Hot-Sell-Couples-and-Lovers-Game-in-Private-Truth-Dare-Card-Games.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "10 Packs (MOQ)",
        "supplier": "FABS Tabletop Manufacturing",
        "source": "Playing-card manufacturer product media",
        "summary": "A private-label card-game pack suitable for small market tests before larger customised print runs.",
    },
    {
        "slug": "wholesale-custom-board-game-set",
        "title": "Wholesale Custom Board Game Set",
        "genre": "Board Game",
        "platform": "Tabletop",
        "price": 2.40,
        "compare": 4.20,
        "image": "https://image.made-in-china.com/43f34j00MvCcZpGzbaun/Wholesale-Custom-Made-Board-Game-Set-From-China-Manufacturer.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "100 Sets (MOQ)",
        "supplier": "FABS Tabletop Manufacturing",
        "source": "Custom board-game manufacturer product media",
        "summary": "A configurable board-game set with printed board, cards, playing pieces and retail-ready packaging.",
    },
    {
        "slug": "custom-memory-card-game",
        "title": "Custom Printed Memory Card Game",
        "genre": "Board Game",
        "platform": "Tabletop",
        "price": 1.80,
        "compare": 2.00,
        "image": "https://image.made-in-china.com/43f34j00tlIeVCTZHuoM/China-Factory-Custom-Flash-Card-Printing-Customized-Adult-Question-Card-Game-Family-Card-Game-Children-Adult-Memo-Memory-Card-Game.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Sets (MOQ)",
        "supplier": "FABS Tabletop Manufacturing",
        "source": "Flash-card manufacturer product media",
        "summary": "Custom memory cards with full-colour artwork, optional question prompts and branded packaging.",
    },
    {
        "slug": "oem-playing-cards-packaging",
        "title": "OEM Playing Cards with Custom Packaging",
        "genre": "Board Game",
        "platform": "Tabletop",
        "price": 0.60,
        "compare": 0.98,
        "image": "https://image.made-in-china.com/43f34j00sAGWtkYURRGf/Custom-Card-Game-Manufacturer-OEM-Playing-Cards-Printing-Factory-with-Custom-Packaging.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Packs (MOQ)",
        "supplier": "FABS Tabletop Manufacturing",
        "source": "OEM playing-card manufacturer product media",
        "summary": "Custom playing-card production with printed faces, branded tuck box and optional finishing treatments.",
    },
    {
        "slug": "oem-tabletop-board-game",
        "title": "OEM Tabletop Board Game Printing Set",
        "genre": "Board Game",
        "platform": "Tabletop",
        "price": 0.60,
        "compare": 1.00,
        "image": "https://image.made-in-china.com/43f34j00BwMlTWFaOQGt/Custom-Board-Game-Manufacturer-OEM-Tabletop-Game-Printing-Factory.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Sets (MOQ)",
        "supplier": "FABS Tabletop Manufacturing",
        "source": "OEM tabletop manufacturer product media",
        "summary": "Factory-volume tabletop production covering boards, cards, tokens, instructions and custom boxes.",
    },
    {
        "slug": "food-memory-matching-game",
        "title": "Personalised Food Memory Matching Game",
        "genre": "Board Game",
        "platform": "Tabletop",
        "price": 1.25,
        "compare": 3.50,
        "image": "https://image.made-in-china.com/43f34j00uksoihdJwlqb/Personlized-OEM-Foodie-Favorites-Memory-Card-Game-Food-Matching-Game-with-Customized-Design.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "1,000 Sets (MOQ)",
        "supplier": "FABS Tabletop Manufacturing",
        "source": "Educational-game manufacturer product media",
        "summary": "A personalised food-themed matching game for education, retail promotions and private-label ranges.",
    },
    {
        "slug": "custom-ludo-game-pawns",
        "title": "Colour Board-Game Pawns & Ludo Pieces",
        "genre": "Board Game",
        "platform": "Tabletop",
        "price": 0.08,
        "compare": 0.15,
        "image": "https://image.made-in-china.com/43f34j00OeUGFyNhGLod/Plastic-Color-Board-Game-Flight-Chess-Ludo-Accessories-Game-Pawns.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "5,000 Pieces (MOQ)",
        "supplier": "FABS Game Components",
        "source": "Game-component manufacturer product media",
        "summary": "Injection-moulded game pawns available in customised colours, sizes and bulk packaging formats.",
    },
    {
        "slug": "custom-printed-d6-dice",
        "title": "16mm Custom-Printed D6 Game Dice",
        "genre": "Board Game",
        "platform": "Tabletop",
        "price": 0.05,
        "compare": 0.06,
        "image": "https://image.made-in-china.com/202f0j00NpofBOSwwurm/16mm-DIY-Printing-Kid-Toys-Game-Plastic-Dice-D6-Dice.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "10,000 Pieces (MOQ)",
        "supplier": "FABS Game Components",
        "source": "Custom-dice manufacturer product media",
        "summary": "Custom 16mm D6 dice for board-game production, promotions and branded educational sets.",
    },

    # PAGE 2 — VENUE EXPANSION
    {
        "slug": "interactive-basketball-arcade",
        "title": "Interactive Basketball Arcade Machine",
        "genre": "Sports Arcade",
        "platform": "Arcade / Sports",
        "price": 2700,
        "compare": 3200,
        "image": "https://www.gztomy.com/cdn/shop/products/China-Factory-Direct-Basketball-Arcade-for-Sale-Sport-series-1664345563.jpg?v=1664345567&width=1946",
        "trailer": TRAILERS["arcade"],
        "moq": "2 Pieces (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Basketball-arcade manufacturer product media",
        "summary": "A commercial basketball challenge machine with automatic ball return, electronic scoring and LED cabinet.",
    },
    {
        "slug": "commercial-claw-prize-machine",
        "title": "Full-Size Commercial Claw Prize Machine",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 1900,
        "compare": 2400,
        "image": "https://maxxgrab.com/cdn/shop/files/clawexpress4.jpg?crop=center&v=1764768516&width=600",
        "trailer": TRAILERS["arcade"],
        "moq": "2 Pieces (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "Commercial claw-machine product media",
        "summary": "A full-size prize crane with adjustable claw control, illuminated cabinet and clear merchandising display.",
    },
    {
        "slug": "commercial-skee-ball-lanes",
        "title": "Commercial Skee-Ball Redemption Lane",
        "genre": "Sports Arcade",
        "platform": "Arcade / Sports",
        "price": 2450,
        "compare": 2950,
        "image": "https://www.videoamusement.com/wp-content/uploads/2022/08/Skeeball-Arcade-Game-Custom-Branded-for-a-Corporate-Event-in-Las-Vegas-Video-Amusement.jpg",
        "trailer": TRAILERS["arcade"],
        "moq": "2 Lanes (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Commercial skee-ball product media",
        "summary": "An alley-ball redemption lane with enclosed targets, electronic scoring and configurable venue branding.",
    },
    {
        "slug": "motorcycle-racing-simulators",
        "title": "Commercial Motorcycle Racing Simulator",
        "genre": "Racing Simulator",
        "platform": "Arcade / Commercial",
        "price": 5600,
        "compare": 6400,
        "image": "https://yugamemachine.com/cdn/shop/files/MotoGpSimulatorArcadeRacingGameMachine_yugamemachine.webp?v=1703391364&width=1445",
        "trailer": TRAILERS["racing"],
        "moq": "2 Machines (MOQ)",
        "supplier": "FABS Racing Technology",
        "source": "Motorcycle-racing simulator product media",
        "summary": "A full-size racing cabinet with bike controls, commercial display, LED lighting and link-play capability.",
    },
    {
        "slug": "commercial-driving-simulator-55",
        "title": "55-Inch Commercial Driving Simulator",
        "genre": "Racing Simulator",
        "platform": "Arcade / Commercial",
        "price": 6800,
        "compare": 7900,
        "image": "https://image.made-in-china.com/43f34j00ayGVYNnsEJfL/Indoor-Game-Park-Coin-Operated-Racing-Gaming-55-Inch-Arcade-Video-Game-Machine-Car-Driving-Simulator.webp",
        "trailer": TRAILERS["racing"],
        "moq": "2 Machines (MOQ)",
        "supplier": "FABS Racing Technology",
        "source": "55-inch racing-machine manufacturer product media",
        "summary": "A venue-ready 55-inch driving simulator with force-feedback controls and linkable multiplayer operation.",
    },
    {
        "slug": "two-player-vr-attack",
        "title": "Two-Player VR Attack Shooting Simulator",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 9800,
        "compare": 10800,
        "image": "https://image.made-in-china.com/43f34j00QmeBPdKGykcZ/Vr-Attack-Shooting-Game-Simulator-2-Players-Amusement-Game-Equipment.webp",
        "trailer": TRAILERS["vr"],
        "moq": "2 Systems (MOQ)",
        "supplier": "FABS Immersive Systems",
        "source": "Two-player VR simulator product media",
        "summary": "A two-player virtual-reality shooting attraction with motion platform, headsets and operator controls.",
    },
    {
        "slug": "two-player-dance-arcade",
        "title": "Two-Player LED Dance Arcade System",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 7800,
        "compare": 8900,
        "image": "https://image.made-in-china.com/365f3j00zHAvrkKynEcU/New-Arrival-Arcade-Dance-Machine-2-Player-Interactive-Pump-It-up-Music-Rhythm-Dance-Revolution-Arcade-Machine-for-Sale.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "2 Systems (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "Two-player dance-machine product media",
        "summary": "A commercial rhythm system with two illuminated dance platforms, large display and integrated sound.",
    },
    {
        "slug": "six-seat-vr-flight-simulator",
        "title": "Six-Seat 9D VR Flight Simulator",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 16000,
        "compare": 18000,
        "image": "https://image.made-in-china.com/2f0j00tfWvpwUcOqkE/9d-Cinema-Vr-Flight-360-Motion-Shooting-Game-Equipment.webp",
        "trailer": TRAILERS["vr"],
        "moq": "2 Systems (MOQ)",
        "supplier": "FABS Immersive Systems",
        "source": "Multi-seat VR flight-simulator product media",
        "summary": "A multi-seat motion VR attraction designed for amusement parks, malls and high-capacity gaming venues.",
    },

    # PAGE 3 — STARTER ORDERS
    {
        "slug": "reaction-catch-stick-machine",
        "title": "Reaction Catch Stick Game Machine",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 260,
        "compare": 320,
        "image": "https://image.made-in-china.com/43f34j00YLICUsvlnOqi/The-Latest-Popular-Reaction-Catch-Stick-Game-Machine-Catch-Stick-Game.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "Reaction-machine manufacturer product media",
        "summary": "A compact reaction-speed attraction suitable for arcades, events, shopping centres and first-site trials.",
    },
    {
        "slug": "compact-led-claw-machine",
        "title": "Compact LED Claw Prize Machine",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 300,
        "compare": 450,
        "image": "https://image.made-in-china.com/2f0j00AGnCfviKrlbR/Funspace-New-Arcade-Coin-Operated-Basehall-Stars-Sport-Skill-Game-Machine-with-Prize-and-Gachapon.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "Compact prize-machine manufacturer product media",
        "summary": "A compact prize machine with LED lighting, coin operation and a small footprint for pilot locations.",
    },
    {
        "slug": "fury-43-skill-cabinet",
        "title": "43-Inch Commercial Skill Arcade Cabinet",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 570,
        "compare": 680,
        "image": "https://image.made-in-china.com/43f34j00RzdBvArcLjbY/USA-Entertaining-Gaming-Experiences-Fury-43-Cabinet-Fusion-Games-Skill-Game-Machine-Follow-The-Banana-Feature-Compatible-Wire-Installation-for-Sale.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "43-inch skill-cabinet manufacturer product media",
        "summary": "A commercial 43-inch game cabinet for operators testing a new title, floor layout or location.",
    },
    {
        "slug": "four-player-fish-game-console",
        "title": "Four-Player Fish Game Console",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 680,
        "compare": 850,
        "image": "https://image.made-in-china.com/43f34j00zWrvFSshGJcj/with-Btc-Bill-Acceptor-4-Player-Slot-Fish-Game-Consol.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "Four-player cabinet manufacturer product media",
        "summary": "A multi-player commercial cabinet supplied as a single-unit starter order for venue evaluation.",
    },
    {
        "slug": "coin-operated-foosball-table",
        "title": "Coin-Operated Commercial Foosball Table",
        "genre": "Table Game",
        "platform": "Arcade / Sports",
        "price": 880,
        "compare": 1080,
        "image": "https://s.alicdn.com/@sc04/kf/H373a284ea1b24a61adb4c9e2380910c9f.jpg",
        "trailer": TRAILERS["tabletop"],
        "moq": "1 Table (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Commercial foosball product media",
        "summary": "A reinforced coin-operated foosball table with durable rods, protected playfield and venue-grade cabinet.",
    },
    {
        "slug": "electronic-score-air-hockey",
        "title": "84-Inch Electronic-Score Air Hockey Table",
        "genre": "Table Game",
        "platform": "Arcade / Sports",
        "price": 1050,
        "compare": 1350,
        "image": "https://image.made-in-china.com/2f0j00iplYIfLnJZbG/Luxury-Sports-Commercial-Use-Electronic-Score-Counter-Indoor-Games-Push-Air-Hockey-Table-84inch.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Table (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Air-hockey manufacturer product media",
        "summary": "A commercial air-hockey table with electronic scoring, high-output airflow and illuminated cabinet.",
    },
    {
        "slug": "interactive-kiddie-ride",
        "title": "Interactive Coin-Operated Kiddie Ride",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 1550,
        "compare": 1900,
        "image": "https://tiimg.tistatic.com/fp/1/002/295/baby-kart-coin-operated-game-kiddie-ride-241.jpg",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Coin-operated kiddie-ride product media",
        "summary": "A child-focused ride with steering controls, lighting, sound and a compact mall-ready footprint.",
    },
    {
        "slug": "interactive-floor-projection-system",
        "title": "Interactive Floor Projection Gaming System",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 2800,
        "compare": 3400,
        "image": "https://www.interactivewallprojection.com/photo/pl203249613-interactive_system_all_in_one_interactive_mobile_floor_ground_projection_game.jpg",
        "trailer": TRAILERS["arcade"],
        "moq": "1 System (MOQ)",
        "supplier": "FABS Immersive Systems",
        "source": "Interactive-floor system product media",
        "summary": "An all-in-one movement-responsive projection platform for malls, play centres, events and schools.",
    },
]


COMMODITY_DATA = [
    ("bitumen", "Bitumen", "Road & construction", "40/50, 60/70, 80/100, PMB", "500 MT"),
    ("tmt-bars", "TMT Reinforcement Bars", "Steel products", "Multiple grades and diameters", "100 MT"),
    ("steel-angles", "Steel Angles", "Steel products", "Equal and unequal angles", "50 MT"),
    ("z-purlins", "Z Purlins", "Steel products", "Project-specific dimensions", "50 MT"),
    ("black-pipes", "Black Steel Pipes", "Steel products", "Welded and seamless", "50 MT"),
    ("i-beams", "I-Beams", "Structural steel", "Multiple profiles", "100 MT"),
    ("channels", "Steel Channels", "Structural steel", "U and C profiles", "50 MT"),
    ("chequered-plates", "Chequered Plates", "Steel plates", "Multiple thicknesses", "50 MT"),
    ("steel-plates", "Steel Plates", "Steel products", "Commercial and project grades", "100 MT"),
    ("expanded-metal", "Expanded Metal", "Fabricated steel", "Multiple mesh sizes", "20 MT"),
    ("weld-mesh", "Weld Mesh", "Fabricated steel", "Multiple wire gauges", "20 MT"),
    ("brc-mesh", "BRC Mesh", "Construction steel", "Standard sheets and rolls", "50 MT"),
    ("nails", "Construction Nails", "Fasteners", "Multiple lengths and gauges", "20 MT"),
    ("hollow-sections", "Hollow Sections", "Structural steel", "Square and rectangular", "50 MT"),
    ("base-oil", "Virgin & RC Base Oil", "Base oils", "SN grades and re-refined", "100 MT"),
    ("rpo", "Rubber Process Oil", "Process oils", "Aromatic and treated", "100 MT"),
    ("carbon-black", "Carbon Black", "Performance materials", "N-series grades", "25 MT"),
    ("caustic-soda", "Caustic Soda Flakes", "Industrial chemicals", "98–99%", "25 MT"),
]


def _duplicates(values):
    seen = set()
    return {value for value in values if value in seen or seen.add(value)}


def validate_seed_data():
    """Fail before database changes if identities, images or page sizes are wrong."""

    if len(GAME_DATA) != PAGE_SIZE * 3:
        raise ValueError(f"Expected 24 games for three 8-product pages; received {len(GAME_DATA)}")

    checks = {
        "game slugs": [item["slug"] for item in GAME_DATA],
        "game images": [item["image"] for item in GAME_DATA],
        "commodity slugs": [item[0] for item in COMMODITY_DATA],
    }
    for label, values in checks.items():
        repeated = _duplicates(values)
        if repeated:
            raise ValueError(f"Duplicate {label}: {sorted(repeated)}")


def seed_catalogue():
    """Create or refresh the catalogue safely and return record counts."""

    validate_seed_data()

    try:
        for index, item in enumerate(GAME_DATA):
            game = Game.query.filter_by(slug=item["slug"]).first()
            if game is None:
                game = Game(slug=item["slug"])
                db.session.add(game)

            game.title = item["title"]
            game.genre = item["genre"]
            game.platform = item["platform"]
            game.edition = "Commercial Supply"
            game.region = "Global"
            game.price = Decimal(str(item["price"]))
            game.compare_price = Decimal(str(item["compare"]))
            game.description = item["summary"]
            game.image_url = item["image"]
            game.trailer_url = item["trailer"]
            game.minimum_order = item["moq"]
            game.supplier = item["supplier"]
            game.photo_source = item["source"]
            game.stock_count = max(10, 100 - index)
            game.is_featured = index < PAGE_SIZE
            game.is_active = True

        commodity_image = "/static/images/commodity-list.jpeg"
        for slug, name, category, grade, moq in COMMODITY_DATA:
            commodity = Commodity.query.filter_by(slug=slug).first()
            if commodity is None:
                commodity = Commodity(slug=slug)
                db.session.add(commodity)

            commodity.name = name
            commodity.category = category
            commodity.grade = grade
            commodity.minimum_order = moq
            commodity.unit = "Metric tonne"
            commodity.incoterms = "EXW · FOB · CFR · CIF"
            commodity.description = (
                f"{name} supplied against confirmed specification, volume, "
                "destination and commercial terms."
            )
            commodity.applications = "Industrial processing|Manufacturing|Project supply"
            commodity.image_url = commodity_image
            commodity.is_active = True

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return {
        "games": len(GAME_DATA),
        "commodities": len(COMMODITY_DATA),
        "pages": len(GAME_DATA) // PAGE_SIZE,
        "unique_game_images": len({item["image"] for item in GAME_DATA}),
        "unique_commodity_images": 1,
    }
