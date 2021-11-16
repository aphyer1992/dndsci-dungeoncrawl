import random
import math
import csv

global_verbose_flag = False

def roll_die(n):
    return(math.ceil(random.random() * n))

class Char_Class():
    def __init__(self, name, melee_guard, range_guard, magic_guard, healing, wild_empathy, cowardly):
        self.name = name
        self.melee_guard = melee_guard
        self.range_guard = range_guard
        self.magic_guard = magic_guard
        self.healing = healing
        self.wild_empathy = wild_empathy
        self.cowardly = cowardly

class Adventurer():
    def __init__(self, char_class, level):
        self.char_class = char_class
        self.level = level
        self.melee_guard = self.char_class.melee_guard
        self.range_guard = self.char_class.range_guard
        self.magic_guard = self.char_class.magic_guard
        self.healing = 0.5 if self.char_class.healing == True else 0
        self.wild_empathy = self.level if self.char_class.wild_empathy == True else 0
        

    def print_self(self):
        print('Level {} {}'.format(self.level, self.char_class.name))
    
        
class Party():
    def __init__(self, world, adventurers):
        self.world = world
        self.adventurers = adventurers
        self.total_hp = sum([(1+a.level) for a in self.adventurers])
        self.current_hp = self.total_hp
        self.guards = []
        if len([a for a in self.adventurers if a.melee_guard == True]):
            self.guards.append('Melee')
        if len([a for a in self.adventurers if a.range_guard == True]):
            self.guards.append('Range')
        if len([a for a in self.adventurers if a.magic_guard == True]):
            self.guards.append('Magic')
        self.healing = sum([a.healing for a in self.adventurers])
        self.wild_empathy = max([a.wild_empathy for a in self.adventurers])
        self.class_max_levels = {}
        for c in self.world.char_classes:
            levels = [0] + [a.level for a in self.adventurers if a.char_class == c]
            self.class_max_levels[c.name] = max(levels)

    def log_dungeon(self, dungeon):
        party_log = [dungeon.name]
        for a in self.adventurers:
            party_log.append(a.char_class.name)
            party_log.append(a.level)
        encounter_list = [(e.encounter_type.name) for e in dungeon.encounters]
        while len(encounter_list) < self.world.max_dungeon_length:
            encounter_list.append('')
        assert(len(encounter_list) == self.world.max_dungeon_length)
        threat_level = dungeon.get_threat_level()
        num_encounters = len(dungeon.encounters)
        num_beaten = len([e for e in dungeon.encounters if e.beaten == True])
        victory = 1 if num_encounters == num_beaten else 0
        log = party_log + encounter_list + [threat_level, num_encounters, num_beaten, victory]

        # what you were beated by:
        beaten_by = ''
        for encounter in dungeon.encounters:
            if encounter.beaten == False:
                beaten_by = encounter.encounter_type.name
                break

        log.append(beaten_by)
        
        self.world.log(log)

        # extended log for lazy people:
        extended_log = log
        for c in self.world.char_classes:
            class_list = [a for a in self.adventurers if a.char_class == c]
            extended_log.append(len(class_list))
            extended_log.append(sum([0]+[a.level for a in class_list]))
            extended_log.append(max([0]+[a.level for a in class_list]))
            
        for encounter_type in self.world.encounter_types:
            enc_list = [ e for e in dungeon.encounters if e.encounter_type == encounter_type]
            extended_log.append(len(enc_list))

        self.world.log(extended_log, extended_log=True)

    def heal(self):
        self.current_hp = min(self.total_hp, self.current_hp + self.healing)
        
    def run_dungeon(self, dungeon, log=True):
        for e in dungeon.encounters:
            e.encountered = True
            if global_verbose_flag:
                print('Encountering {} at {} HP'.format(e.encounter_type.name, self.current_hp))
            e.encounter_type.encounter_func(self)
            if global_verbose_flag:
                print('Remaining HP {}'.format(self.current_hp))
            if self.current_hp <= 0:
                break
            else:
                e.beaten = True
            self.heal()
        if log:
            self.log_dungeon(dungeon)

    def print_self(self):
        print('Party Members:\n')
        for a in self.adventurers:
            a.print_self()
        print(self.guards)
                  

