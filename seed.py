from decimal import Decimal

from models import Commodity, Game, db

TRAILERS = {
    "vr": "https://videos.pexels.com/video-files/7774512/7774512-uhd_3840_2160_30fps.mp4",
    "arcade": "https://videos.pexels.com/video-files/7914936/7914936-hd_1920_1080_30fps.mp4",
    "racing": "https://videos.pexels.com/video-files/4291850/4291850-hd_1920_1080_30fps.mp4",
    "tabletop": "https://videos.pexels.com/video-files/17329650/17329650-hd_1920_1080_60fps.mp4",
}

GAME_DATA = [
    {"slug":"hologate-vr-arcade","title":"HOLOGATE Multiplayer VR Arena","genre":"VR Simulator","platform":"VR / Commercial","price":9500,"compare":11800,"image":"/static/images/home-media/immersive-vr-arena.jpg","trailer":TRAILERS["vr"],"moq":"1 Set (MOQ)","supplier":"FABS Immersive Systems","source":"HOLOGATE official product media","summary":"A room-scale commercial VR attraction for family entertainment centres, malls and professional gaming venues."},
    {"slug":"vr-360-motion-simulator","title":"Two-Seat 360° VR Motion Simulator","genre":"VR Simulator","platform":"Arcade / VR","price":19000,"compare":21000,"image":"/static/images/home-media/vr-360-simulator.webp","trailer":TRAILERS["vr"],"moq":"1 Set (MOQ)","supplier":"FABS Immersive Systems","source":"Manufacturer product media","summary":"A dual-seat 360-degree motion platform engineered for amusement parks, malls and professional VR venues."},
    {"slug":"commercial-racing-simulator","title":"Full-Size Commercial Racing Simulator","genre":"Racing Simulator","platform":"Arcade / Commercial","price":5800,"compare":7200,"image":"/static/images/home-media/commercial-racing-simulator.jpg","trailer":TRAILERS["racing"],"moq":"1 Set (MOQ)","supplier":"FABS Racing Technology","source":"LeChen Amusement product media","summary":"A complete force-feedback racing cockpit with commercial cabinet, adjustable seat, wheel, pedals and display."},
    {"slug":"air-hockey-arcade-table","title":"Two-Player Air Hockey Arcade Table","genre":"Table Game","platform":"Arcade / Recreation","price":1150,"compare":1450,"image":"/static/images/home-media/air-hockey-table.jpg","trailer":TRAILERS["arcade"],"moq":"1 Piece (MOQ)","supplier":"FABS Recreation Equipment","source":"Manufacturer product media","summary":"Commercial two-player air hockey with LED cabinet, digital scoring, high-output airflow and coin operation."},
    {"slug":"coin-operated-arcade-cabinet","title":"Coin-Operated Sports Arcade Cabinet","genre":"Arcade Game","platform":"Arcade / Commercial","price":800,"compare":960,"image":"/static/images/home-media/coin-operated-arcade.jpg","trailer":TRAILERS["arcade"],"moq":"1 Piece (MOQ)","supplier":"FABS Arcade Distribution","source":"Guangzhou Chenshou Electronic","summary":"A venue-ready coin-operated cabinet with dual-player controls, illuminated display and configurable graphics."},
    {"slug":"shooting-master-arcade","title":"Shooting Master Arcade Machine","genre":"Shooting Game","platform":"Arcade / Commercial","price":6800,"compare":8200,"image":"/static/images/home-media/shooting-master-arcade.jpg","trailer":TRAILERS["arcade"],"moq":"1 Piece (MOQ)","supplier":"FABS Arcade Distribution","source":"Uniana product media","summary":"A full-length commercial shooting attraction with rifle controller, illuminated cabinet and digital scoring."},
    {"slug":"interactive-basketball-arcade","title":"Interactive Basketball Arcade Machine","genre":"Sports Arcade","platform":"Arcade / Sports","price":3200,"compare":3950,"image":"/static/images/home-media/basketball-arcade.webp","trailer":TRAILERS["arcade"],"moq":"1 Piece (MOQ)","supplier":"FABS Recreation Equipment","source":"Manufacturer product media","summary":"A commercial basketball challenge machine with animated display, automatic ball return, scoring and LED cabinet."},
    {"slug":"dual-lane-bowling-arcade","title":"Dual-Lane Bowling Arcade Machine","genre":"Sports Arcade","platform":"Arcade / Sports","price":7200,"compare":8900,"image":"/static/images/home-media/bowling-arcade.jpg","trailer":TRAILERS["arcade"],"moq":"1 Set (MOQ)","supplier":"FABS Recreation Equipment","source":"Yugamemachine product media","summary":"A two-lane bowling attraction with animated displays, illuminated cabinet, scoring and ticket redemption."},
    {"slug":"adventure-board-game-oem","title":"OEM Adventure Board Game Manufacturing Set","genre":"Board Game","platform":"Tabletop","price":3.20,"compare":5.40,"image":"/static/images/home-media/adventure-board-game.jpg","trailer":TRAILERS["tabletop"],"moq":"500 Sets (MOQ)","supplier":"FABS Tabletop Manufacturing","source":"I Slay The Dragon product media","summary":"Complete OEM tabletop production with illustrated cards, tokens, rules and custom retail-box packaging."},
    {"slug":"custom-strategy-board-game","title":"Custom Printed Strategy Board Game Set","genre":"Board Game","platform":"Tabletop","price":2.10,"compare":3.80,"image":"/static/images/home-media/custom-strategy-board-game.jpg","trailer":TRAILERS["tabletop"],"moq":"200 Sets (MOQ)","supplier":"FABS Tabletop Manufacturing","source":"Manufacturer product media","summary":"Custom printed strategy game with cards, wooden tokens, game board and rigid retail packaging."},
    {"slug":"family-arcade-racing-twin","title":"Twin-Seat Family Arcade Racing System","genre":"Racing Simulator","platform":"Arcade / Commercial","price":10800,"compare":12800,"image":"/static/images/home-media/commercial-racing-simulator.jpg","trailer":TRAILERS["racing"],"moq":"1 Pair (MOQ)","supplier":"FABS Racing Technology","source":"LeChen Amusement product media","summary":"Linked twin-seat racing system for family entertainment centres with competitive multi-player configuration."},
    {"slug":"immersive-vr-venue-package","title":"Immersive VR Venue Starter Package","genre":"VR Simulator","platform":"VR / Commercial","price":24500,"compare":28900,"image":"/static/images/home-media/immersive-vr-arena.jpg","trailer":TRAILERS["vr"],"moq":"1 Venue Package (MOQ)","supplier":"FABS Immersive Systems","source":"HOLOGATE official product media","summary":"A structured starter package combining room-scale hardware, operator workflow and venue installation planning."},
]

