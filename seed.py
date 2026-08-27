"""Idempotent catalogue seed data for FABS Trading Global E-Commerce.

Run this module through the Flask application context. See the Render commands
in the handoff message; do not execute ``python seed.py`` directly.
"""

from decimal import Decimal

from models import Commodity, Game, db


TRAILERS = {
    "vr": "https://videos.pexels.com/video-files/7774512/7774512-uhd_3840_2160_30fps.mp4",
    "arcade": "https://videos.pexels.com/video-files/7914936/7914936-hd_1920_1080_30fps.mp4",
    "racing": "https://videos.pexels.com/video-files/4291850/4291850-hd_1920_1080_30fps.mp4",
    "tabletop": "https://videos.pexels.com/video-files/17329650/17329650-hd_1920_1080_60fps.mp4",
}


GAME_DATA = [
    {
        "slug": "hologate-vr-arcade",
        "title": "HOLOGATE Multiplayer VR Arena",
        "genre": "VR Simulator",
        "platform": "VR / Commercial",
        "price": 9500,
        "compare": 11800,
        "image": "https://www.hologate.com/wp-content/uploads/2021/04/HG_Upgrade_Arena_01-1000x1000.jpg",
        "trailer": TRAILERS["vr"],
        "moq": "1 Set (MOQ)",
        "supplier": "FABS Immersive Systems",
        "source": "HOLOGATE official product media",
        "summary": "A room-scale commercial VR attraction for family entertainment centres, malls and professional gaming venues.",
    },
    {
        "slug": "vr-360-motion-simulator",
        "title": "Two-Seat 360° VR Motion Simulator",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 19000,
        "compare": 21000,
        "image": "https://image.made-in-china.com/2f0j00MJDqmySlGfbV/Exclusive-Edition-Vr-Game-Machines-Black-and-White-Color-Vr-360-Degree-Rolling-for-Adults-Vr-Game-Room.jpg",
        "trailer": TRAILERS["vr"],
        "moq": "1 Set (MOQ)",
        "supplier": "FABS Immersive Systems",
        "source": "Manufacturer product media",
        "summary": "A dual-seat 360-degree motion platform engineered for amusement parks, malls and professional VR venues.",
    },
    {
        "slug": "commercial-racing-simulator",
        "title": "Full-Size Commercial Racing Simulator",
        "genre": "Racing Simulator",
        "platform": "Arcade / Commercial",
        "price": 5800,
        "compare": 7200,
        "image": "https://s.alicdn.com/@sc04/kf/Hee6c0c70a59649f0af7246fad4ff6c812/Coin-Operated-Metal-Arcade-Racing-Simulator-High-Quality-Driving-Simulation-Racing-Game-Machine-for-Sale.jpg",
        "trailer": TRAILERS["racing"],
        "moq": "1 Set (MOQ)",
        "supplier": "FABS Racing Technology",
        "source": "Commercial racing-simulator supplier reference media",
        "summary": "A complete force-feedback racing cockpit with commercial cabinet, adjustable seat, wheel, pedals and display.",
    },
    {
        "slug": "air-hockey-arcade-table",
        "title": "Two-Player Air Hockey Arcade Table",
        "genre": "Table Game",
        "platform": "Arcade / Recreation",
        "price": 1150,
        "compare": 1450,
        "image": "https://image.made-in-china.com/2f0j00iplYIfLnJZbG/Luxury-Sports-Commercial-Use-Electronic-Score-Counter-Indoor-Games-Push-Air-Hockey-Table-84inch.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Manufacturer product media",
        "summary": "Commercial two-player air hockey with LED cabinet, digital scoring, high-output airflow and coin operation.",
    },
    {
        "slug": "coin-operated-arcade-cabinet",
        "title": "Coin-Operated Sports Arcade Cabinet",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 800,
        "compare": 960,
        "image": "https://image.made-in-china.com/2f0j00AGnCfviKrlbR/Funspace-New-Arcade-Coin-Operated-Basehall-Stars-Sport-Skill-Game-Machine-with-Prize-and-Gachapon.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "FUNSPACE sports-arcade product reference media",
        "summary": "A venue-ready coin-operated cabinet with dual-player controls, illuminated display and configurable graphics.",
    },
    {
        "slug": "shooting-master-arcade",
        "title": "Shooting Master Arcade Machine",
        "genre": "Shooting Game",
        "platform": "Arcade / Commercial",
        "price": 6800,
        "compare": 8200,
        "image": "https://image.made-in-china.com/202f0j00yjnbNlEzPmcS/Game-City-Children-s-Simulated-Shooting-Machine-Two-Person-Shooting-Game-Machine-Adult-Coin-Operated-Large-Game-Machine-Entertainment-Equipment.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "Guangzhou Shanghaojia shooting-machine product media",
        "summary": "A full-length commercial shooting attraction with rifle controller, illuminated cabinet and digital scoring.",
    },
    {
        "slug": "interactive-basketball-arcade",
        "title": "Interactive Basketball Arcade Machine",
        "genre": "Sports Arcade",
        "platform": "Arcade / Sports",
        "price": 3200,
        "compare": 3950,
        "image": "https://www.gztomy.com/cdn/shop/products/China-Factory-Direct-Basketball-Arcade-for-Sale-Sport-series-1664345563.jpg?v=1664345567&width=1946",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Tomy Arcade basketball-machine product media",
        "summary": "A commercial basketball challenge machine with animated display, automatic ball return, scoring and LED cabinet.",
    },
    {
        "slug": "dual-lane-bowling-arcade",
        "title": "Dual-Lane Bowling Arcade Machine",
        "genre": "Sports Arcade",
        "platform": "Arcade / Sports",
        "price": 7200,
        "compare": 8900,
        "image": "https://xtremeeventsgroup.com.au/wp-content/uploads/2024/12/Sq-Lane-Master-8_Sm.jpg",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Set (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Xtreme Events Lane Master reference media",
        "summary": "A two-lane bowling attraction with animated displays, illuminated cabinet, scoring and ticket redemption.",
    },
    {
        "slug": "adventure-board-game-oem",
        "title": "OEM Adventure Board Game Manufacturing Set",
        "genre": "Board Game",
        "platform": "Tabletop",
        "price": 3.20,
        "compare": 5.40,
        "image": "https://www.eastarboardgame.com/ueditor/php/upload/image/20251218/1766032571981781.jpg",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Sets (MOQ)",
        "supplier": "FABS Tabletop Manufacturing",
        "source": "Eastar custom board-game component media",
        "summary": "Complete OEM tabletop production with illustrated cards, tokens, rules and custom retail-box packaging.",
    },
    {
        "slug": "custom-strategy-board-game",
        "title": "Custom Printed Strategy Board Game Set",
        "genre": "Board Game",
        "platform": "Tabletop",
        "price": 2.10,
        "compare": 3.80,
        "image": "https://littlemagic.pro/pic/banmo2.jpeg",
        "trailer": TRAILERS["tabletop"],
        "moq": "200 Sets (MOQ)",
        "supplier": "FABS Tabletop Manufacturing",
        "source": "Little Magic OEM tabletop product media",
        "summary": "Custom printed strategy game with cards, wooden tokens, game board and rigid retail packaging.",
    },
    {
        "slug": "family-arcade-racing-twin",
        "title": "Twin-Seat Family Arcade Racing System",
        "genre": "Racing Simulator",
        "platform": "Arcade / Commercial",
        "price": 10800,
        "compare": 12800,
        "image": "https://image.made-in-china.com/2f0j00BFcbtyKsGYkw/Commercial-Video-Arcade-Racing-Game-for-Two-Player-Children-and-Adult-Players-Around-The-World-Simulator.webp",
        "trailer": TRAILERS["racing"],
        "moq": "1 Pair (MOQ)",
        "supplier": "FABS Racing Technology",
        "source": "Guangzhou Shanghaojia twin-racing product media",
        "summary": "Linked twin-seat racing system for family entertainment centres with competitive multi-player configuration.",
    },
    {
        "slug": "immersive-vr-venue-package",
        "title": "Immersive VR Venue Starter Package",
        "genre": "VR Simulator",
        "platform": "VR / Commercial",
        "price": 24500,
        "compare": 28900,
        "image": "https://portal-vr.ru/wp-content/uploads/2024/02/elb_3175-1-scaled.jpg",
        "trailer": TRAILERS["vr"],
        "moq": "1 Venue Package (MOQ)",
        "supplier": "FABS Immersive Systems",
        "source": "Portal VR free-roam venue reference media",
        "summary": "A structured starter package combining room-scale hardware, operator workflow and venue installation planning.",
    },
    {
        "slug": "commercial-claw-prize-machine",
        "title": "Commercial LED Claw Prize Machine",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 2500,
        "compare": 3100,
        "image": "https://maxxgrab.com/cdn/shop/files/clawexpress4.jpg?crop=center&v=1764768516&width=600",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "Maxx Grab commercial claw-machine reference media",
        "summary": "A commercial prize crane with illuminated cabinet, adjustable claw control, coin operation and clear merchandising display.",
    },
    {
        "slug": "two-player-dance-arcade",
        "title": "Two-Player LED Dance Arcade System",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 8900,
        "compare": 10500,
        "image": "https://image.made-in-china.com/365f3j00zHAvrkKynEcU/New-Arrival-Arcade-Dance-Machine-2-Player-Interactive-Pump-It-up-Music-Rhythm-Dance-Revolution-Arcade-Machine-for-Sale.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Set (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "FUNSPACE dance-arcade product reference media",
        "summary": "A two-player rhythm system with illuminated dance platforms, commercial display, sound system and venue-ready cabinet.",
    },
    {
        "slug": "boxing-punch-arcade",
        "title": "Commercial Boxing Punch Arcade Machine",
        "genre": "Sports Arcade",
        "platform": "Arcade / Sports",
        "price": 4200,
        "compare": 5100,
        "image": "https://image.made-in-china.com/2f0j00RAJCqmwbNGod/Neofuns-Punch-and-Kick-3-Boxing-Arcade-Street-Amusement-Coin-Operated-Games-Electronic-Sports-Punching-Bag-Vending-Machine-Price.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Neofuns boxing-machine product reference media",
        "summary": "A coin-operated boxing attraction with suspended punch bag, electronic power scoring, LED cabinet and high-traffic venue design.",
    },
    {
        "slug": "motorcycle-racing-arcade",
        "title": "Commercial Motorcycle Racing Arcade Simulator",
        "genre": "Racing Simulator",
        "platform": "Arcade / Commercial",
        "price": 6200,
        "compare": 7500,
        "image": "https://yugamemachine.com/cdn/shop/files/MotoGpSimulatorArcadeRacingGameMachine_yugamemachine.webp?v=1703391364&width=1445",
        "trailer": TRAILERS["racing"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Racing Technology",
        "source": "Yugamemachine motorcycle-racing product media",
        "summary": "A full-size motorcycle racing cabinet with bike controls, commercial display, LED lighting and multiplayer-link capability.",
    },
    {
        "slug": "coin-operated-foosball-table",
        "title": "Coin-Operated Commercial Foosball Table",
        "genre": "Table Game",
        "platform": "Arcade / Recreation",
        "price": 1350,
        "compare": 1650,
        "image": "https://s.alicdn.com/@sc04/kf/H373a284ea1b24a61adb4c9e2380910c9f.jpg",
        "trailer": TRAILERS["tabletop"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Commercial foosball product reference media",
        "summary": "A reinforced commercial foosball table with coin mechanism, durable rods, protected playfield and venue-grade cabinet.",
    },
    {
        "slug": "vr-flight-motion-simulator",
        "title": "Single-Seat VR Flight Motion Simulator",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 11800,
        "compare": 13500,
        "image": "https://image.made-in-china.com/2f0j00tfWvpwUcOqkE/9d-Cinema-Vr-Flight-360-Motion-Shooting-Game-Equipment.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 Set (MOQ)",
        "supplier": "FABS Immersive Systems",
        "source": "Movie Power VR flight-simulator product media",
        "summary": "A compact full-motion VR aircraft simulator with reclined seat, interactive controls, effects and spectator display.",
    },
    {
        "slug": "dual-seat-9d-vr-cinema",
        "title": "Dual-Seat 9D VR Cinema Simulator",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 9800,
        "compare": 11900,
        "image": "https://s.alicdn.com/@sc04/kf/Hcc3f35ddb6824d32951a97acea598813c/Dreamland-9D-Cine-Box-360-Degree-VR-Cinema-Simulator-Including-200-Free-VR-Movies.jpg",
        "trailer": TRAILERS["vr"],
        "moq": "1 Set (MOQ)",
        "supplier": "FABS Immersive Systems",
        "source": "Dreamland dual-seat VR cinema reference media",
        "summary": "A two-seat motion cinema pod with individual VR headsets, synchronized effects, illuminated platform and operator controls.",
    },
    {
        "slug": "coin-operated-kiddie-ride",
        "title": "Interactive Coin-Operated Kiddie Ride",
        "genre": "Arcade Game",
        "platform": "Arcade / Family",
        "price": 1850,
        "compare": 2300,
        "image": "https://tiimg.tistatic.com/fp/1/002/295/baby-kart-coin-operated-game-kiddie-ride-241.jpg",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Jin Teng Baby Kart product reference media",
        "summary": "A child-focused coin-operated ride with steering controls, animated display, lighting and compact mall-ready footprint.",
    },
    {
        "slug": "commercial-skee-ball-lane",
        "title": "Commercial Skee-Ball Redemption Lane",
        "genre": "Sports Arcade",
        "platform": "Arcade / Sports",
        "price": 2750,
        "compare": 3400,
        "image": "https://www.videoamusement.com/wp-content/uploads/2022/08/Skeeball-Arcade-Game-Custom-Branded-for-a-Corporate-Event-in-Las-Vegas-Video-Amusement.jpg",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Lane (MOQ)",
        "supplier": "FABS Recreation Equipment",
        "source": "Video Amusement skee-ball reference media",
        "summary": "A commercial alley-ball redemption lane with enclosed targets, electronic scoring and customizable venue branding.",
    },
    {
        "slug": "commercial-pinball-machine",
        "title": "Commercial Electronic Pinball Machine",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 8900,
        "compare": 10500,
        "image": "https://o.pinside.com/4/d2/e0/4d2e09c1799bebf4dea9bfbffb3a74f2dbab9b01.jpeg",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "FABS Arcade Distribution",
        "source": "Pinside commercial pinball venue reference media",
        "summary": "A full-size electronic pinball platform with illuminated playfield, mechanical targets, digital scoring and commercial cabinet.",
    },
    {
        "slug": "interactive-floor-projection-system",
        "title": "Interactive Floor Projection Gaming System",
        "genre": "Arcade Game",
        "platform": "Interactive / Commercial",
        "price": 3100,
        "compare": 3900,
        "image": "https://www.interactivewallprojection.com/photo/pl203249613-interactive_system_all_in_one_interactive_mobile_floor_ground_projection_game.jpg",
        "trailer": TRAILERS["arcade"],
        "moq": "1 System (MOQ)",
        "supplier": "FABS Immersive Systems",
        "source": "Northern Lights interactive-floor product media",
        "summary": "An all-in-one movement-responsive floor projection platform for malls, play centres, events and educational venues.",
    },
    {
        "slug": "esports-venue-workstation-package",
        "title": "Professional Esports Venue Workstation Package",
        "genre": "Esports System",
        "platform": "PC / Commercial",
        "price": 18500,
        "compare": 22000,
        "image": "https://bytespeed.com/wp-content/uploads/elementor/thumbs/Esports-Evo-S2S-Shoutcaster-Genova-Room-Opt2-071421-qw3cisynxcnowq0fsai0o5tyytjpdfcfx7xw2h1r48.jpg",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Venue Package (MOQ)",
        "supplier": "FABS Esports Technology",
        "source": "ByteSpeed Spectrum esports-furniture reference media",
        "summary": "A commercial esports package combining gaming desks, ergonomic seating, display positions, cable management and venue planning.",
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
    """Fail before touching the database if seed identities or images repeat."""

    game_slugs = [item["slug"] for item in GAME_DATA]
    game_images = [item["image"] for item in GAME_DATA]
    commodity_slugs = [item[0] for item in COMMODITY_DATA]
    checks = {
        "game slugs": game_slugs,
        "game images": game_images,
        "commodity slugs": commodity_slugs,
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
            game.stock_count = 100
            game.is_featured = index < 8
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
        "unique_game_images": len({item["image"] for item in GAME_DATA}),
        "unique_commodity_images": 1,
    }