class Encounter_Type():
    def __init__(self, name, threat_level, species, encounter_func):
        self.name = name
        self.threat_level = threat_level
        self.species = species
        self.encounter_func = encounter_func

class Encounter():
    def __init__(self, encounter_type):
        self.encounter_type = encounter_type
        self.encountered = False
        self.beaten = False


class Dungeon():
    def __init__(self, world):
        self.world = world

        rng = random.random()
        if rng < 0.35:
            self.type = 'City'
            self.setup_city()
        elif rng < 0.7:
            self.type = 'Lair'
            self.setup_lair()
        else:
            self.type = 'Dungeon'
            self.setup_dungeon()

        self.get_encounters_by_name()
        self.name = self.name + ' of ' + random.choice([
            'Khaz-Gorond', 'Riverfell', 'Limeneth', 'Galoron', 'Cheliax', 'Lemarchand', 'Calantha', 'Almadris', 'Sintharion',
            'Azmar', 'Icemarch', 'Lakeshore', 'Stormwind', 'Darkflight Pass', 'Stonefell Peak'
        ])

    def setup_city(self):
        self.species = random.choice(['Goblin', 'Orc', 'Undead'])
        encounter_count = roll_die(4) + roll_die(4)
        trap_count = math.floor(encounter_count / 2.0)
        if self.species == 'Goblin':
            boss = random.choice(['Goblin Chieftain', 'Goblin Chieftain', 'Goblins'])
            if encounter_count >= 6:
                boss = 'Goblin Chieftain'
            encounters = ['Goblins', 'Goblins', 'Goblins', 'Goblins']
            self.name = 'Goblin ' + random.choice(['Tunnels', 'Warrens', 'Cave', 'Town', 'Hole', 'Tower', 'Fort'])
            goblin_type_rng = random.random()
            if goblin_type_rng < 0.2:
                self.name = 'Night ' + self.name
                encounters.append('Ghosts')
            elif goblin_type_rng < 0.4:
                self.name = 'Mountain ' + self.name
                encounters.append('Wolves')
                encounters.append('Wolves')
            trap_type = random.choice(['Boulder Trap', 'Snake Pit', 'Poison Needle Trap'])
        elif self.species == 'Orc':
            boss = random.choice(['Orc Warlord', 'Orc Warlord','Orc Warlord','Orc Shaman','Orc Shaman', 'Orcs'])
            encounters = ['Orcs', 'Orcs', 'Orcs', 'Orcs', 'Wolves', 'Wolves']
            name_options = ['Keep', 'Cave', 'Town', 'Camp', 'Tower', 'Warcamp', 'Fort']
            if encounter_count >= 6:
                name_options.append('City')
                name_options.append('Citadel')
            self.name = 'Orc ' + random.choice(name_options)
            if boss == 'Orc Warlord':
                encounters.append('Orc Shaman')
            if random.random() < 0.2:
                self.name = 'Black ' + self.name
                encounters.append('Orc Warlord')
            trap_type = random.choice(['Boulder Trap', 'Snake Pit', 'Poison Needle Trap', 'Cursed Altar'])
        elif self.species == 'Undead':
            boss = random.choice(['Skeletons', 'Zombies', 'Ghosts', 'Ghosts', 'Lich'])
            encounters = [ 'Skeletons', 'Skeletons', 'Zombies', 'Zombies', 'Ghosts' ]
            self.name = 'Undead ' + random.choice(['Sepulcher', 'Pyramid', 'Mausoleum', 'Ziggurat', 'City', 'Keep'])
            trap_type = random.choice(['Boulder Trap', 'Poison Needle Trap', 'Cursed Altar'])

        self.encounter_names = []
        while encounter_count > 1: # save one for the boss
            self.encounter_names.append(random.choice(encounters))
            encounter_count = encounter_count - 1
        
        while trap_count > 0: 
            self.encounter_names.append(trap_type)
            trap_count = trap_count - 1
        
        random.shuffle(self.encounter_names)
        self.encounter_names.append(boss)       
        
    def setup_lair(self):
        boss = random.choice(['Dragon', 'Basilisk', 'Lich'])
        slaves = random.choice(['Goblins', 'Orcs', 'Undead'])
        if boss == 'Lich':
            slaves = 'Undead'

        if slaves == 'Undead':
            slave_encounters = ['Zombies', 'Skeletons']
        elif slaves == 'Goblins':
            slave_encounters = [ 'Goblins', 'Wolves' ]
        elif slaves == 'Orcs':
            slave_encounters = [ 'Orcs', 'Wolves' ]

        slave_encounter_count = roll_die(3)
        trap_count = roll_die(3)

        prefixes = [ 'Ancient', 'Infernal', 'Old', 'Nightmare', 'Dread', 'Sunken' ]
        suffixes = [ 'Lair', 'Den', 'Cave', 'Maw' ]
        if boss == 'Lich':
            suffixes.remove('Maw')
            suffixes.append('Tomb')
        if boss == 'Basilisk':
            prefixes.remove('Ancient')
            prefixes.remove('Infernal')

        self.name = random.choice(prefixes) + ' ' + random.choice(suffixes)
        
        self.encounter_names = []
        while slave_encounter_count > 0: 
            self.encounter_names.append(random.choice(slave_encounters))
            slave_encounter_count = slave_encounter_count - 1

        trap_types = [ e_type.name for e_type in self.world.encounter_types if e_type.species == 'Trap' ]
        while trap_count > 0:
            self.encounter_names.append(random.choice(trap_types))
            trap_count = trap_count - 1
        
        random.shuffle(self.encounter_names)
        self.encounter_names.append(boss)
        
            
    def setup_dungeon(self):
        encounter_count = roll_die(4)
        trap_count = roll_die(3) + roll_die(3)
        encounters = [ 'Zombies', 'Skeletons', 'Ghosts' ]
        if random.random() < 0.2:
            encounters.append('Goblins')
        if random.random() < 0.2:
            encounters.append('Orcs')
        if random.random() < 0.5:
            encounters.append('Wolves')
        if random.random() < 0.1:
            encounters.append('Dragon')
        if random.random() < 0.1:
            encounters.append('Lich')
        if random.random() < 0.2:
            encounters.append('Basilisk')

        self.encounter_names = []
        while encounter_count > 0: 
            self.encounter_names.append(random.choice(encounters))
            encounter_count = encounter_count - 1
        trap_types = [ e_type.name for e_type in self.world.encounter_types if e_type.species == 'Trap' ]
        while trap_count > 0:
            self.encounter_names.append(random.choice(trap_types))
            trap_count = trap_count - 1

        prefixes = [ 'Lost', 'Forgotten', 'Abandoned', 'Timeless' ]
        suffixes = [ 'Temple', 'Dungeon', 'Treasure' ]
        if 'Dragon' in encounters:
            suffixes = ['Treasure']

        self.name = random.choice(prefixes) + ' ' + random.choice(suffixes)

        random.shuffle(self.encounter_names)

    def get_encounters_by_name(self):
        self.encounters = []
        for e_name in self.encounter_names:
            encounter_types = [ e_type for e_type in self.world.encounter_types if e_type.name == e_name ]
            if len(encounter_types) != 1:
                print('PROBLEM ENCOUNTERED: {} results found querying for {}!\n'.format(len(encounter_types), e_name))
            self.encounters.append(Encounter(encounter_types[0]))

    def get_threat_level(self):
        total_damage = sum([e.encounter_type.threat_level for e in self.encounters])
        return((total_damage-1) / self.world.party_size)

    def print_self(self):
        print('\n{}:\n'.format(self.name))
        print(self.encounter_names)
        print('\nThreat Level: {}\n'.format(self.get_threat_level()))
        


