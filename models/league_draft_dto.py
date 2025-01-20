class LeagueDraftDTO:
    def __init__(self, gcs_id: str, match_id: str, blue_team_id: str, red_team_id: str, draft_sequence: list = []):
        self.gcs_id = gcs_id
        self.match_id = match_id
        self.blue_team_id = blue_team_id
        self.red_team_id = red_team_id
        self.draft_sequence = draft_sequence        # list of champions picked / banned in draft

        # options per arg for semantic reasons
        self.draft_phase_options = ['ban_phase_1', 'draft_phase_1', 'ban_phase_2', 'draft_phase_2']
        self.team_color_options = ['blue', 'red']
        self.draft_action_options = ['ban', 'pick']
        self.champ_role_options = ['top', 'jgl', 'mid', 'bot', 'sup']

    def add_draft_event(self, draft_phase, team_color, draft_action, champion, champ_role):

        # do some input validation
        if draft_phase not in self.draft_phase_options:
            raise ValueError(f"Invalid draft_phase: {draft_phase}")
        if team_color not in self.team_color_options:   
            raise ValueError(f"Invalid team_color: {team_color}")
        if draft_action not in self.draft_action_options:
            raise ValueError(f"Invalid draft_action: {draft_action}")
        if champ_role not in self.champ_role_options:
            raise ValueError(f"Invalid champ_role: {champ_role}")

        self.draft_sequence.append({
            "draft_phase": draft_phase,
            "team_side": team_color,
            "team_id": self.blue_team_id if team_color == 'blue' else self.red_team_id,
            "draft_action": draft_action,
            "champion": champion,
            "champ_role": champ_role
        })

    def replace_draft_event(draft_phase, team_color, champion, champ_role):
        # replace champion and champ role in the draft_phase stated 
        pass

    @classmethod
    def from_json(cls, json_data):
        """create DTO from JSON"""
        return cls(
            gcs_id=json_data['gcs_id'],
            match_id=json_data['match_id'], 
            blue_team_id=json_data['blue_team_id'],
            red_team_id=json_data['red_team_id'],
            draft_sequence=json_data['draft_sequence']
        )
    
    ### Getters and Setters (Property Decorators) ###
    @property
    def gcs_id(self):
        # access gcs_id like an attribute (aka <LeagueDraftDTO>.gcs_id)
        return self._gcs_id

    @gcs_id.setter
    def gcs_id(self, gcs_id):
        # set gcs_id like an attribute (aka <LeagueDraftDTO>.gcs_id = "<new_gcs_id>")
        self._gcs_id = gcs_id

    @property
    def match_id(self):
        return self._match_id
    
    @match_id.setter
    def match_id(self, match_id):
        self._match_id = match_id

    @property
    def blue_team_id(self):
        return self._blue_team_id
    
    @blue_team_id.setter
    def blue_team_id(self, blue_team_id):
        self._blue_team_id = blue_team_id

    @property
    def red_team_id(self):
        return self._red_team_id
    
    def get_draft_sequence(self):
        return self.draft_sequence
    
    def __repr__(self):
        return f"LeagueDraftDTO(gcs_id={self.gcs_id}, match_id={self.match_id}, blue_team_id={self.blue_team_id}, red_team_id={self.red_team_id}, draft_sequence={self.draft_sequence})"

"""
JSON STRUCTURE
{
  "game": {
    "blue_team_id": "TEAM_BLUE_ID",
    "red_team_id": "TEAM_RED_ID",
    "draft_sequence": [
      {"phase": "ban_phase_1", "team": "blue", "action": "ban", "champion": "Blue Ban 1"},
      {"phase": "ban_phase_1", "team": "red", "action": "ban", "champion": "Red Ban 1"},
      {"phase": "ban_phase_1", "team": "blue", "action": "ban", "champion": "Blue Ban 2"},
      {"phase": "ban_phase_1", "team": "red", "action": "ban", "champion": "Red Ban 2"},
      {"phase": "ban_phase_1", "team": "blue", "action": "ban", "champion": "Blue Ban 3"},
      {"phase": "ban_phase_1", "team": "red", "action": "ban", "champion": "Red Ban 3"},
      {"phase": "draft_phase_1", "team": "blue", "action": "pick", "champion": "Blue Draft 1"},
      {"phase": "draft_phase_1", "team": "red", "action": "pick", "champion": "Red Draft 1"},
      {"phase": "draft_phase_1", "team": "red", "action": "pick", "champion": "Red Draft 2"},
      {"phase": "draft_phase_1", "team": "blue", "action": "pick", "champion": "Blue Draft 2"},
      {"phase": "draft_phase_1", "team": "blue", "action": "pick", "champion": "Blue Draft 3"},
      {"phase": "draft_phase_1", "team": "red", "action": "pick", "champion": "Red Draft 3"},
      {"phase": "ban_phase_2", "team": "red", "action": "ban", "champion": "Red Ban 4"},
      {"phase": "ban_phase_2", "team": "blue", "action": "ban", "champion": "Blue Ban 4"},
      {"phase": "ban_phase_2", "team": "red", "action": "ban", "champion": "Red Ban 5"},
      {"phase": "ban_phase_2", "team": "blue", "action": "ban", "champion": "Blue Ban 5"},
      {"phase": "draft_phase_2", "team": "red", "action": "pick", "champion": "Red Draft 4"},
      {"phase": "draft_phase_2", "team": "blue", "action": "pick", "champion": "Blue Draft 4"},
      {"phase": "draft_phase_2", "team": "blue", "action": "pick", "champion": "Blue Draft 5"},
      {"phase": "draft_phase_2", "team": "red", "action": "pick", "champion": "Red Draft 5"}
    ]
  }
}


"""
"""
# Example usage
draft = LeagueDraft("TEAM_BLUE_ID", "TEAM_RED_ID")

# Adding events in order
draft.add_event("ban_phase_1", "blue", "ban", "Blue Ban 1")
draft.add_event("ban_phase_1", "red", "ban", "Red Ban 1")
# Continue adding events...

# Accessing the draft sequence
print(draft.get_draft_sequence())

"""