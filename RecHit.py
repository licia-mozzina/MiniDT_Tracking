CellLength = 4.2 # cm
CellHeight = 1.3 # cm
VDrift = 0.00535 # cm / ns

class RecHit:        
    def __init__(self, timestamp, station, layer, wire):
        self.Timestamp = timestamp
        self.Station = 'X' if (station == 0) else 'Y'
        self.Layer = layer
        self.Wire = wire
        self.Position = ((-1, -1), (-1, -1)) 
        self.Laterality = -1
    
    def SetHitPosition(self):
        # two positions, lateral ambiguity
        j = self.Layer * CellHeight  + 0.5 * CellHeight - 2 * CellHeight
        i_offset = self.Wire * CellLength + (0.5 if (self.Layer % 2 == 1) else 1) * CellLength - 8.25 * CellLength
        
        iL = i_offset - (self.Timestamp * VDrift)
        iR = i_offset + (self.Timestamp * VDrift)
        
        self.Position = ((iL, j), (iR, j))
        
    def SetHitLaterality(self, laterality):
        self.Laterality = laterality