def encounter_enemy(party, damage, attack_types, wild_empathy_works=False, turn_undead_works=False, verbose=False):
    double_damage = False
    uncountered_attack_types = [a for a in attack_types if a not in party.guards]

    if wild_empathy_works:
        damage = damage - party.wild_empathy

    uncountered_type_count = len(uncountered_attack_types)
    if turn_undead_works and party.healing > 0:
        uncountered_type_count = uncountered_type_count - 1
        
    if uncountered_type_count > 0:
        if global_verbose_flag:
            print('POW!')
        damage = damage * 2

    if damage > 0:
        party.current_hp = party.current_hp - damage

def encounter_trap(party, damage, counter_class):
    party_counter_level = party.class_max_levels[counter_class]
    damage = damage - party_counter_level
    if damage > 0:
        party.current_hp = party.current_hp - damage
    
def encounter_goblins(party):
    damage = roll_die(3)
    encounter_enemy(party, damage, ['Range'])

def encounter_goblin_chief(party):
    damage = roll_die(4)
    encounter_enemy(party, damage, ['Melee'])
    
def encounter_orcs(party):
    damage = roll_die(4)
    encounter_enemy(party, damage, ['Melee'])

def encounter_wolves(party):
    damage = roll_die(4)
    encounter_enemy(party, damage, ['Melee'], wild_empathy_works=True)

