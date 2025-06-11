class SummonerDTO:
    def __init__(self, encryptedAccountId: str, profileIconID: int, revisionDate: int, encryptedSummonerID: str, encryptedPuuid: str, summonerLevel: int):
        self.encryptedAccountId = encryptedAccountId # Encrypted account ID. Max length 56 characters
        self.profileIconID = profileIconID # ID of the summoner icon associated with the summoner
        self.revisionDate = revisionDate # Date summoner was last modified specified as epoch milliseconds
        self.encryptedSummonerID = encryptedSummonerID # Encrypted summoner ID. Max length 63 characters
        self.encryptedPuuid = encryptedPuuid # Encrypted PUUID. Exact length of 78 characters
        self.summonerLevel = summonerLevel # Summoner level associated with the summoner

    @classmethod
    def from_json(cls, json_data):
        """create DTO from JSON"""
        return cls(
            encryptedAccountId=json_data['accountId'],
            profileIconID=json_data['profileIconId'],
            revisionDate=json_data['revisionDate'],
            encryptedSummonerID=json_data['id'],
            encryptedPuuid=json_data['puuid'],
            summonerLevel=json_data['summonerLevel']
        )
    
    def to_dict(self):
        """Convert DTO to dictionary."""
        return {
            "encryptedAccountId": self.encryptedAccountId,
            "profileIconID": self.profileIconID,
            "revisionDate": self.revisionDate,
            "encryptedSummonerID": self.encryptedSummonerID,
            "encryptedPuuid": self.encryptedPuuid,
            "summonerLevel": self.summonerLevel
        }
    
    ### Getters and Setters (Property Decorators) ###
    @property
    def encryptedAccountId(self):
        # access encryptedAccountId like an attribute (aka <SummonerDTO>.encryptedAccountId)
        return self._encryptedAccountId 
    
    @encryptedAccountId.setter
    def encryptedAccountId(self, encryptedAccountId):
        # set encryptedAccountId like an attribute (aka <SummonerDTO>.encryptedAccountId = "<new_encryptedAccountId>")
        self._encryptedAccountId = encryptedAccountId

    @property
    def profileIconID(self):
        return self._profileIconID
    
    @profileIconID.setter
    def profileIconID(self, profileIconID):
        self._profileIconID = profileIconID

    @property
    def revisionDate(self):
        return self._revisionDate
    
    @revisionDate.setter
    def revisionDate(self, revisionDate):
        self._revisionDate = revisionDate

    @property
    def encryptedSummonerID(self):
        return self._encryptedSummonerID
    
    @encryptedSummonerID.setter
    def encryptedSummonerID(self, encryptedSummonerID):
        self._encryptedSummonerID = encryptedSummonerID

    @property
    def encryptedPuuid(self):
        return self._encryptedPuuid
    
    @encryptedPuuid.setter
    def encryptedPuuid(self, encryptedPuuid):
        self._encryptedPuuid = encryptedPuuid

    @property
    def summonerLevel(self):
        return self._summonerLevel
    
    @summonerLevel.setter
    def summonerLevel(self, summonerLevel):
        self._summonerLevel = summonerLevel
    
    def __repr__(self):
        return f"SummonerDTO(encryptedAccountId={self.encryptedAccountId}, profileIconID={self.profileIconID}, revisionDate={self.revisionDate}, encryptedSummonerID={self.encryptedSummonerID}, encryptedPuuid={self.encryptedPuuid}, summonerLevel={self.summonerLevel})"

