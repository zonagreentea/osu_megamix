import unittest

from portrayal_consent import Consent, authorize_portrayal


class PortrayalConsentTests(unittest.TestCase):
    def test_fictional_content_needs_no_real_person_consent(self):
        self.assertTrue(authorize_portrayal((), "ball_skit"))

    def test_missing_consent_denies_portrayal(self):
        self.assertFalse(
            authorize_portrayal(("person-1",), "ball_skit")
        )

    def test_explicit_consent_allows_matching_use(self):
        consent = Consent("person-1", "ball_skit", True)
        self.assertTrue(
            authorize_portrayal(
                ("person-1",), "ball_skit", (consent,)
            )
        )

    def test_consent_for_another_use_is_insufficient(self):
        consent = Consent("person-1", "private_scene", True)
        self.assertFalse(
            authorize_portrayal(
                ("person-1",), "public_skit", (consent,)
            )
        )

    def test_revoked_consent_denies_portrayal(self):
        consent = Consent("person-1", "ball_skit", True, revoked=True)
        self.assertFalse(
            authorize_portrayal(
                ("person-1",), "ball_skit", (consent,)
            )
        )

    def test_every_person_needs_consent(self):
        consent = Consent("person-1", "ball_skit", True)
        self.assertFalse(
            authorize_portrayal(
                ("person-1", "person-2"),
                "ball_skit",
                (consent,),
            )
        )

    def test_unconfirmed_consent_is_denied(self):
        consent = Consent("person-1", "ball_skit", False)
        self.assertFalse(
            authorize_portrayal(
                ("person-1",), "ball_skit", (consent,)
            )
        )


if __name__ == "__main__":
    unittest.main()
