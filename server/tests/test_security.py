import unittest

from utils.security import hash_password, is_password_hash, verify_password


class PasswordSecurityTests(unittest.TestCase):
    def test_passwords_are_salted_and_verified(self):
        first_hash = hash_password("correct horse battery staple")
        second_hash = hash_password("correct horse battery staple")

        self.assertNotEqual(first_hash, "correct horse battery staple")
        self.assertNotEqual(first_hash, second_hash)
        self.assertTrue(is_password_hash(first_hash))
        self.assertTrue(verify_password("correct horse battery staple", first_hash))
        self.assertFalse(verify_password("wrong password", first_hash))

    def test_legacy_plaintext_password_can_be_verified_for_upgrade(self):
        self.assertFalse(is_password_hash("legacy-password"))
        self.assertTrue(verify_password("legacy-password", "legacy-password"))
        self.assertFalse(verify_password("wrong-password", "legacy-password"))

    def test_malformed_hash_is_rejected(self):
        self.assertFalse(verify_password("password", "pbkdf2_sha256$invalid"))


if __name__ == "__main__":
    unittest.main()
