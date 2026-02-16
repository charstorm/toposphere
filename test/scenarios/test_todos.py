"""
Scenario-based integration tests for Todos API.

These tests simulate complete user workflows through the todos API
to ensure all features work together correctly.
"""

from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from todos.models import TodoItem, TodoList


def get_tokens_for_user(user: Any) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class TodoWorkflowsTest(TestCase):  # type: ignore[misc]
    """
    Test complete todo management workflows for multiple users.

    Scenario: Bob and Alice sign up, create todo lists, manage items,
    mark tasks complete, and ensure data isolation between users.
    """

    def setUp(self) -> None:
        self.client = APIClient()
        self.base_url = "/api"
        self.bob_email = "bob@example.com"
        self.alice_email = "alice@example.com"
        self.bob_password = "BobPass123"
        self.alice_password = "AlicePass456"

    def test_complete_todo_workflows(self) -> None:
        """Execute Bob and Alice's complete todo workflows through the API."""

        # ============================================================================
        # PHASE 1: User Registration
        # ============================================================================
        print("\n=== Phase 1: User Registration ===")

        # Register Bob
        bob_register_data = {
            "email": self.bob_email,
            "password": self.bob_password,
            "first_name": "Bob",
            "last_name": "Builder",
        }
        response = self.client.post(
            f"{self.base_url}/auth/register/", bob_register_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bob_access_token = response.data["access"]
        bob_id = response.data["id"]
        print(f"✓ Registered Bob (ID: {bob_id})")

        # Register Alice
        alice_register_data = {
            "email": self.alice_email,
            "password": self.alice_password,
            "first_name": "Alice",
            "last_name": "Wonderland",
        }
        response = self.client.post(
            f"{self.base_url}/auth/register/", alice_register_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        alice_access_token = response.data["access"]
        alice_id = response.data["id"]
        print(f"✓ Registered Alice (ID: {alice_id})")

        # Verify users exist
        self.assertTrue(User.objects.filter(email=self.bob_email).exists())
        self.assertTrue(User.objects.filter(email=self.alice_email).exists())
        bob = User.objects.get(email=self.bob_email)
        alice = User.objects.get(email=self.alice_email)

        # ============================================================================
        # PHASE 2: Bob Creates Todo Lists
        # ============================================================================
        print("\n=== Phase 2: Bob Creates Todo Lists ===")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {bob_access_token}")

        # Create "Work Projects" list
        list1_data = {
            "title": "Work Projects",
            "description": "All work-related tasks and projects",
        }
        response = self.client.post(f"{self.base_url}/todos/", list1_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bob_work_list_id = response.data["id"]
        print(f"✓ Created 'Work Projects' list (ID: {bob_work_list_id})")

        # Create "Home Improvement" list
        list2_data = {
            "title": "Home Improvement",
            "description": "House repairs and improvements",
        }
        response = self.client.post(f"{self.base_url}/todos/", list2_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bob_home_list_id = response.data["id"]
        print(f"✓ Created 'Home Improvement' list (ID: {bob_home_list_id})")

        # Create list without description
        list3_data = {"title": "Grocery List"}
        response = self.client.post(f"{self.base_url}/todos/", list3_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bob_grocery_list_id = response.data["id"]
        print(f"✓ Created 'Grocery List' list (ID: {bob_grocery_list_id})")

        # Verify Bob has 3 lists
        self.assertEqual(TodoList.objects.filter(user=bob).count(), 3)

        # ============================================================================
        # PHASE 3: Bob Adds Items to Lists
        # ============================================================================
        print("\n=== Phase 3: Bob Adds Items to Lists ===")

        # Add items to Work Projects list
        work_items = [
            {"title": "Complete Q4 report", "description": "Due next Friday"},
            {"title": "Review team performance"},
            {"title": "Update project documentation"},
        ]
        work_item_ids = []
        for item in work_items:
            response = self.client.post(
                f"{self.base_url}/todos/{bob_work_list_id}/items/",
                item,
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            work_item_ids.append(response.data["id"])
            print(f"  ✓ Added work item: {item['title']}")

        # Add items to Home Improvement list
        home_items = [
            {"title": "Fix kitchen faucet"},
            {"title": "Paint living room walls"},
        ]
        home_item_ids = []
        for item in home_items:
            response = self.client.post(
                f"{self.base_url}/todos/{bob_home_list_id}/items/",
                item,
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            home_item_ids.append(response.data["id"])
            print(f"  ✓ Added home item: {item['title']}")

        # Add items to Grocery List
        grocery_items = [
            {"title": "Milk"},
            {"title": "Eggs"},
            {"title": "Bread"},
            {"title": "Coffee"},
        ]
        grocery_item_ids = []
        for item in grocery_items:
            response = self.client.post(
                f"{self.base_url}/todos/{bob_grocery_list_id}/items/",
                item,
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            grocery_item_ids.append(response.data["id"])
            print(f"  ✓ Added grocery item: {item['title']}")

        # Verify item counts
        self.assertEqual(TodoItem.objects.filter(todo_list_id=bob_work_list_id).count(), 3)
        self.assertEqual(TodoItem.objects.filter(todo_list_id=bob_home_list_id).count(), 2)
        self.assertEqual(TodoItem.objects.filter(todo_list_id=bob_grocery_list_id).count(), 4)

        # ============================================================================
        # PHASE 4: Bob Marks Items Complete
        # ============================================================================
        print("\n=== Phase 4: Bob Marks Items Complete ===")

        # Mark some grocery items as complete
        for item_id in grocery_item_ids[:2]:
            response = self.client.patch(
                f"{self.base_url}/todos/items/{item_id}/",
                {"is_completed": True},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data["is_completed"])
            self.assertIsNotNone(response.data["completed_at"])
            print(f"  ✓ Marked grocery item {item_id} as complete")

        # Verify completed status
        completed_count = TodoItem.objects.filter(
            todo_list_id=bob_grocery_list_id, is_completed=True
        ).count()
        self.assertEqual(completed_count, 2)

        # ============================================================================
        # PHASE 5: Alice Creates Her Own Todo Lists
        # ============================================================================
        print("\n=== Phase 5: Alice Creates Todo Lists ===")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {alice_access_token}")

        # Alice creates a personal goals list
        alice_list_data = {
            "title": "2026 Goals",
            "description": "Personal development goals for the year",
        }
        response = self.client.post(f"{self.base_url}/todos/", alice_list_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        alice_goals_list_id = response.data["id"]
        print(f"✓ Created '2026 Goals' list (ID: {alice_goals_list_id})")

        # Alice adds items to her goals list
        goals_items = [
            {"title": "Learn Python"},
            {"title": "Read 24 books"},
            {"title": "Travel to Japan"},
        ]
        for item in goals_items:
            response = self.client.post(
                f"{self.base_url}/todos/{alice_goals_list_id}/items/",
                item,
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            print(f"  ✓ Added goal item: {item['title']}")

        # ============================================================================
        # PHASE 6: Data Isolation Verification
        # ============================================================================
        print("\n=== Phase 6: Data Isolation Verification ===")

        # Bob lists his todo lists
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {bob_access_token}")
        response = self.client.get(f"{self.base_url}/todos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bob_list_count = len(response.data["results"])
        self.assertEqual(bob_list_count, 3)
        bob_list_titles = [lst["title"] for lst in response.data["results"]]
        self.assertIn("Work Projects", bob_list_titles)
        self.assertIn("Home Improvement", bob_list_titles)
        self.assertIn("Grocery List", bob_list_titles)
        print(f"✓ Bob sees {bob_list_count} lists: {bob_list_titles}")

        # Alice lists her todo lists
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {alice_access_token}")
        response = self.client.get(f"{self.base_url}/todos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        alice_list_count = len(response.data["results"])
        self.assertEqual(alice_list_count, 1)
        alice_list_titles = [lst["title"] for lst in response.data["results"]]
        self.assertIn("2026 Goals", alice_list_titles)
        print(f"✓ Alice sees {alice_list_count} list(s): {alice_list_titles}")

        # Bob tries to access Alice's list (should fail)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {bob_access_token}")
        response = self.client.get(f"{self.base_url}/todos/{alice_goals_list_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print("✓ Bob cannot access Alice's list (404)")

        # Alice tries to access Bob's list (should fail)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {alice_access_token}")
        response = self.client.get(f"{self.base_url}/todos/{bob_work_list_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print("✓ Alice cannot access Bob's list (404)")

        # ============================================================================
        # PHASE 7: Bob Updates Lists and Items
        # ============================================================================
        print("\n=== Phase 7: Bob Updates Lists and Items ===")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {bob_access_token}")

        # Update work list description
        update_data = {
            "title": "Work Projects Q4",
            "description": "Q4 work tasks and deliverables - Updated",
        }
        response = self.client.put(
            f"{self.base_url}/todos/{bob_work_list_id}/",
            update_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Work Projects Q4")
        print("✓ Updated work list title and description")

        # Partial update - only title
        patch_data = {"title": "Home Renovation"}
        response = self.client.patch(
            f"{self.base_url}/todos/{bob_home_list_id}/",
            patch_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Home Renovation")
        print("✓ Partially updated home list title only")

        # Update a work item
        update_item_data = {
            "title": "Complete Q4 report - URGENT",
            "description": "Due Monday morning - priority!",
        }
        response = self.client.put(
            f"{self.base_url}/todos/items/{work_item_ids[0]}/",
            update_item_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Complete Q4 report - URGENT")
        print("✓ Updated work item title and description")

        # Mark work item as complete
        response = self.client.patch(
            f"{self.base_url}/todos/items/{work_item_ids[0]}/",
            {"is_completed": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_completed"])
        print("✓ Marked updated work item as complete")

        # ============================================================================
        # PHASE 8: List Items with Filtering
        # ============================================================================
        print("\n=== Phase 8: List and Verify Items ===")

        # Get all items from work list
        response = self.client.get(f"{self.base_url}/todos/{bob_work_list_id}/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        completed_count = sum(1 for item in response.data["results"] if item["is_completed"])
        self.assertEqual(completed_count, 1)
        print(f"✓ Work list has 3 items, {completed_count} completed")

        # Get all items from grocery list
        response = self.client.get(f"{self.base_url}/todos/{bob_grocery_list_id}/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)
        completed_count = sum(1 for item in response.data["results"] if item["is_completed"])
        self.assertEqual(completed_count, 2)
        print(f"✓ Grocery list has 4 items, {completed_count} completed")

        # ============================================================================
        # PHASE 9: Bob Deletes Items and Lists
        # ============================================================================
        print("\n=== Phase 9: Bob Deletes Items and Lists ===")

        # Delete completed grocery items
        for item_id in grocery_item_ids[:2]:
            response = self.client.delete(f"{self.base_url}/todos/items/{item_id}/")
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            print(f"  ✓ Deleted grocery item {item_id}")

        # Verify items deleted
        response = self.client.get(f"{self.base_url}/todos/{bob_grocery_list_id}/items/")
        self.assertEqual(len(response.data["results"]), 2)
        print("✓ Grocery list now has 2 items")

        # Delete the entire grocery list (cascade deletes remaining items)
        response = self.client.delete(f"{self.base_url}/todos/{bob_grocery_list_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        print(f"✓ Deleted grocery list (ID: {bob_grocery_list_id})")

        # Verify grocery list and its items are gone
        self.assertFalse(TodoList.objects.filter(id=bob_grocery_list_id).exists())
        self.assertEqual(TodoItem.objects.filter(todo_list_id=bob_grocery_list_id).count(), 0)
        print("✓ Verified grocery list and all items deleted")

        # Verify Bob still has 2 lists
        response = self.client.get(f"{self.base_url}/todos/")
        self.assertEqual(len(response.data["results"]), 2)
        print("✓ Bob now has 2 lists")

        # ============================================================================
        # PHASE 10: Final Verification and Cleanup
        # ============================================================================
        print("\n=== Phase 10: Final Verification ===")

        # Verify database state
        self.assertEqual(TodoList.objects.filter(user=bob).count(), 2)
        self.assertEqual(TodoList.objects.filter(user=alice).count(), 1)

        total_bob_items = TodoItem.objects.filter(todo_list__user=bob).count()
        total_alice_items = TodoItem.objects.filter(todo_list__user=alice).count()
        self.assertEqual(total_bob_items, 5)  # 3 work + 2 home
        self.assertEqual(total_alice_items, 3)  # 3 goals

        print(f"✓ Final state: Bob has 2 lists with {total_bob_items} items")
        print(f"✓ Final state: Alice has 1 list with {total_alice_items} items")

        # Verify isolation: Alice still can't see Bob's lists
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {alice_access_token}")
        response = self.client.get(f"{self.base_url}/todos/")
        self.assertEqual(len(response.data["results"]), 1)
        print("✓ Alice's view unchanged (isolation maintained)")

        print("\n" + "=" * 60)
        print("✅ TODO WORKFLOWS TEST PASSED")
        print("=" * 60)