def encounter_orc_warlord(party):
    damage = roll_die(8)
    encounter_enemy(party, damage, ['Melee'])
 
def encounter_orc_shaman(party):
    damage = roll_die(6)
    encounter_enemy(party, damage, ['Magic'])

def encounter_skeletons(party):
    damage = roll_die(3)
    encounter_enemy(party, damage, [ 'Range', 'Magic'], turn_undead_works=True )

def encounter_zombies(party):
    damage = roll_die(3)
    encounter_enemy(party, damage, [ 'Melee', 'Magic'], turn_undead_works=True )    

def encounter_ghosts(party):
    damage = roll_die(4)
    encounter_enemy(party, damage, [ 'Magic' ], turn_undead_works=True )

def encounter_basilisk(party):
    damage = roll_die(8)
    encounter_enemy(party, damage, ['Melee', 'Magic'], wild_empathy_works=True)

def encounter_lich(party):
    damage = roll_die(10)
    encounter_enemy(party, damage, ['Magic'], turn_undead_works=True)
    
def encounter_dragon(party):
    damage = roll_die(6) + roll_die(6)
    encounter_enemy(party, damage, ['Melee', 'Range', 'Magic'])
    
def encounter_boulder_trap(party):
    damage = roll_die(6)
    encounter_trap(party, damage, 'Fighter')

def encounter_lever_puzzle_room(party):
    damage = roll_die(6)
    encounter_trap(party, damage, 'Ranger')

def encounter_riddle_door(party):
    damage = roll_die(6)
    encounter_trap(party, damage, 'Mage')

def encounter_cursed_altar(party):
    damage = roll_die(6)
    encounter_trap(party, damage, 'Cleric')

def encounter_snake_pit(party):
    damage = roll_die(6)
    encounter_trap(party, damage, 'Druid')

def encounter_poison_needle_trap(party):
    damage = roll_die(6)
    encounter_trap(party, damage, 'Rogue')



                   
