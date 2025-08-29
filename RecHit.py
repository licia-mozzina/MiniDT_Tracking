CellLength = 4.2 # cm
CellHeight = 1.3 # cm
VDrift = 0.00535 # cm / ns

# raise ValueError for wrong initialization

class RecHit:        
    """
    --------
    Members
    --------
    
    Timestamp: the hit timestamp. Necessary to initilize a RecHit instance
    
    Station: the hit station ('X' = MiniDTX, 'Y' = MiniDT Y). Necessary to initilize a RecHit instance
    
    Layer: the hit layer (0, 1, 2, 3). Necessary to initilize a RecHit instance
    
    Wire: the hit wire/cell. Necessary to initilize a RecHit instance
    
    Position: the hit positions (two sets of values, due to left-right ambiguity) in a local frame of reference (the origin is on the chamber's lower left angle), after applying the SetHitPosition() method. It is initialized to ((-1, -1), (-1, -1))
    
    Laterality: the hit laterality (0 = left, 1 = right). Every hit can be reconstructed either left or right of the cell anodic wire. The ambiguity is solved only with a reconstructed track. It will be assigned when constructing a RecTrack object. It is initialized to -1
     
    
    --------
    Methods
    --------
    
    __init__(self, timestamp, station, layer, wire): RecHit initialization. To initialize, the timestamp, station, layer and wire values are required
    
    SetHitPosition(self): the hit position computation, in a local frame of reference (the origin is on the chamber's lower left angle).
                          It assigns two values to the Position member, due to left-right ambiguity
    
    SetHitLaterality(self, laterality): it assigns the correct value to the Laterality. It can be correctly used only once the hit belongs to a RecTrack object 
    
    
    """
    def __init__(self, timestamp, station, layer, wire):
        self.Timestamp = timestamp
        self.Station = 'X' if (station == 0) else 'Y'
        self.Layer = layer
        self.Wire = wire
        self.Position = ((-1, -1), (-1, -1)) 
        self.Laterality = -1
    
    def SetHitPosition(self):
        # two positions, lateral ambiguity
        j = self.Layer * CellHeight  + 0.5 * CellHeight
        i_offset = self.Wire * CellLength + (0.5 if (self.Layer % 2 == 1) else 1) * CellLength 
        
        iL = i_offset - (self.Timestamp * VDrift)
        iR = i_offset + (self.Timestamp * VDrift)
        
        self.Position = ((iL, j), (iR, j))
        
    def SetHitLaterality(self, laterality):
        self.Laterality = laterality