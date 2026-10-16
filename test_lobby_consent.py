import unittest

from lobby import RPLobby, create_lobby
from portrayal_consent import Consent


class RPLobbyConsentTests(unittest.TestCase):
    def test_factory_still_creates_every_lobby_type(self):
        for mode in ("regular", "megamix", "collection", "rp"):
            with self.subTest(mode=mode):
                self.assertEqual(create_lobby(mode).mode, mode)

    def test_unclassified_character_is_rejected(self):
        lobby = RPLobby()
        with self.assertRaises(ValueError):
            lobby.create_character("player-a", {"name": "Mystery"})
        self.assertNotIn("player-a", lobby.players)

    def test_explicitly_fictional_character_is_allowed(self):
        result = RPLobby().create_character(
            "player-a", {"name": "Nova", "real_life_event": False, "event_classification": "fictional"}, fictional=True
        )
        self.assertTrue(result["character_created"])

    def test_real_person_without_consent_is_rejected(self):
        lobby = RPLobby()
        with self.assertRaises(PermissionError):
            lobby.create_character(
                "player-a",
                {"name": "Portrayal", "real_life_event": False, "event_classification": "fictional"},
                real_people=("person-a",),
                scope="RP scene",
            )
        self.assertNotIn("player-a", lobby.players)

    def test_consent_must_match_person_and_scope(self):
        lobby = RPLobby()
        consent = Consent("person-a", "RP scene", explicit=True)
        result = lobby.create_character(
            "player-a",
            {"name": "Portrayal", "real_life_event": False, "event_classification": "fictional"},
            real_people=("person-a",),
            scope="RP scene",
            consents=(consent,),
        )
        self.assertTrue(result["character_created"])

    def test_wrong_scope_or_revoked_consent_is_rejected(self):
        lobby = RPLobby()
        for consent in (
            Consent("person-a", "Different scene", explicit=True),
            Consent("person-a", "RP scene", explicit=True, revoked=True),
        ):
            with self.subTest(consent=consent):
                with self.assertRaises(PermissionError):
                    lobby.create_character(
                        "player-a",
                        {"name": "Portrayal", "real_life_event": False, "event_classification": "fictional"},
                        real_people=("person-a",),
                        scope="RP scene",
                        consents=(consent,),
                    )


if __name__ == "__main__":
    unittest.main()