class World():
    def __init__(self, log=True):
        self.party_size = 4
        self.max_dungeon_length = 12
        self.char_classes = [
            Char_Class('Fighter', True, False, False, False, False, False ),
            Char_Class('Ranger', False, True, False, False, False, False ),
            Char_Class('Mage', False, False, True, False, False, False ),
            Char_Class('Cleric', False, False, False, True, False, False ),
            Char_Class('Druid', False, False, False, False, True, False ),
            Char_Class('Rogue', False, False, False, False, False, True ),
            ]
        self.encounter_types = [
            Encounter_Type('Goblins', 1.3, 'Goblin', encounter_goblins),
            Encounter_Type('Goblin Chieftain', 3, 'Goblin', encounter_goblin_chief),
            Encounter_Type('Wolves', 3, 'Beast', encounter_wolves),
            Encounter_Type('Orcs', 2, 'Orc', encounter_orcs),
            Encounter_Type('Orc Warlord', 5, 'Orc', encounter_orc_warlord),
            Encounter_Type('Orc Shaman', 3, 'Orc', encounter_orc_shaman),
            Encounter_Type('Skeletons', 2, 'Undead', encounter_skeletons),
            Encounter_Type('Zombies', 2, 'Undead', encounter_zombies),
            Encounter_Type('Ghosts', 3, 'Undead', encounter_ghosts),
            Encounter_Type('Basilisk', 5, 'Boss', encounter_basilisk),
            Encounter_Type('Lich', 7, 'Boss', encounter_lich),
            Encounter_Type('Dragon', 10, 'Boss', encounter_dragon),
            Encounter_Type('Boulder Trap', 2, 'Trap', encounter_boulder_trap),
            Encounter_Type('Lever Puzzle Room', 2, 'Trap', encounter_lever_puzzle_room),
            Encounter_Type('Riddle Door', 2, 'Trap', encounter_riddle_door),
            Encounter_Type('Cursed Altar', 2, 'Trap', encounter_cursed_altar),
            Encounter_Type('Snake Pit', 2, 'Trap', encounter_snake_pit),
            Encounter_Type('Poison Needle Trap', 2, 'Trap', encounter_poison_needle_trap),
        ]
        if log:
            self.setup_logs()

    def choose_adventurers(self, dungeon):
        party = []
        dungeon_threat_level = dungeon.get_threat_level()
        assert(dungeon_threat_level < 10) # if not we will not be able to get chars
        while len(party) < self.party_size:
            new_char_class = random.choice(self.char_classes)
            new_char_level = min(roll_die(8), roll_die(8))
            level_diff = abs(new_char_level - dungeon_threat_level)
            if new_char_class.cowardly: # favor low-level dungeons
                if new_char_level > dungeon_threat_level:
                    level_diff = level_diff / 2
                else:
                    level_diff = level_diff * 2
                
            accept_prob = 1 - (0.5 * level_diff) # favor chars of the right level
            for c in party:
                if c.char_class == new_char_class:
                    accept_prob = 0.5 * accept_prob # favor chars we don't already have
            if random.random() < accept_prob:
                party.append(Adventurer(new_char_class, new_char_level))

        return(Party(self,party))
            
    def log(self, contents, extended_log=False, overwrite=False):
        log_location = 'dungeon_crawl_corrected.csv' if extended_log else 'dungeon_crawl.csv'
        contents = [str(x) for x in contents]
        message = ','.join(contents) + '\n'
        file = open(log_location, 'w' if overwrite else 'a')
        file.write(message)
        

    def setup_logs(self):
        log_headers = ['Dungeon Name']
        for i in range(1, self.party_size + 1):
            log_headers.append('Adventurer {} Class'.format(str(i)))
            log_headers.append('Adventurer {} Level'.format(str(i)))
        for i in range(1, self.max_dungeon_length + 1):
            log_headers.append('Encounter {}'.format(str(i)))
        log_headers = log_headers + [ 'Threat Level', '# Encounters', '# Encounters Beaten', 'Victory?', 'Defeated By']

        self.log(log_headers, extended_log=False, overwrite=True)

        extended_log_headers = log_headers
        for c in self.char_classes:
            extended_log_headers.append('# of {} Adventurers'.format(c.name))
            extended_log_headers.append('Total Level of {} Adventurers'.format(c.name))
            extended_log_headers.append('Max Level of {} Adventurers'.format(c.name))

        for e_type in self.encounter_types:
            extended_log_headers.append('# of {} Encounters'.format(e_type.name))

        self.log(extended_log_headers, extended_log=True, overwrite=True)

    def get_class_by_name(self, name):
        return([c for c in self.char_classes if c.name == name][0])

    def get_party_by_name_and_levels(self, a_list): # [ ('Cleric', 3), ('Druid', 3), ('Rogue', 3), ('Cleric', 3) ]
        party = [ Adventurer(self.get_class_by_name(a[0]), a[1]) for a in a_list ]
        return(Party(self,party))

    def run_dungeon(self):
        dungeon = Dungeon(self)
        party = self.choose_adventurers(dungeon)
        if global_verbose_flag:
            dungeon.print_self()
            party.print_self()
        party.run_dungeon(dungeon)

