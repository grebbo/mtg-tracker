from app import db

PLAYERS = ['Daniele', 'Enrico', 'Federico', 'Lorenzo', 'Semir', 'Simone']

INITIAL_COMMANDERS = [
    ('Abdel', 'WU'), ('Anim Pakal', 'RW'), ('Animar', 'GUR'), ('Araumi', 'UB'),
    ('Bartolomé', 'WB'), ('Belbe', 'BG'), ('Elas', 'WB'), ('Emmara', 'GW'),
    ('Erinis', 'RG'), ('Felothar', 'WBG'), ('Frodo & Sam', 'WBG'), ('Galadriel', 'GWU'),
    ('Gandalf', 'UR'), ('Ganax', 'RG'), ('Indominus Rex', 'BGU'), ('Inniaz', 'WU'),
    ('Ivy', 'GU'), ('Jolrael', 'GU'), ('Kardur', 'BR'), ('Krenko', 'R'),
    ('Lord Skitter', 'B'), ('Magar', 'BR'), ("N'ghathrod", 'UB'), ('Noctis', 'WUB'),
    ('Obeka', 'UBR'), ('Old Rutstein', 'BG'), ('Marchesa', 'UBR'), ('Pantlaza', 'RGW'),
    ('Sauron', 'UBR'), ('Sephirot', 'B'), ('Setzer', 'BR'), ('Shelob', 'BG'),
    ('Stangg', 'RG'), ('Treebeard', 'WBG'), ('Ureni', 'GUR'), ('Urza', 'WUB'),
    ('Volo', 'GU'), ('Wilhelt', 'UB'), ('Will & Mike', 'WBG'), ('Zask', 'BG'),
]

WIN_CONDITIONS = ['Combat Damage', 'Commander Damage', 'Drain/Burn', 'Poison', 'Combo', 'Mill']
LOSS_CONDITIONS = ['Combat Damage', 'Commander Damage', 'Drain/Burn', 'Poison', 'Concede']

COLOR_NAMES = {
    'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green',
    'WU': 'Azorius', 'UB': 'Dimir', 'BR': 'Rakdos', 'RG': 'Gruul', 'GW': 'Selesnya',
    'WB': 'Orzhov', 'UR': 'Izzet', 'BG': 'Golgari', 'RW': 'Boros', 'GU': 'Simic',
    'WUB': 'Esper', 'UBR': 'Grixis', 'BRG': 'Jund', 'RGW': 'Naya', 'GWU': 'Bant',
    'WBG': 'Abzan', 'URW': 'Jeskai', 'BGU': 'Sultai', 'RWB': 'Mardu', 'GUR': 'Temur',
    'WUBR': 'Sans Green', 'UBRG': 'Sans White', 'BRGW': 'Sans Blue',
    'RGWU': 'Sans Black', 'GWUB': 'Sans Red', 'WUBRG': '5 Colour',
}

COLOR_HEX = {
    'W': '#f9fafb', 'U': '#3b82f6', 'B': '#1f2937', 'R': '#ef4444', 'G': '#22c55e',
}


class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    entries = db.relationship('GameEntry', foreign_keys='GameEntry.player_id',
                              backref='player', lazy=True)


class Commander(db.Model):
    __tablename__ = 'commanders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color_identity = db.Column(db.String(10), nullable=False)
    entries = db.relationship('GameEntry', foreign_keys='GameEntry.commander_id',
                              backref='commander', lazy=True)
    kills = db.relationship('GameEntry', foreign_keys='GameEntry.eliminated_by_id',
                            backref='eliminated_by_commander', lazy=True)

    @classmethod
    def known(cls):
        return cls.query.filter(cls.color_identity != '?').order_by(cls.name)


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    total_turns = db.Column(db.Integer)
    entries = db.relationship('GameEntry', backref='game', lazy=True,
                              cascade='all, delete-orphan',
                              order_by='GameEntry.finish')


class GameEntry(db.Model):
    __tablename__ = 'game_entries'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    commander_id = db.Column(db.Integer, db.ForeignKey('commanders.id'), nullable=False)
    finish = db.Column(db.Integer)
    turn_order = db.Column(db.Integer)
    sol_ring_t1 = db.Column(db.Boolean, default=False)
    turn_eliminated = db.Column(db.Integer)
    eliminated_by_id = db.Column(db.Integer, db.ForeignKey('commanders.id'), nullable=True)
    victory_condition = db.Column(db.String(50))
    loss_condition = db.Column(db.String(50))
    notes = db.Column(db.Text)


def seed_initial_data():
    for name in PLAYERS:
        if not Player.query.filter_by(name=name).first():
            db.session.add(Player(name=name))
    for name, color in INITIAL_COMMANDERS:
        if not Commander.query.filter_by(name=name).first():
            db.session.add(Commander(name=name, color_identity=color))
    db.session.commit()
