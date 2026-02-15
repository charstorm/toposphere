"""
Scenario-based integration tests for Toposphere API.

These tests simulate complete user journeys through the API
to ensure all features work together correctly.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from notes.models import Note


class CompleteUserJourneyTest(TestCase):  # type: ignore[misc]
    """
    Test a complete user journey from registration to account deletion.

    Scenario: Alice signs up, creates notes, manages her profile,
    changes password, and eventually deletes her account.
    """

    def setUp(self) -> None:
        self.client = APIClient()
        self.base_url = "/api"
        self.user_email = "alice@example.com"
        self.initial_password = "SecurePass123"
        self.new_password = "NewSecurePass456"

    def test_complete_user_journey(self) -> None:
        """Execute Alice's complete journey through the API."""

        # ============================================================================
        # STEP 1: User Registration
        # ============================================================================
        print("\n=== Step 1: User Registration ===")
        register_data = {
            "email": self.user_email,
            "password": self.initial_password,
            "first_name": "Alice",
            "last_name": "Smith",
        }
        response = self.client.post(f"{self.base_url}/auth/register/", register_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("id", response.data)
        user_id = response.data["id"]
        auth_token = response.data["token"]
        print(f"✓ Registered user: {self.user_email} (ID: {user_id})")

        # Verify user exists in database
        self.assertTrue(User.objects.filter(email=self.user_email).exists())
        user = User.objects.get(email=self.user_email)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Smith")

        # ============================================================================
        # STEP 2: Initial Login
        # ============================================================================
        print("\n=== Step 2: Initial Login ===")
        login_data = {
            "email": self.user_email,
            "password": self.initial_password,
        }
        response = self.client.post(f"{self.base_url}/auth/login/", login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        auth_token = response.data["token"]  # Update token
        print("✓ Logged in successfully, received token")

        # Set authentication for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {auth_token}")

        # ============================================================================
        # STEP 3: Create Multiple Notes
        # ============================================================================
        print("\n=== Step 3: Creating Notes ===")

        # Create first note: Work ideas
        note1_data = {
            "title": "Work Project Ideas",
            "content": "1. Build a note-taking app\n2. Add AI features\n3. Create mobile version",
        }
        response = self.client.post(f"{self.base_url}/notes/", note1_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note1_id = response.data["id"]
        print(f"✓ Created note 1: 'Work Project Ideas' (ID: {note1_id})")

        # Create second note: Grocery list
        note2_data = {
            "title": "Grocery List",
            "content": "- Milk\n- Eggs\n- Bread\n- Coffee",
        }
        response = self.client.post(f"{self.base_url}/notes/", note2_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note2_id = response.data["id"]
        print(f"✓ Created note 2: 'Grocery List' (ID: {note2_id})")

        # Create third note: Meeting notes
        note3_data = {
            "title": "Team Meeting Notes",
            "content": "Discussed Q4 goals. Action items: Review budget, update roadmap.",
        }
        response = self.client.post(f"{self.base_url}/notes/", note3_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note3_id = response.data["id"]
        print(f"✓ Created note 3: 'Team Meeting Notes' (ID: {note3_id})")

        # Verify all notes exist
        self.assertEqual(Note.objects.filter(user=user).count(), 3)

        # ============================================================================
        # STEP 4: List and Search Notes
        # ============================================================================
        print("\n=== Step 4: List and Search Notes ===")

        # List all notes
        response = self.client.get(f"{self.base_url}/notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        print(f"✓ Listed all notes: {len(response.data['results'])} found")

        # Search for "work" (should match note 1)
        response = self.client.get(f"{self.base_url}/notes/?search=work")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Work Project Ideas")
        print(f"✓ Search for 'work': {len(response.data['results'])} match")

        # Search for "meeting" (should match note 3)
        response = self.client.get(f"{self.base_url}/notes/?search=meeting")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Team Meeting Notes")
        print(f"✓ Search for 'meeting': {len(response.data['results'])} match")

        # Search for common term (should match multiple)
        response = self.client.get(f"{self.base_url}/notes/?search=notes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # Only "Team Meeting Notes"
        print(f"✓ Search for 'notes': {len(response.data['results'])} match")

        # ============================================================================
        # STEP 5: Update a Note
        # ============================================================================
        print("\n=== Step 5: Update Note ===")

        update_data = {
            "title": "Team Meeting Notes - Updated",
            "content": (
                "Discussed Q4 goals.\n\n"
                "Action Items:\n"
                "1. Review budget by Friday\n"
                "2. Update roadmap\n"
                "3. Schedule follow-up"
            ),
        }
        response = self.client.put(f"{self.base_url}/notes/{note3_id}/", update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], update_data["title"])
        self.assertEqual(response.data["content"], update_data["content"])
        print(f"✓ Updated note {note3_id} with new content")

        # Verify update persisted
        note3 = Note.objects.get(id=note3_id)
        self.assertEqual(note3.title, "Team Meeting Notes - Updated")

        # Partial update test
        patch_data = {"title": "Q4 Team Meeting"}
        response = self.client.patch(
            f"{self.base_url}/notes/{note3_id}/", patch_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Q4 Team Meeting")
        print(f"✓ Patched note {note3_id} title only")

        # ============================================================================
        # STEP 6: Profile Management
        # ============================================================================
        print("\n=== Step 6: Profile Management ===")

        # View profile
        response = self.client.get(f"{self.base_url}/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user_email)
        self.assertEqual(response.data["first_name"], "Alice")
        self.assertEqual(response.data["last_name"], "Smith")
        self.assertIn("date_joined", response.data)
        print(f"✓ Viewed profile: {response.data['first_name']} {response.data['last_name']}")

        # Update profile
        profile_update = {
            "first_name": "Alice Marie",
            "last_name": "Johnson-Smith",
        }
        response = self.client.put(f"{self.base_url}/auth/profile/", profile_update, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Alice Marie")
        self.assertEqual(response.data["last_name"], "Johnson-Smith")
        self.assertEqual(response.data["email"], self.user_email)  # Unchanged
        print(f"✓ Updated profile: {response.data['first_name']} {response.data['last_name']}")

        # Verify in database
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Alice Marie")
        self.assertEqual(user.last_name, "Johnson-Smith")

        # ============================================================================
        # STEP 7: Password Change
        # ============================================================================
        print("\n=== Step 7: Password Change ===")

        # Attempt change with wrong old password
        wrong_pw_data = {
            "old_password": "WrongPassword123",
            "new_password": self.new_password,
        }
        response = self.client.post(
            f"{self.base_url}/auth/change-password/", wrong_pw_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("✓ Password change rejected with wrong old password")

        # Change password successfully
        change_pw_data = {
            "old_password": self.initial_password,
            "new_password": self.new_password,
        }
        response = self.client.post(
            f"{self.base_url}/auth/change-password/", change_pw_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password changed successfully.")
        print("✓ Password changed successfully")

        # Verify old password no longer works
        old_login_data = {
            "email": self.user_email,
            "password": self.initial_password,
        }
        response = self.client.post(f"{self.base_url}/auth/login/", old_login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("✓ Old password rejected on login")

        # Verify new password works
        new_login_data = {
            "email": self.user_email,
            "password": self.new_password,
        }
        response = self.client.post(f"{self.base_url}/auth/login/", new_login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        new_token = response.data["token"]
        print("✓ New password accepted on login")

        # Update auth token
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {new_token}")

        # ============================================================================
        # STEP 8: Delete a Note
        # ============================================================================
        print("\n=== Step 8: Delete Note ===")

        # Delete the grocery list (completed)
        response = self.client.delete(f"{self.base_url}/notes/{note2_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        print(f"✓ Deleted note {note2_id} (Grocery List)")

        # Verify deletion
        self.assertEqual(Note.objects.filter(user=user).count(), 2)
        self.assertFalse(Note.objects.filter(id=note2_id).exists())
        print("✓ Verified note deleted from database")

        # Verify remaining notes
        response = self.client.get(f"{self.base_url}/notes/")
        self.assertEqual(len(response.data["results"]), 2)
        remaining_titles = [n["title"] for n in response.data["results"]]
        self.assertIn("Work Project Ideas", remaining_titles)
        self.assertIn("Q4 Team Meeting", remaining_titles)
        print("✓ Confirmed remaining notes intact")

        # ============================================================================
        # STEP 9: Account Cleanup (Delete Account)
        # ============================================================================
        print("\n=== Step 9: Account Deletion ===")

        # Attempt deletion without password
        response = self.client.post(f"{self.base_url}/auth/delete-account/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("✓ Account deletion rejected without password")

        # Attempt deletion with wrong password
        wrong_delete_data = {"password": "WrongPassword123"}
        response = self.client.post(
            f"{self.base_url}/auth/delete-account/", wrong_delete_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("✓ Account deletion rejected with wrong password")

        # Delete account successfully
        delete_data = {"password": self.new_password}
        response = self.client.post(
            f"{self.base_url}/auth/delete-account/", delete_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Account deleted successfully.")
        print("✓ Account deleted successfully")

        # ============================================================================
        # STEP 10: Verify Cleanup
        # ============================================================================
        print("\n=== Step 10: Verify Cleanup ===")

        # Verify user no longer exists
        self.assertFalse(User.objects.filter(email=self.user_email).exists())
        print("✓ User removed from database")

        # Verify user's notes are deleted (cascade)
        self.assertEqual(Note.objects.filter(user__email=self.user_email).count(), 0)
        print("✓ All user notes removed from database")

        # Verify cannot login anymore (clear credentials first)
        self.client.credentials()  # Clear auth token
        response = self.client.post(f"{self.base_url}/auth/login/", new_login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("✓ Login rejected for deleted account")

        # Verify token no longer works
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {new_token}")
        response = self.client.get(f"{self.base_url}/notes/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✓ Old token rejected for deleted account")

        print("\n" + "=" * 60)
        print("✅ COMPLETE USER JOURNEY TEST PASSED")
        print("=" * 60)