random.seed('Dungeon Crawl Stone Soup')
ad_hoc_test_runs = False
main_run = False
specific_team_test_runs = True
if( specific_team_test_runs == True):
    my_world = World(log=False)
    runs = 0
    wins = 0
    losses = 0
    while runs < 50000:
        #string_party = [('Mage', 2), ('Cleric', 3), ('Rogue', 2), ('Druid', 2)]   # simon LTL
        #string_party = [('Fighter', 4), ('Ranger', 4), ('Cleric', 3), ('Druid', 4)]  # simon ITC
        string_party = [('Ranger', 3), ('Fighter', 4), ('Druid', 3), ('Ranger', 3)] # simon GWK
        #string_party = [('Mage', 4), ('Cleric', 4), ('Rogue', 1), ('Ranger', 1)]   # Talentum LTL
        #string_party = [('Fighter', 3), ('Ranger', 5), ('Mage', 1), ('Druid', 4)]  # Talentum ITC
        #string_party = [('Ranger', 3), ('Fighter', 3), ('Cleric', 4), ('Rogue', 3)] # Talentum GWK
        #string_party = [('Mage', 2), ('Cleric', 3), ('Rogue', 2), ('Druid', 2)]   # Yonge LTL
        #string_party = [('Fighter', 7), ('Ranger', 3), ('Cleric', 2), ('Druid', 2)]  # Yonge ITC
        #string_party = [('Ranger', 6), ('Fighter', 4), ('Rogue', 1), ('Cleric', 2)] # Yonge GWK
        #string_party = [('Mage', 2), ('Cleric', 2), ('Rogue', 2), ('Druid', 2)]   # aa LTL
        #string_party = [('Fighter', 5), ('Ranger', 3), ('Mage', 3), ('Druid', 3)]  # aa ITC
        #string_party = [('Ranger', 4), ('Fighter', 4), ('Fighter', 3), ('Cleric', 3)] # aa GWK
        #string_party = [('Fighter', 1), ('Ranger', 1), ('Mage', 1), ('Cleric', 3)] #Measure LTL
        #string_party = [('Fighter', 4), ('Ranger', 3), ('Mage', 7), ('Cleric', 4)] #Measure IDC
        #string_party = [('Fighter', 3), ('Fighter', 2), ('Ranger', 3), ('Cleric', 4)] #Measure GWK
        #string_party = [('Mage', 1), ('Cleric', 1), ('Rogue', 5), ('Druid', 5)]   # 12 total levels
        #string_party = [('Fighter', 3), ('Ranger', 2), ('Mage', 2), ('Druid', 6)]  # 13 total levels
        #string_party = [('Ranger', 2), ('Fighter', 6), ('Cleric', 1), ('Cleric', 1)] #10 total levels
        #string_party = [('Mage', 3), ('Cleric', 3), ('Rogue', 3), ('Druid', 3)]   # Class based LTL
        #string_party = [('Fighter', 3), ('Ranger', 3), ('Mage', 3), ('Druid', 3)]  # Class based ITC
        #string_party = [('Ranger', 3), ('Fighter', 3), ('Cleric', 3), ('Cleric', 3)] # Class based GWK
        party = my_world.get_party_by_name_and_levels( [(x[0], x[1]) for x in string_party] )
        dungeon = Dungeon(my_world)
        #dungeon.encounter_names = [ 'Skeletons', 'Skeletons', 'Poison Needle Trap', 'Zombies', 'Snake Pit', 'Poison Needle Trap', 'Ghosts', 'Snake Pit' ] 
        #dungeon.encounter_names = [ 'Snake Pit', 'Orcs', 'Snake Pit', 'Wolves', 'Dragon' ]
        dungeon.encounter_names = [ 'Goblins', 'Boulder Trap', 'Goblins', 'Goblins', 'Boulder Trap', 'Goblins', 'Goblins', 'Boulder Trap', 'Goblins', 'Goblin Chieftain' ]
        dungeon.get_encounters_by_name()
        party.run_dungeon(dungeon, log=False)
        if party.current_hp > 0:
            wins = wins + 1
        else:
            losses = losses + 1
        runs = runs + 1
    print('Won {}/{} ({:.2f}%)'.format(wins, runs, wins * 100 / runs))

