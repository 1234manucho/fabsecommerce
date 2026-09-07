"""Idempotent, gaming-only catalogue seed for FABS Gaming Marketplace.

The catalogue contains exactly 80 products: eight products on each of ten pages.
Starting unit prices are non-decreasing from page 1 through page 10. In the
games route, preserve that contract with::

    Game.query.filter_by(is_active=True).order_by(Game.price.asc(), Game.id.asc())

Run this module inside the Flask application context. Do not execute
``python seed.py`` directly.

Every run refreshes the 80 approved gaming products, deactivates obsolete game
rows that are no longer part of this catalogue, and deactivates all legacy
commodity rows. Nothing is deleted, so historical order and enquiry relations
remain intact.
"""

from decimal import Decimal

from models import Commodity, Game, db


PAGE_SIZE = 8
PAGE_COUNT = 10

TRAILERS = {
    "vr": "https://videos.pexels.com/video-files/7774512/7774512-uhd_3840_2160_30fps.mp4",
    "arcade": "https://videos.pexels.com/video-files/7914936/7914936-hd_1920_1080_30fps.mp4",
    "racing": "https://videos.pexels.com/video-files/4291850/4291850-hd_1920_1080_30fps.mp4",
    "sports": "https://videos.pexels.com/video-files/7914936/7914936-hd_1920_1080_30fps.mp4",
    "tabletop": "https://videos.pexels.com/video-files/17329650/17329650-hd_1920_1080_60fps.mp4",
}


