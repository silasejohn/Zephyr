class AccountDTO:
    def __init__(self, puuid: str, gameName: str, tagLine: str):
        self.puuid = puuid
        self.gameName = gameName
        self.tagLine = tagLine

    @classmethod
    def from_json(cls, json_data):
        """create DTO from JSON"""
        return cls(
            puuid=json_data['puuid'],
            gameName=json_data['gameName'],
            tagLine=json_data['tagLine']    
        )
    
    def to_dict(self):
        """Convert DTO to dictionary."""
        return {
            "puuid": self.puuid,
            "gameName": self.gameName,
            "tagLine": self.tagLine
        }
    
    ### Getters and Setters (Property Decorators) ###
    @property
    def puuid(self):
        # access puuid like an attribute (aka <AccountDTO>.puuid)
        return self._puuid

    @puuid.setter
    def puuid(self, puuid):
        # set puuid like an attribute (aka <AccountDTO>.puuid = "<new_puuid>")
        self._puuid = puuid

    @property
    def gameName(self):
        return self._gameName
    
    @gameName.setter
    def gameName(self, gameName):
        self._gameName = gameName

    @property
    def tagLine(self):
        return self._tagLine
    
    @tagLine.setter
    def tagLine(self, tagLine):
        self._tagLine = tagLine
    
    def __repr__(self):
        return f"AccountDTO(puuid={self.puuid}, gameName={self.gameName}, tagLine={self.tagLine})"