if( ad_hoc_test_runs == True  ):

    possible_parties = [[]]
    char_classes = [ 'Fighter', 'Ranger', 'Mage', 'Cleric', 'Druid', 'Rogue']
    for char_class in char_classes:
        new_parties = []
        for entry in possible_parties:
            for num_to_add in range(0,5-len(entry)):
                alt_entry = entry + []
                for i in range(0, num_to_add):
                    alt_entry.append(char_class)
                new_parties.append(alt_entry)
        possible_parties = new_parties
    possible_parties = [ p for p in possible_parties if len(p) == 4]
            

    my_world = World(log=False)
    out_list = []

    for possible_party in possible_parties:
        runs = 0
        wins = 0
        losses = 0
        while runs < 1000:
            party = my_world.get_party_by_name_and_levels( [(x, 3) for x in possible_party] )
            dungeon = Dungeon(my_world)
            dungeon.encounter_names = [ 'Goblins', 'Boulder Trap', 'Goblins', 'Goblins', 'Boulder Trap', 'Goblins', 'Goblins', 'Boulder Trap', 'Goblins', 'Goblin Chieftain' ]
            #dungeon.encounter_names = [ 'Orcs', 'Snake Pit', 'Wolves', 'Snake Pit', 'Dragon' ]
            #dungeon.encounter_names = [ 'Skeletons', 'Poison Needle Trap', 'Zombies', 'Snake Pit', 'Poison Needle Trap', 'Skeletons', 'Snake Pit', 'Ghosts' ]
            dungeon.get_encounters_by_name()
            party.run_dungeon(dungeon, log=False)
            if party.current_hp > 0:
                wins = wins + 1
            else:
                losses = losses + 1
            runs = runs + 1
        out_list.append({ 'party' : possible_party, 'win_rate' : wins / runs})

    out_list.sort(key=lambda struct: struct['win_rate'])
    for entry in out_list:
        print(entry)
    overall_winrate = sum([entry['win_rate'] for entry in out_list]) / len(out_list)
    print('Random winrate: {:.2f}%'.format(100*overall_winrate))
        
        