# List order is the intended catalogue order. The route must order by price,
# then id, so pagination remains deterministic after repeat seed runs.
GAME_DATA = [
    # 01 · PAGE 1
    {
        "slug": "oem-manufacturer-winning-moves-custom-printing-playing-cards-2-001",
        "title": "OEM Manufacturer Winning Moves Custom Printing Playing Cards 2.2 Inch X 3.4 Inch Table Board Games",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 0.2,
        "compare": 1.99,
        "image": "https://image.made-in-china.com/43f34j00PoSldsgDZTfC/OEM-Manufacturer-Winning-Moves-Custom-Printing-Playing-Cards-2-2-Inch-X-3-4-Inch-Table-Board-Games.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "1,000 Sets (MOQ)",
        "supplier": "Shenzhen Hestron International Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 02 · PAGE 1
    {
        "slug": "alphabet-and-animal-matching-game-card-game-002",
        "title": "Alphabet and Animal Matching Game Card Game",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 0.5,
        "compare": 0.68,
        "image": "https://image.made-in-china.com/43f34j00RwfevloznTqd/Alphabet-and-Animal-Matching-Game-Card-Game.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "1,000 Sets (MOQ)",
        "supplier": "Taizhou Melon Toys Co., Ltd",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 03 · PAGE 1
    {
        "slug": "colorful-high-quality-dinosaur-board-game-playing-cards-table-003",
        "title": "Colorful High Quality Dinosaur Board Game Playing Cards Table Board Games Dice Rolling Strategy Board Games Game Card Printing",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 0.65,
        "compare": 0.96,
        "image": "https://image.made-in-china.com/43f34j00gFEoHUkzHvbM/Colorful-High-Quality-Dinosaur-Board-Game-Playing-Cards-Table-Board-Games-Dice-Rolling-Strategy-Board-Games-Game-Card-Printing.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "1,000 Sets (MOQ)",
        "supplier": "Taizhou Melon Toys Co., Ltd",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 04 · PAGE 1
    {
        "slug": "custom-printing-paper-plastic-table-board-games-adults-travell-004",
        "title": "Custom Printing Paper Plastic Table Board Games Adults Travelling Playing Cards",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 0.8,
        "compare": 1.15,
        "image": "https://image.made-in-china.com/43f34j00QSYcEzPBqokU/Custom-Printing-Paper-Plastic-Table-Board-Games-Adults-Travelling-Playing-Cards.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Sets (MOQ)",
        "supplier": "Taizhou Melon Toys Co., Ltd",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 05 · PAGE 1
    {
        "slug": "wholesale-oem-paper-playing-card-oracle-tarot-decks-cards-cust-005",
        "title": "Wholesale OEM Paper Playing Card Oracle Tarot Decks Cards Custom Printed Card Game",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 0.9,
        "compare": 1.9,
        "image": "https://image.made-in-china.com/43f34j00VSHhfWRPOioz/Wholesale-OEM-Paper-Playing-Card-Oracle-Tarot-Decks-Cards-Custom-Printed-Card-Game.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Deck (MOQ)",
        "supplier": "Carrie Smart (Shenzhen) Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 06 · PAGE 1
    {
        "slug": "adjustable-bet-handheld-sticky-catch-ball-game-006",
        "title": "Adjustable Bet Handheld Sticky Catch Ball Game",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 1.19,
        "compare": 1.19,
        "image": "https://image.made-in-china.com/43f34j00izeGMrBCAuqw/Adjustable-Bet-Handheld-Sticky-Catch-Ball-Game.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "500 Pieces (MOQ)",
        "supplier": "Nanjing Bewe Intl Trading Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 07 · PAGE 1
    {
        "slug": "high-quality-custom-children-s-party-memory-card-game-set-boar-007",
        "title": "High Quality Custom Children's Party Memory Card Game Set Board Games",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 1.5,
        "compare": 1.5,
        "image": "https://image.made-in-china.com/43f34j00UvbeTAEcAVkn/High-Quality-Custom-Children-s-Party-Memory-Card-Game-Set-Board-Games.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Pieces (MOQ)",
        "supplier": "Anhui Beauty Culture Development Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 08 · PAGE 1
    {
        "slug": "kids-learning-toys-educational-board-games-for-kids-008",
        "title": "Kids Learning Toys Educational Board Games for Kids",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 1.9,
        "compare": 1.9,
        "image": "https://image.made-in-china.com/43f34j00mNEMkgRFEroV/Kids-Learning-Toys-Educational-Board-Games-for-Kids.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Pieces (MOQ)",
        "supplier": "Anhui Beauty Culture Development Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 09 · PAGE 2
    {
        "slug": "children-s-classic-puzzle-casual-battle-board-game-xo-interact-009",
        "title": "Children's Classic Puzzle Casual Battle Board Game Xo Interactive Board Toys",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 2,
        "compare": 2.2,
        "image": "https://image.made-in-china.com/43f34j00SwDoPKmAyTcY/Children-s-Classic-Puzzle-Casual-Battle-Board-Game-Xo-Interactive-Board-Toys.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "1,000 Sets (MOQ)",
        "supplier": "Hangzhou Ez Leisure Co., Ltd",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 10 · PAGE 2
    {
        "slug": "customizable-middle-east-style-card-games-010",
        "title": "Customizable Middle East Style Card Games",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 2.31,
        "compare": 3.35,
        "image": "https://image.made-in-china.com/43f34j00ZdJWRQLclsYy/Customizable-Middle-East-Style-Card-Games.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "1,000 Pieces (MOQ)",
        "supplier": "Ningbo Uwin Board Games Manufacturing Co., Ltd",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 11 · PAGE 2
    {
        "slug": "custom-design-oem-adult-playing-card-table-board-game-for-part-011",
        "title": "Custom Design OEM Adult Playing Card Table Board Game for Party Entertainment",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 2.5,
        "compare": 6,
        "image": "https://image.made-in-china.com/43f34j00LfKCkTaBIPzE/Custom-Design-OEM-Adult-Playing-Card-Table-Board-Game-for-Party-Entertainment.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "1,000 Pieces (MOQ)",
        "supplier": "Xiamen Fulego International Trade Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 12 · PAGE 2
    {
        "slug": "torson-100-card-storage-deck-box-customizable-oem-board-game-c-012",
        "title": "Torson 100+ Card Storage Deck Box Customizable OEM Board Game Case Printed Gift Environmentally Friendly Custom Colors",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 2.71,
        "compare": 3.14,
        "image": "https://image.made-in-china.com/43f34j00MtSjslhqkWkC/Torson-100-Card-Storage-Deck-Box-Customizable-OEM-Board-Game-Case-Printed-Gift-Environmentally-Friendly-Custom-Colors.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "80 Pieces (MOQ)",
        "supplier": "Dongguan Tuoxiang Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 13 · PAGE 2
    {
        "slug": "hot-sale-high-quality-30-piece-beer-pong-party-drinking-cup-ga-013",
        "title": "Hot Sale High Quality 30 Piece Beer Pong Party Drinking Cup Games",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 3.8,
        "compare": 3.8,
        "image": "https://image.made-in-china.com/43f34j00wRTBFEgMbnkt/Hot-Sale-High-Quality-30-Piece-Beer-Pong-Party-Drinking-Cup-Games.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Pieces (MOQ)",
        "supplier": "Ningbo XiaoChuang Crafts Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 14 · PAGE 2
    {
        "slug": "customised-cash-flow-playing-family-fun-card-game-tabletop-boa-014",
        "title": "Customised Cash Flow Playing Family Fun Card Game Tabletop Board Games",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 5,
        "compare": 6.5,
        "image": "https://image.made-in-china.com/43f34j00VCEbaGQKufpB/Customised-Cash-Flow-Playing-Family-Fun-Card-Game-Tabletop-Board-Games.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Sets (MOQ)",
        "supplier": "Qingdao Chenghaoda Science and Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 15 · PAGE 2
    {
        "slug": "board-game-printing-glossy-lamination-with-playing-cards-dices-015",
        "title": "Board Game Printing Glossy Lamination with Playing Cards Dices Pawns",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 6,
        "compare": 8,
        "image": "https://image.made-in-china.com/43f34j00DvjVbCyhyice/Board-Game-Printing-Glossy-Lamination-with-Playing-Cards-Dices-Pawns.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Pieces (MOQ)",
        "supplier": "Jiang-house Co-operated Co., Limited",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 16 · PAGE 2
    {
        "slug": "torson-1360-large-capacity-pu-deck-box-with-separable-storage-016",
        "title": "Torson 1360 Large Capacity PU Deck Box with Separable Storage Cover for Commander Tcg Board Games Yugioh for Playing Cards",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 9.5,
        "compare": 9.5,
        "image": "https://image.made-in-china.com/43f34j00gTisEnNPYWoQ/Torson-1360-Large-Capacity-PU-Deck-Box-with-Separable-Storage-Cover-for-Commander-Tcg-Board-Games-Yugioh-for-Playing-Cards.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "15 Pieces (MOQ)",
        "supplier": "Dongguan Tuoxiang Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 17 · PAGE 3
    {
        "slug": "torson-270-trading-card-game-deck-box-premium-playing-cards-bo-017",
        "title": "Torson 270+ Trading Card Game Deck Box Premium Playing Cards Board Game Storage Solution",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 10,
        "compare": 11,
        "image": "https://image.made-in-china.com/43f34j00LQNKldpDLhqF/Torson-270-Trading-Card-Game-Deck-Box-Premium-Playing-Cards-Board-Game-Storage-Solution.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "20 Pieces (MOQ)",
        "supplier": "Dongguan Tuoxiang Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 18 · PAGE 3
    {
        "slug": "new-custom-pu-leather-play-chessboard-luxury-chess-game-set-ch-018",
        "title": "New Custom PU Leather Play Chessboard Luxury Chess Game Set Chess Pieces Backgammon Checkers Wooden 3 in 1 Chess Board Games Set",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 11.2,
        "compare": 13.5,
        "image": "https://image.made-in-china.com/43f34j00gEQeOtdaqIqz/New-Custom-PU-Leather-Play-Chessboard-Luxury-Chess-Game-Set-Chess-Pieces-Backgammon-Checkers-Wooden-3-in-1-Chess-Board-Games-Set.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "500 Pieces (MOQ)",
        "supplier": "Shenzhen Lionstar Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 19 · PAGE 3
    {
        "slug": "torson-customizable-three-row-pu-leather-card-game-storage-box-019",
        "title": "Torson Customizable Three-Row PU Leather Card Game Storage Box Removable Lid Table Game Waterproof Durable Eco-Friendly Gaming",
        "genre": "Tabletop Game",
        "platform": "Tabletop / Retail",
        "price": 13,
        "compare": 13.5,
        "image": "https://image.made-in-china.com/43f34j00nteKNVTskloB/Torson-Customizable-Three-Row-PU-Leather-Card-Game-Storage-Box-Removable-Lid-Table-Game-Waterproof-Durable-Eco-Friendly-Gaming.webp",
        "trailer": TRAILERS["tabletop"],
        "moq": "100 Pieces (MOQ)",
        "supplier": "Dongguan Tuoxiang Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Customisable tabletop or retail game suitable for branded merchandise, education, events and market-testing programmes.",
    },
    # 20 · PAGE 3
    {
        "slug": "gameroom-top-rated-adjustable-high-holding-electronic-fish-hun-020",
        "title": "Gameroom Top Rated Adjustable High Holding Electronic Fish Hunter Table Redemption Game",
        "genre": "Redemption Game",
        "platform": "Arcade / Redemption",
        "price": 15,
        "compare": 15,
        "image": "https://image.made-in-china.com/43f34j00fjHomekKEYcU/Gameroom-Top-Rated-Adjustable-High-Holding-Electronic-Fish-Hunter-Table-Redemption-Game.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Crazy Software Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial prize or redemption equipment designed for dependable venue operation and repeat customer engagement.",
    },
    # 21 · PAGE 3
    {
        "slug": "custom-outdoor-bocce-ball-set-outdoor-game-021",
        "title": "Custom Outdoor Bocce Ball Set, Outdoor Game",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 26.5,
        "compare": 29.5,
        "image": "https://image.made-in-china.com/43f34j00wtBbEfizYHWK/Custom-Outdoor-Bocce-Ball-Set-Outdoor-Game.webp",
        "trailer": TRAILERS["sports"],
        "moq": "500 Sets (MOQ)",
        "supplier": "TianChang Liangwen Sporting Equipment Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 22 · PAGE 3
    {
        "slug": "4x3m-inflatable-football-shooting-target-outdoor-shoot-out-gam-022",
        "title": "4X3m Inflatable Football Shooting Target Outdoor Shoot out Game Inflatable Soccer Shooting Goal Game",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 28,
        "compare": 45,
        "image": "https://image.made-in-china.com/43f34j00HvYWMVAtZbfO/4X3m-Inflatable-Football-Shooting-Target-Outdoor-Shoot-out-Game-Inflatable-Soccer-Shooting-Goal-Game.webp",
        "trailer": TRAILERS["sports"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Youdowell Trade Co.,Limited",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 23 · PAGE 3
    {
        "slug": "tv-video-somatosensory-game-console-fitness-and-parent-child-i-023",
        "title": "TV Video Somatosensory Game Console, Fitness and Parent-Child Interactive Entertainment, Christmas Gift",
        "genre": "Redemption Game",
        "platform": "Arcade / Redemption",
        "price": 59,
        "compare": 59,
        "image": "https://image.made-in-china.com/43f34j00TYGjNUphbJqK/TV-Video-Somatosensory-Game-Console-Fitness-and-Parent-Child-Interactive-Entertainment-Christmas-Gift.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Set (MOQ)",
        "supplier": "Jiangxi Hongtu Iot Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial prize or redemption equipment designed for dependable venue operation and repeat customer engagement.",
    },
    # 24 · PAGE 3
    {
        "slug": "factory-outlet-hot-sale-mario-taiwanesas-coin-operated-game-ma-024",
        "title": "Factory Outlet Hot Sale Mario Taiwanesas Coin Operated Game Machine Bonanza Machine",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 99,
        "compare": 100,
        "image": "https://image.made-in-china.com/43f34j00JDPCteczhQob/Factory-Outlet-Hot-Sale-Mario-Taiwanesas-Coin-Operated-Game-Machine-Bonanza-Machine.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "10 Sets (MOQ)",
        "supplier": "Jiangmen Huazhi Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 25 · PAGE 4
    {
        "slug": "wholesale-arcade-game-machine-magic-hammer-kiddie-hitting-game-025",
        "title": "Wholesale Arcade Game Machine Magic Hammer Kiddie Hitting Game Coin Operated Game Whack a Mole",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 100,
        "compare": 150,
        "image": "https://image.made-in-china.com/43f34j00kcRiVjbPbpYy/Wholesale-Arcade-Game-Machine-Magic-Hammer-Kiddie-Hitting-Game-Coin-Operated-Game-Whack-a-Mole.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Colorful Park Animation Technology Co., Ltd",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 26 · PAGE 4
    {
        "slug": "cheap-amusement-park-coin-operated-game-toy-vending-arcade-cra-026",
        "title": "Cheap Amusement Park Coin Operated Game Toy Vending Arcade Crane Game",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 200,
        "compare": 400,
        "image": "https://image.made-in-china.com/43f34j00tabBguZcHqoC/Cheap-Amusement-Park-Coin-Operated-Game-Toy-Vending-Arcade-Crane-Game.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 set (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 27 · PAGE 4
    {
        "slug": "funny-interesting-pvc-material-inflatable-tower-of-hanoi-for-t-027",
        "title": "Funny Interesting PVC Material Inflatable Tower of Hanoi for Team Building Games",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 251,
        "compare": 253,
        "image": "https://image.made-in-china.com/43f34j00WJgbFOyGMDcH/Funny-Interesting-PVC-Material-Inflatable-Tower-of-Hanoi-for-Team-Building-Games.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Huayue Inflatable Products Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 28 · PAGE 4
    {
        "slug": "hot-sell-mini-arcade-pac-man-pandora-s-box-taito-vewlix-l-cabi-028",
        "title": "Hot Sell Mini Arcade PAC Man Pandora's Box Taito Vewlix-L Cabinet Game Machine",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 288,
        "compare": 288,
        "image": "https://image.made-in-china.com/43f34j00nPUYfktbIaoV/Hot-Sell-Mini-Arcade-PAC-Man-Pandora-s-Box-Taito-Vewlix-L-Cabinet-Game-Machine.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "10 Pieces (MOQ)",
        "supplier": "Guangzhou Yuehong Electronics Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 29 · PAGE 4
    {
        "slug": "42-paradise-lost-sharpshooter-gun-shooting-simulator-game-vide-029",
        "title": "42\" Paradise Lost Sharpshooter Gun Shooting Simulator Game Video Arcade Game",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 300,
        "compare": 300,
        "image": "https://image.made-in-china.com/43f34j00jeVcwPEgYtbT/42-Paradise-Lost-Sharpshooter-Gun-Shooting-Simulator-Game-Video-Arcade-Game.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 set (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 30 · PAGE 4
    {
        "slug": "amusement-park-coin-operated-cola-cabinet-prize-gift-arcade-ki-030",
        "title": "Amusement Park Coin Operated Cola Cabinet Prize Gift Arcade Kids Game",
        "genre": "Redemption Game",
        "platform": "Arcade / Redemption",
        "price": 350,
        "compare": 350,
        "image": "https://image.made-in-china.com/43f34j00vtseASWGGjbd/Amusement-Park-Coin-Operated-Cola-Cabinet-Prize-Gift-Arcade-Kids-Game.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 set (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial prize or redemption equipment designed for dependable venue operation and repeat customer engagement.",
    },
    # 31 · PAGE 4
    {
        "slug": "factory-directly-sale-fire-link-multi-skill-game-arcade-games-031",
        "title": "Factory Directly Sale Fire Link Multi Skill Game Arcade Games Board",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 370,
        "compare": 400,
        "image": "https://image.made-in-china.com/43f34j00MQtCkaDzIeqT/Factory-Directly-Sale-Fire-Link-Multi-Skill-Game-Arcade-Games-Board.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Miracle Intelligent Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 32 · PAGE 4
    {
        "slug": "hot-sale-interesting-2-player-arcade-table-game-fast-eye-games-032",
        "title": "Hot Sale Interesting 2 Player Arcade Table Game Fast Eye Games Coin Operated Beat Button Gaming Equipment",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 399,
        "compare": 399,
        "image": "https://image.made-in-china.com/43f34j00vGZetFlWnjbE/Hot-Sale-Interesting-2-Player-Arcade-Table-Game-Fast-Eye-Games-Coin-Operated-Beat-Button-Gaming-Equipment.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 pieces (MOQ)",
        "supplier": "Guangzhou Funspace Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 33 · PAGE 5
    {
        "slug": "commercial-8m-x-5m-inflatable-human-soccer-pool-table-game-for-033",
        "title": "Commercial 8m X 5m Inflatable Human Soccer Pool Table Game for Events",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 400,
        "compare": 450,
        "image": "https://image.made-in-china.com/43f34j00KtikaVEPOqhM/Commercial-8m-X-5m-Inflatable-Human-Soccer-Pool-Table-Game-for-Events.webp",
        "trailer": TRAILERS["sports"],
        "moq": "1 Piece (MOQ)",
        "supplier": "ZHONGSHAN TH TOYS LIMITED",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 34 · PAGE 5
    {
        "slug": "inflatable-4-spot-tic-tac-toe-carnival-entertainment-game-with-034",
        "title": "Inflatable 4 Spot Tic Tac Toe Carnival Entertainment Game with Free Blower for Outdoor Activities",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 450,
        "compare": 500,
        "image": "https://image.made-in-china.com/43f34j00CMqVckrgauUz/Inflatable-4-Spot-Tic-Tac-Toe-Carnival-Entertainment-Game-with-Free-Blower-for-Outdoor-Activities.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Youdowell Trade Co.,Limited",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 35 · PAGE 5
    {
        "slug": "cute-hammer-amusement-entertainment-equipment-coin-operated-ga-035",
        "title": "Cute Hammer Amusement Entertainment Equipment Coin Operated Game",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 500,
        "compare": 500,
        "image": "https://image.made-in-china.com/43f34j00kDroqhzWLwcJ/Cute-Hammer-Amusement-Entertainment-Equipment-Coin-Operated-Game.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 set (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 36 · PAGE 5
    {
        "slug": "buffalo-skill-game-pcb-chinese-game-board-for-coin-operated-ma-036",
        "title": "Buffalo Skill Game PCB Chinese Game Board for Coin Operated Machine",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 600,
        "compare": 600,
        "image": "https://image.made-in-china.com/43f34j00YemWFgyDMNRC/Buffalo-Skill-Game-PCB-Chinese-Game-Board-for-Coin-Operated-Machine.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Miracle Intelligent Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 37 · PAGE 5
    {
        "slug": "usa-new-high-quality-55-inch-8-players-fish-hunter-casino-mach-037",
        "title": "USA New High Quality 55 Inch 8 Players Fish Hunter Casino Machine Game Board Thunder Dragon",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 600,
        "compare": 600,
        "image": "https://image.made-in-china.com/43f34j00cqBbKMLEftoJ/USA-New-High-Quality-55-Inch-8-Players-Fish-Hunter-Casino-Machine-Game-Board-Thunder-Dragon.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Crazy Software Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 38 · PAGE 5
    {
        "slug": "pcb-game-board-firelink-triple-nova-for-coin-operated-game-cen-038",
        "title": "PCB Game Board Firelink Triple Nova for Coin-Operated Game Centers",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 660,
        "compare": 688,
        "image": "https://image.made-in-china.com/43f34j00VAKMuDJrwycW/PCB-Game-Board-Firelink-Triple-Nova-for-Coin-Operated-Game-Centers.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Miracle Intelligent Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 39 · PAGE 5
    {
        "slug": "high-quality-lcd-alien-shooting-game-for-family-entertainment-039",
        "title": "High-Quality LCD Alien Shooting Game for Family Entertainment",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 700,
        "compare": 800,
        "image": "https://image.made-in-china.com/43f34j00ensctTQEOvzV/High-Quality-LCD-Alien-Shooting-Game-for-Family-Entertainment.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Dinibao Animation Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 40 · PAGE 5
    {
        "slug": "interactive-airplane-arcade-game-for-engaging-children-s-play-040",
        "title": "Interactive Airplane Arcade Game for Engaging Children's Play",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 799,
        "compare": 799,
        "image": "https://image.made-in-china.com/43f34j00DJoqmduRlErA/Interactive-Airplane-Arcade-Game-for-Engaging-Children-s-Play.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Dinibao Animation Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 41 · PAGE 6
    {
        "slug": "aurora-coin-operated-hockey-arcade-game-for-fun-play-041",
        "title": "Aurora Coin Operated Hockey Arcade Game for Fun Play",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 800,
        "compare": 900,
        "image": "https://image.made-in-china.com/43f34j00CJQbvPwaYEzU/Aurora-Coin-Operated-Hockey-Arcade-Game-for-Fun-Play.webp",
        "trailer": TRAILERS["sports"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Dinibao Animation Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 42 · PAGE 6
    {
        "slug": "high-profit-screen-operation-skills-coin-game-video-arcade-gra-042",
        "title": "High Profit Screen Operation Skills Coin Game Video Arcade Grand Prize Fruit Mario Wheel Machine Cabinet Customized Entertainment Equipment",
        "genre": "Redemption Game",
        "platform": "Arcade / Redemption",
        "price": 803,
        "compare": 1013,
        "image": "https://image.made-in-china.com/43f34j00JAgCTsByPicK/High-Profit-Screen-Operation-Skills-Coin-Game-Video-Arcade-Grand-Prize-Fruit-Mario-Wheel-Machine-Cabinet-Customized-Entertainment-Equipment.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Shenzhen LCDKIOSK Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial prize or redemption equipment designed for dependable venue operation and repeat customer engagement.",
    },
    # 43 · PAGE 6
    {
        "slug": "funspace-indoor-electronic-basketball-arcade-game-machine-043",
        "title": "Funspace Indoor Electronic Basketball Arcade Game Machine",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 899,
        "compare": 999,
        "image": "https://image.made-in-china.com/202f0j00HYPehiVzhwoI/Funspace-Factory-Price-Adult-Indoor-Electronic-Adult-Indoor-Electronic-Basketball-Arcade-Game-Machine.webp",
        "trailer": TRAILERS["sports"],
        "moq": "1 Set (MOQ)",
        "supplier": "Guangzhou Funspace Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial coin-operated basketball shooting game designed for arcades, family entertainment centres and indoor amusement venues.",
    },
    # 44 · PAGE 6
    {
        "slug": "newest-popular-favourable-price-3-players-fishing-game-shootin-044",
        "title": "Newest Popular Favourable Price 3 Players Fishing Game Shooting Buttons Fish Table Arcade Game Machines Ocean King 3 Plus Lucky Link",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 900,
        "compare": 1500,
        "image": "https://image.made-in-china.com/43f34j00mvpbTEwgnNor/Newest-Popular-Favourable-Price-3-Players-Fishing-Game-Shooting-Buttons-Fish-Table-Arcade-Game-Machines-Ocean-King-3-Plus-Lucky-Link.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Crazy Software Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 45 · PAGE 6
    {
        "slug": "arcade-gaming-air-hockey-table-game-indoor-amusement-park-coin-045",
        "title": "Arcade Gaming Air Hockey Table Game Indoor Amusement Park Coin Operated Game",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 1000,
        "compare": 1200,
        "image": "https://image.made-in-china.com/43f34j00JWvCKzqnPVbs/Arcade-Gaming-Air-Hockey-Table-Game-Indoor-Amusement-Park-Coin-Operated-Game.webp",
        "trailer": TRAILERS["sports"],
        "moq": "1 pieces (MOQ)",
        "supplier": "Guangzhou Yifeng Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 46 · PAGE 6
    {
        "slug": "commercial-inflatable-interactive-game-adults-sport-inflatable-046",
        "title": "Commercial Inflatable Interactive Game Adults Sport Inflatable IPS Football Game",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 1150,
        "compare": 1180,
        "image": "https://image.made-in-china.com/43f34j00pIFvnzeMZtoR/Commercial-Inflatable-Interactive-Game-Adults-Sport-Inflatable-IPS-Football-Game.webp",
        "trailer": TRAILERS["sports"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Huayue Inflatable Products Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 47 · PAGE 6
    {
        "slug": "scooter-hero-amusement-park-kids-game-machine-arcade-running-g-047",
        "title": "Scooter Hero Amusement Park Kids Game Machine Arcade Running Game",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 1200,
        "compare": 1200,
        "image": "https://image.made-in-china.com/43f34j00qcRoEesGaWbY/Scooter-Hero-Amusement-Park-Kids-Game-Machine-Arcade-Running-Game.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 set (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 48 · PAGE 6
    {
        "slug": "skating-game-machine-master-skateboard-indoor-coin-video-arcad-048",
        "title": "Skating Game Machine Master Skateboard Indoor Coin Video Arcade Game",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 1480,
        "compare": 1480,
        "image": "https://image.made-in-china.com/43f34j00rqTkCMsEHVoI/Skating-Game-Machine-Master-Skateboard-Indoor-Coin-Video-Arcade-Game.webp",
        "trailer": TRAILERS["sports"],
        "moq": "1 set (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 49 · PAGE 7
    {
        "slug": "racing-ff-moto-dinibao-arcade-game-049",
        "title": "Racing FF Moto Dinibao Arcade Game",
        "genre": "Racing Simulator",
        "platform": "Arcade / Racing",
        "price": 1500,
        "compare": 1500,
        "image": "https://image.made-in-china.com/43f34j00TFRcGnMlZqgs/Racing-FF-Moto-Dinibao-Arcade-Game.webp",
        "trailer": TRAILERS["racing"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Dinibao Animation Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial driving and racing simulator designed for high-engagement play in arcades and family entertainment centres.",
    },
    # 50 · PAGE 7
    {
        "slug": "sleek-designs-cash-ticket-redemption-kiosks-skill-game-machine-050",
        "title": "Sleek Designs Cash Ticket Redemption Kiosks Skill Game Machine Prize Sports Games",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 1600,
        "compare": 2000,
        "image": "https://image.made-in-china.com/43f34j00fdvceEhWZnup/Sleek-Designs-Cash-Ticket-Redemption-Kiosks-Skill-Game-Machine-Prize-Sports-Games.webp",
        "trailer": TRAILERS["sports"],
        "moq": "1 units (MOQ)",
        "supplier": "Fuzhou Tita Technologies Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 51 · PAGE 7
    {
        "slug": "vibrant-rainbow-ball-arcade-game-for-ticket-redemption-051",
        "title": "Vibrant Rainbow Ball Arcade Game for Ticket Redemption",
        "genre": "Redemption Game",
        "platform": "Arcade / Redemption",
        "price": 1800,
        "compare": 1900,
        "image": "https://image.made-in-china.com/43f34j00oqEVuCgzarBe/Vibrant-Rainbow-Ball-Arcade-Game-for-Ticket-Redemption.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Dinibao Animation Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial prize or redemption equipment designed for dependable venue operation and repeat customer engagement.",
    },
    # 52 · PAGE 7
    {
        "slug": "coin-operated-indoor-ice-knight-water-shooting-machines-zombie-052",
        "title": "Coin Operated Indoor Ice Knight Water Shooting Machines Zombies Water Machine Video Arcade Games for Sale",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 1980,
        "compare": 2120,
        "image": "https://image.made-in-china.com/43f34j00ZGrCmafFbQke/Coin-Operated-Indoor-Ice-Knight-Water-Shooting-Machines-Zombies-Water-Machine-Video-Arcade-Games-for-Sale.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Xiao Tong Yao Amusement Equipment Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 53 · PAGE 7
    {
        "slug": "fun-filled-pirate-shooting-adventure-game-for-game-rooms-053",
        "title": "Fun-Filled Pirate Shooting Adventure Game for Game Rooms",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 2100,
        "compare": 2200,
        "image": "https://image.made-in-china.com/43f34j00uevMBmjapAkC/Fun-Filled-Pirate-Shooting-Adventure-Game-for-Game-Rooms.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Dinibao Animation Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 54 · PAGE 7
    {
        "slug": "cartoon-air-taxi-theme-paren-child-coin-operated-kids-ride-gam-054",
        "title": "Cartoon Air Taxi Theme Paren-Child Coin Operated Kids Ride Game Machine for Game City",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 2399,
        "compare": 2699,
        "image": "https://image.made-in-china.com/43f34j00eaiMpwmIMScq/Cartoon-Air-Taxi-Theme-Paren-Child-Coin-Operated-Kids-Ride-Game-Machine-for-Game-City.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 sets (MOQ)",
        "supplier": "Guangzhou Funspace Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 55 · PAGE 7
    {
        "slug": "herovr-indoor-esports-online-team-battle-unattended-vr-shootin-055",
        "title": "Herovr Indoor Esports Online Team Battle Unattended Vr Shooting Arcade Game Machine for Adults",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 2680,
        "compare": 2980,
        "image": "https://image.made-in-china.com/43f34j00mbVeKnuCeBqN/Herovr-Indoor-Esports-Online-Team-Battle-Unattended-Vr-Shooting-Arcade-Game-Machine-for-Adults.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Xiechuang Culture Media Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Immersive commercial entertainment system suited to premium attractions, malls and professionally managed gaming venues.",
    },
    # 56 · PAGE 7
    {
        "slug": "high-end-customized-arcade-game-consoles-with-built-in-multipl-056",
        "title": "High End Customized Arcade Game Consoles with Built-in Multiple Games",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 2999,
        "compare": 2999,
        "image": "https://image.made-in-china.com/43f34j00SAqWjEsbLGYK/High-End-Customized-Arcade-Game-Consoles-with-Built-in-Multiple-Games.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Set (MOQ)",
        "supplier": "Guangzhou Big Whale Amusement Equipment Co. Ltd",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 57 · PAGE 8
    {
        "slug": "pirate-treasure-shooting-arcade-coin-operation-game-ticket-red-057",
        "title": "Pirate Treasure Shooting Arcade Coin Operation Game Ticket Redemption",
        "genre": "Redemption Game",
        "platform": "Arcade / Redemption",
        "price": 3000,
        "compare": 3400,
        "image": "https://image.made-in-china.com/43f34j00RAGblnJzLhgO/Pirate-Treasure-Shooting-Arcade-Coin-Operation-Game-Ticket-Redemption.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Dinibao Animation Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial prize or redemption equipment designed for dependable venue operation and repeat customer engagement.",
    },
    # 58 · PAGE 8
    {
        "slug": "saio-interactive-ar-software-ladar-for-mobile-education-50-sen-058",
        "title": "Saio Interactive Ar Software+Ladar for Mobile Education 50+ Sensory Ground Projection Games Fitness Training Kids Game System",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 3080,
        "compare": 3190,
        "image": "https://image.made-in-china.com/43f34j00tEljySWanNqb/Saio-Interactive-Ar-Software-Ladar-for-Mobile-Education-50-Sensory-Ground-Projection-Games-Fitness-Training-Kids-Game-System.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Onecraze Media Limited",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 59 · PAGE 8
    {
        "slug": "indoor-coin-operated-arcade-game-pumpkin-party-ball-tossing-ma-059",
        "title": "Indoor Coin-Operated Arcade Game: \"Pumpkin Party\" Ball-Tossing Machine",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 3250,
        "compare": 3550,
        "image": "https://image.made-in-china.com/43f34j00MQWZGoFJyjqv/Indoor-Coin-Operated-Arcade-Game-Pumpkin-Party-Ball-Tossing-Machine.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Shanghaojia Electronic Technology Co., Ltd",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 60 · PAGE 8
    {
        "slug": "virtual-reality-entertainment-9d-vr-racing-simulator-machine-t-060",
        "title": "Virtual Reality Entertainment 9d Vr Racing Simulator Machine Three Screen Three Axis Racing Car Game",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 3500,
        "compare": 3500,
        "image": "https://image.made-in-china.com/43f34j00DoCcqywtlIbk/Virtual-Reality-Entertainment-9d-Vr-Racing-Simulator-Machine-Three-Screen-Three-Axis-Racing-Car-Game.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 set (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Immersive commercial entertainment system suited to premium attractions, malls and professionally managed gaming venues.",
    },
    # 61 · PAGE 8
    {
        "slug": "3-player-horse-racing-arcade-game-coin-operated-speed-horse-si-061",
        "title": "3 Player Horse Racing Arcade Game Coin Operated Speed Horse Simulator for Amusement Parks",
        "genre": "Racing Simulator",
        "platform": "Arcade / Racing",
        "price": 4000,
        "compare": 4685,
        "image": "https://image.made-in-china.com/43f34j00vlVCyisocAqS/3-Player-Horse-Racing-Arcade-Game-Coin-Operated-Speed-Horse-Simulator-for-Amusement-Parks.webp",
        "trailer": TRAILERS["racing"],
        "moq": "1 piece (MOQ)",
        "supplier": "Guangzhou Ama Amusement Equipment Co, . Ltd",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial driving and racing simulator designed for high-engagement play in arcades and family entertainment centres.",
    },
    # 62 · PAGE 8
    {
        "slug": "vart-popular-indoor-ball-throwing-game-machine-coin-operated-h-062",
        "title": "Vart Popular Indoor Ball Throwing Game Machine Coin Operated Hungry Shark Arcade Game for Kids Playground Amusement Park",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 4700,
        "compare": 4700,
        "image": "https://image.made-in-china.com/43f34j00RksWHgQrYzvA/Vart-Popular-Indoor-Ball-Throwing-Game-Machine-Coin-Operated-Hungry-Shark-Arcade-Game-for-Kids-Playground-Amusement-Park.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Longcheng Electronics Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 63 · PAGE 8
    {
        "slug": "fighter-jet-arcade-game-for-dynamic-air-combat-excitement-063",
        "title": "Fighter Jet Arcade Game for Dynamic Air Combat Excitement",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 4706,
        "compare": 5118,
        "image": "https://image.made-in-china.com/43f34j00ltaZzWGygwbr/Fighter-Jet-Arcade-Game-for-Dynamic-Air-Combat-Excitement.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Mei Yi Lian Anime Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 64 · PAGE 8
    {
        "slug": "vart-ar-light-chasing-party-interactive-floor-projection-game-064",
        "title": "Vart Ar Light Chasing Party Interactive Floor Projection Game for Indoor Playground",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 5200,
        "compare": 5200,
        "image": "https://image.made-in-china.com/43f34j00PmOVpzSnEvGt/Vart-Ar-Light-Chasing-Party-Interactive-Floor-Projection-Game-for-Indoor-Playground.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Longcheng Electronics Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 65 · PAGE 9
    {
        "slug": "fast-shooter-exciting-shooting-game-arcade-game-with-gun-065",
        "title": "Fast Shooter Exciting Shooting Game Arcade Game with Gun",
        "genre": "Arcade Game",
        "platform": "Arcade / Commercial",
        "price": 6000,
        "compare": 6100,
        "image": "https://image.made-in-china.com/43f34j00GESoLBpsYqca/Fast-Shooter-Exciting-Shooting-Game-Arcade-Game-with-Gun.webp",
        "trailer": TRAILERS["arcade"],
        "moq": "1 set (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial amusement product suited to arcades, family entertainment centres, malls and leisure venues.",
    },
    # 66 · PAGE 9
    {
        "slug": "the-racing-god-hot-sale-coin-operated-moto-racing-game-for-chi-066",
        "title": "The Racing God Hot Sale Coin Operated Moto Racing Game for Children Playground",
        "genre": "Racing Simulator",
        "platform": "Arcade / Racing",
        "price": 6800,
        "compare": 6900,
        "image": "https://image.made-in-china.com/43f34j00KTCMsSVJygpN/The-Racing-God-Hot-Sale-Coin-Operated-Moto-Racing-Game-for-Children-Playground.webp",
        "trailer": TRAILERS["racing"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Dinibao Animation Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial driving and racing simulator designed for high-engagement play in arcades and family entertainment centres.",
    },
    # 67 · PAGE 9
    {
        "slug": "htc-9d-vr-battle-shooting-gun-simulator-virtual-reality-game-f-067",
        "title": "HTC 9d Vr Battle Shooting Gun Simulator/Virtual Reality Game for Sale",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 6850,
        "compare": 6850,
        "image": "https://image.made-in-china.com/43f34j00gaTktBLWTzbD/HTC-9d-Vr-Battle-Shooting-Gun-Simulator-Virtual-Reality-Game-for-Sale.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Immersive commercial entertainment system suited to premium attractions, malls and professionally managed gaming venues.",
    },
    # 68 · PAGE 9
    {
        "slug": "shopping-mall-popular-simulator-game-coin-operated-curve-drift-068",
        "title": "Shopping Mall Popular Simulator Game Coin Operated Curve Drift Car Game",
        "genre": "Racing Simulator",
        "platform": "Arcade / Racing",
        "price": 7400,
        "compare": 8200,
        "image": "https://image.made-in-china.com/43f34j00mWneIAsJtiqv/Shopping-Mall-Popular-Simulator-Game-Coin-Operated-Curve-Drift-Car-Game.webp",
        "trailer": TRAILERS["racing"],
        "moq": "1 set (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial driving and racing simulator designed for high-engagement play in arcades and family entertainment centres.",
    },
    # 69 · PAGE 9
    {
        "slug": "new-three-axis-three-screen-racing-car-360-degree-car-train-dr-069",
        "title": "New Three-Axis Three-Screen Racing Car 360 Degree Car Train Driving Simulator Race Game",
        "genre": "Racing Simulator",
        "platform": "Arcade / Racing",
        "price": 7800,
        "compare": 8500,
        "image": "https://image.made-in-china.com/43f34j00dvZqHVlhwFbW/New-Three-Axis-Three-Screen-Racing-Car-360-Degree-Car-Train-Driving-Simulator-Race-Game.webp",
        "trailer": TRAILERS["racing"],
        "moq": "1 set (MOQ)",
        "supplier": "Guangzhou EPARK Electronic Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial driving and racing simulator designed for high-engagement play in arcades and family entertainment centres.",
    },
    # 70 · PAGE 9
    {
        "slug": "immersive-dynamic-basketball-indoor-cyber-dunk-reality-interac-070",
        "title": "Immersive Dynamic Basketball Indoor Cyber Dunk Reality Interactive Projection Games for Gymnasium",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 8140,
        "compare": 8250,
        "image": "https://image.made-in-china.com/43f34j00iGcZyoaqEpkN/Immersive-Dynamic-Basketball-Indoor-Cyber-Dunk-Reality-Interactive-Projection-Games-for-Gymnasium.webp",
        "trailer": TRAILERS["sports"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Onecraze Media Limited",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 71 · PAGE 9
    {
        "slug": "indoor-interactive-projection-golf-simulator-game-machine-071",
        "title": "Indoor Interactive Projection Golf Simulator Game Machine",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 9000,
        "compare": 9800,
        "image": "https://image.made-in-china.com/43f34j00LoQebDrcZhkd/Indoor-Interactive-Projection-Golf-Simulator-Game-Machine.webp",
        "trailer": TRAILERS["sports"],
        "moq": "1 units (MOQ)",
        "supplier": "Liangjia Sports Technology (Guangzhou) Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 72 · PAGE 9
    {
        "slug": "vart-vr-games-theme-park-9d-virtual-reality-room-for-sale-072",
        "title": "Vart Vr Games Theme Park 9d Virtual Reality Room for Sale",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 9900,
        "compare": 9900,
        "image": "https://image.made-in-china.com/43f34j00BnZcEQeROtqT/Vart-Vr-Games-Theme-Park-9d-Virtual-Reality-Room-for-Sale.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Longcheng Electronics Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Immersive commercial entertainment system suited to premium attractions, malls and professionally managed gaming venues.",
    },
    # 73 · PAGE 10
    {
        "slug": "earn-money-amusement-park-games-virtual-reality-game-073",
        "title": "Earn Money Amusement Park Games Virtual Reality Game",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 10000,
        "compare": 10000,
        "image": "https://image.made-in-china.com/43f34j00cJtWCHDPhBRi/Earn-Money-Amusement-Park-Games-Virtual-Reality-Game.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Longcheng Electronics Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Immersive commercial entertainment system suited to premium attractions, malls and professionally managed gaming venues.",
    },
    # 74 · PAGE 10
    {
        "slug": "vart-9d-vr-fighting-gun-games-shooting-virtual-reality-simulat-074",
        "title": "Vart 9d Vr Fighting Gun Games Shooting Virtual Reality Simulation for 2 Players",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 10000,
        "compare": 10000,
        "image": "https://image.made-in-china.com/43f34j00nvVWDRjaaLUH/Vart-9d-Vr-Fighting-Gun-Games-Shooting-Virtual-Reality-Simulation-for-2-Players.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Longcheng Electronics Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Immersive commercial entertainment system suited to premium attractions, malls and professionally managed gaming venues.",
    },
    # 75 · PAGE 10
    {
        "slug": "vr-attack-shooting-game-simulator-2-players-amusement-game-equ-075",
        "title": "Vr Attack Shooting Game Simulator 2 Players Amusement Game Equipment",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 10200,
        "compare": 10200,
        "image": "https://image.made-in-china.com/43f34j00QmeBPdKGykcZ/Vr-Attack-Shooting-Game-Simulator-2-Players-Amusement-Game-Equipment.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Zhuoyuan Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Immersive commercial entertainment system suited to premium attractions, malls and professionally managed gaming venues.",
    },
    # 76 · PAGE 10
    {
        "slug": "compact-indoor-mini-bowling-game-set-for-family-fun-076",
        "title": "Compact Indoor Mini Bowling Game Set for Family Fun",
        "genre": "Sports Game",
        "platform": "Sports / Recreation",
        "price": 10800,
        "compare": 11800,
        "image": "https://image.made-in-china.com/43f34j00cGEKVCFnwmke/Compact-Indoor-Mini-Bowling-Game-Set-for-Family-Fun.webp",
        "trailer": TRAILERS["sports"],
        "moq": "2 lanes (MOQ)",
        "supplier": "Beijing Red Sun Bowling Technology Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Interactive sports-entertainment product suitable for recreation venues, events and activity-based leisure businesses.",
    },
    # 77 · PAGE 10
    {
        "slug": "snipe-warrior-stand-best-vr-shooting-arcade-games-simulator-co-077",
        "title": "Snipe Warrior Stand Best Vr Shooting Arcade Games Simulator Coin Operated Game",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 12600,
        "compare": 14600,
        "image": "https://image.made-in-china.com/43f34j00ZkNevqBKQabc/Snipe-Warrior-Stand-Best-Vr-Shooting-Arcade-Games-Simulator-Coin-Operated-Game.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Zhuoyuan Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Immersive commercial entertainment system suited to premium attractions, malls and professionally managed gaming venues.",
    },
    # 78 · PAGE 10
    {
        "slug": "driving-with-electric-machines-games-078",
        "title": "Driving with Electric Machines Games",
        "genre": "Racing Simulator",
        "platform": "Arcade / Racing",
        "price": 12700,
        "compare": 12700,
        "image": "https://image.made-in-china.com/43f34j00gOFcknbEQyov/Driving-with-Electric-Machines-Games.webp",
        "trailer": TRAILERS["racing"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Longcheng Electronics Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Commercial driving and racing simulator designed for high-engagement play in arcades and family entertainment centres.",
    },
    # 79 · PAGE 10
    {
        "slug": "vart-vr-arena-multiplayer-shooting-game-commercial-vr-entertai-079",
        "title": "Vart Vr Arena Multiplayer Shooting Game Commercial Vr Entertainment Equipment",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 16800,
        "compare": 16800,
        "image": "https://image.made-in-china.com/43f34j00lJbWjkcdSoUH/Vart-Vr-Arena-Multiplayer-Shooting-Game-Commercial-Vr-Entertainment-Equipment.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Guangzhou Longcheng Electronics Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Immersive commercial entertainment system suited to premium attractions, malls and professionally managed gaming venues.",
    },
    # 80 · PAGE 10
    {
        "slug": "vr-amusement-money-making-equipment-vr-shooting-arcade-machine-080",
        "title": "Vr Amusement Money Making Equipment Vr Shooting Arcade Machine Game Virtual Reality",
        "genre": "VR Simulator",
        "platform": "Arcade / VR",
        "price": 19000,
        "compare": 20000,
        "image": "https://image.made-in-china.com/43f34j00hoBeJOwndAqE/Vr-Amusement-Money-Making-Equipment-Vr-Shooting-Arcade-Machine-Game-Virtual-Reality.webp",
        "trailer": TRAILERS["vr"],
        "moq": "1 Piece (MOQ)",
        "supplier": "Zhuoyuan Co., Ltd.",
        "source": "Made-in-China product listing",
        "region": "China",
        "summary": "Immersive commercial entertainment system suited to premium attractions, malls and professionally managed gaming venues.",
    },
]

def _duplicates(values):
    seen = set()
    return {value for value in values if value in seen or seen.add(value)}


def validate_seed_data():
    """Fail before database changes if catalogue integrity is compromised."""

    expected = PAGE_SIZE * PAGE_COUNT
    if len(GAME_DATA) != expected:
        raise ValueError(f"Expected {expected} games for ten 8-product pages; received {len(GAME_DATA)}")

    required_fields = {
        "slug",
        "title",
        "genre",
        "platform",
        "price",
        "compare",
        "image",
        "trailer",
        "moq",
        "supplier",
        "source",
        "region",
        "summary",
    }
    for position, item in enumerate(GAME_DATA, start=1):
        missing = required_fields.difference(item)
        if missing:
            raise ValueError(
                f"Game {position} is missing required fields: {sorted(missing)}"
            )

        empty = sorted(
            key for key in required_fields if not str(item[key]).strip()
        )
        if empty:
            raise ValueError(f"Game {position} has empty fields: {empty}")

    checks = {
        "game slugs": [item["slug"] for item in GAME_DATA],
        "game images": [item["image"] for item in GAME_DATA],
    }
    for label, values in checks.items():
        repeated = _duplicates(values)
        if repeated:
            raise ValueError(f"Duplicate {label}: {sorted(repeated)}")

    prices = [Decimal(str(item["price"])) for item in GAME_DATA]
    compare_prices = [Decimal(str(item["compare"])) for item in GAME_DATA]
    if any(price <= 0 for price in prices):
        raise ValueError("Every game must have a positive price")
    if any(compare < price for price, compare in zip(prices, compare_prices)):
        raise ValueError("A compare price cannot be lower than its selling price")
    if prices != sorted(prices):
        raise ValueError("Game prices must be in non-decreasing catalogue order")
    if prices[-1] < Decimal("10000") or prices[-1] > Decimal("20000"):
        raise ValueError("Page 10 must finish within the US$10,000–US$20,000 range")


def seed_catalogue():
    """Upsert the gaming catalogue and deactivate all non-catalogue products."""

    validate_seed_data()

    try:
        catalogue_slugs = [item["slug"] for item in GAME_DATA]

        games_deactivated = (
            Game.query.filter(Game.is_active.is_(True))
            .filter(~Game.slug.in_(catalogue_slugs))
            .update({Game.is_active: False}, synchronize_session=False)
        )

        for index, item in enumerate(GAME_DATA):
            game = Game.query.filter_by(slug=item["slug"]).first()
            if game is None:
                game = Game(slug=item["slug"])
                db.session.add(game)

            game.title = item["title"]
            game.genre = item["genre"]
            game.platform = item["platform"]
            game.edition = "Commercial Supply"
            game.region = item["region"]
            game.price = Decimal(str(item["price"]))
            game.compare_price = Decimal(str(item["compare"]))
            game.description = item["summary"]
            game.image_url = item["image"]
            game.trailer_url = item["trailer"]
            game.minimum_order = item["moq"]
            game.supplier = item["supplier"]
            game.photo_source = item["source"]
            game.stock_count = max(20, 200 - index)
            game.is_featured = index < PAGE_SIZE
            game.is_active = True

        commodities_deactivated = Commodity.query.filter_by(is_active=True).update(
            {Commodity.is_active: False}, synchronize_session=False
        )

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return {
        "games": len(GAME_DATA),
        "active_games": Game.query.filter_by(is_active=True).count(),
        "games_deactivated": games_deactivated,
        "commodities": 0,
        "commodities_deactivated": commodities_deactivated,
        "pages": PAGE_COUNT,
        "unique_game_images": len({item["image"] for item in GAME_DATA}),
    }