COMMODITY_DATA = [
    ("bitumen","Bitumen","Road & construction","40/50, 60/70, 80/100, PMB","500 MT"),
    ("tmt-bars","TMT Reinforcement Bars","Steel products","Multiple grades and diameters","100 MT"),
    ("steel-angles","Steel Angles","Steel products","Equal and unequal angles","50 MT"),
    ("z-purlins","Z Purlins","Steel products","Project-specific dimensions","50 MT"),
    ("black-pipes","Black Steel Pipes","Steel products","Welded and seamless","50 MT"),
    ("i-beams","I-Beams","Structural steel","Multiple profiles","100 MT"),
    ("channels","Steel Channels","Structural steel","U and C profiles","50 MT"),
    ("chequered-plates","Chequered Plates","Steel plates","Multiple thicknesses","50 MT"),
    ("steel-plates","Steel Plates","Steel products","Commercial and project grades","100 MT"),
    ("expanded-metal","Expanded Metal","Fabricated steel","Multiple mesh sizes","20 MT"),
    ("weld-mesh","Weld Mesh","Fabricated steel","Multiple wire gauges","20 MT"),
    ("brc-mesh","BRC Mesh","Construction steel","Standard sheets and rolls","50 MT"),
    ("nails","Construction Nails","Fasteners","Multiple lengths and gauges","20 MT"),
    ("hollow-sections","Hollow Sections","Structural steel","Square and rectangular","50 MT"),
    ("base-oil","Virgin & RC Base Oil","Base oils","SN grades and re-refined","100 MT"),
    ("rpo","Rubber Process Oil","Process oils","Aromatic and treated","100 MT"),
    ("carbon-black","Carbon Black","Performance materials","N-series grades","25 MT"),
    ("caustic-soda","Caustic Soda Flakes","Industrial chemicals","98–99%","25 MT"),
]


def seed_catalogue():
    for index, item in enumerate(GAME_DATA):
        game = Game.query.filter_by(slug=item["slug"]).first()
        if not game:
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
        if not commodity:
            commodity = Commodity(slug=slug)
            db.session.add(commodity)
        commodity.name = name
        commodity.category = category
        commodity.grade = grade
        commodity.minimum_order = moq
        commodity.unit = "Metric tonne"
        commodity.incoterms = "EXW · FOB · CFR · CIF"
        commodity.description = f"{name} supplied against confirmed specification, volume, destination and commercial terms."
        commodity.applications = "Industrial processing|Manufacturing|Project supply"
        commodity.image_url = commodity_image
        commodity.is_active = True
    db.session.commit()