if( main_run == True):
    random.seed('Dungeon Crawl Stone Soup')
    my_world = World()
    for i in range(0,2922):
        my_world.run_dungeon()


    # tracking data:
    with open('dungeon_crawl_corrected.csv') as f:
        a = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]

    runs = len(a)
    wins = len([e for e in a if e['Victory?'] == '1'])
    print('{}/ {} runs won in total ({:.2f}%)'.format(wins, runs, 100 * wins / runs))

    class_results_struct = {}
    for char_class in my_world.char_classes:
        class_results_struct[char_class.name] = {'appearances' : 0, 'wins' : 0, 'losses' : 0, 'total_level' : 0}

    for entry in a:
        for char_class in my_world.char_classes:
            num = int(entry['# of {} Adventurers'.format(char_class.name)])
            class_results_struct[char_class.name]['appearances'] = class_results_struct[char_class.name]['appearances'] + num
            lvl = int(entry['Total Level of {} Adventurers'.format(char_class.name)])
            class_results_struct[char_class.name]['total_level'] = class_results_struct[char_class.name]['total_level'] + lvl
            win = int(entry['Victory?'])
            class_results_struct[char_class.name]['wins'] = class_results_struct[char_class.name]['wins'] + (num * win)
            class_results_struct[char_class.name]['losses'] = class_results_struct[char_class.name]['losses'] + (num * (1-win))


    for char_class in my_world.char_classes:
        result = class_results_struct[char_class.name]
        print('{}:\n{} appearances.\n{} won ({:.2f}%).\nAverage Level {:.2f}.'.format(char_class.name, result['appearances'], result['wins'], 100*result['wins']/result['appearances'], result['total_level']/result['appearances']))

    encounter_names = [ e.name for e in my_world.encounter_types]

    enc_results_struct = {}
    for e in encounter_names:
        enc_results_struct[e] = {'appearances' : 0, 'wins': 0}

    for entry in a:
        for e in encounter_names:
            num = int(entry['# of {} Encounters'.format(e)])
            win = int(entry['Victory?'])
            enc_results_struct[e]['appearances'] = enc_results_struct[e]['appearances'] + num
            enc_results_struct[e]['wins'] = enc_results_struct[e]['wins'] + (num * win)

    for e in encounter_names:
        result = enc_results_struct[e]
        print('{}: {} known appearances, of which adventurers won {} ({:.2f}%)'.format(e, result['appearances'], result['wins'], (0 if result['appearances'] == 0 else 100*result['wins']/result['appearances'])))
            
            
    threat_lvl_victory_struct = {}
    for i in range(1,10):
        threat_lvl_victory_struct[str(i)] = {'appearances' : 0, 'wins' : 0, 'total_party_level' : 0}

    for entry in a:
        threat_lvl = float(entry['Threat Level'])
        total_party_level = int(entry['Adventurer 1 Level']) + int(entry['Adventurer 2 Level']) + int(entry['Adventurer 3 Level']) + int(entry['Adventurer 4 Level'])
        win = int(entry['Victory?'])
        threat_lvl = str(math.ceil(threat_lvl))
        threat_lvl_victory_struct[threat_lvl]['appearances'] = threat_lvl_victory_struct[threat_lvl]['appearances'] + 1
        threat_lvl_victory_struct[threat_lvl]['wins'] = threat_lvl_victory_struct[threat_lvl]['wins'] + win
        threat_lvl_victory_struct[threat_lvl]['total_party_level'] = threat_lvl_victory_struct[threat_lvl]['total_party_level'] + total_party_level

        
    for i in range(1,10):
        result = threat_lvl_victory_struct[str(i)]
        print('Threat Level {} Dungeons: {} appearances, of which adventurers won {} ({:.2f}%).  Average party level {:.2f}.'.format(i, result['appearances'], result['wins'], 0 if result['appearances'] == 0 else 100*result['wins'] / result['appearances'], 0 if result['appearances'] == 0 else 0.25 * result['total_party_level']/result['appearances']))
        
    beaten_by_struct = {}
    for entry in a:
        if entry['Defeated By'] != '':
            if entry['Defeated By'] in beaten_by_struct.keys():
                beaten_by_struct[entry['Defeated By']] = beaten_by_struct[entry['Defeated By']] + 1
            else:
                beaten_by_struct[entry['Defeated By']] = 1

    for key in beaten_by_struct.keys():
        print('{} runs defeated by {}.'.format(beaten_by_struct[key], key))
        
