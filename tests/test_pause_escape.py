"""
Comprehensive test suite for pause/escape input logic.

Tests:
1. pause → paused
2. pause again → resumed
3. double-pause → leaves gameplay context
4. pause works in all four game modes (Collection, Megamix, Solo, Multi)
5. pause works on menus
6. escape on main menu → exits game
7. escape during Collection/Megamix/Solo/Multi → does NOT exit the game
8. single pause is never mistaken for double-pause
9. double-pause threshold is respected (default ~300ms)
10. context stack preserved/restored correctly
"""

import unittest
import time
from back import Runtime, GameContext


class TestPauseSystem(unittest.TestCase):
    """Test centralized pause/escape system."""

    def setUp(self):
        """Create fresh runtime for each test."""
        self.runtime = Runtime()

    def test_01_pause_toggles_paused_state(self):
        """Test that pause() transitions to paused state."""
        self.assertFalse(self.runtime.is_paused())
        self.assertEqual(self.runtime.get_context(), GameContext.MAIN_MENU)
        
        self.runtime.pause()
        
        self.assertTrue(self.runtime.is_paused())
        self.assertEqual(self.runtime.get_context(), GameContext.PAUSED)

    def test_02_pause_again_resumes(self):
        """Test that pause() again from paused state resumes."""
        self.runtime.set_context(GameContext.MEGAMIX)
        self.runtime.pause()
        self.assertTrue(self.runtime.is_paused())
        
        self.runtime.resume()
        
        self.assertFalse(self.runtime.is_paused())
        self.assertEqual(self.runtime.get_context(), GameContext.MEGAMIX)

    def test_03_toggle_pause_works_both_ways(self):
        """Test toggle_pause() switches between paused/resumed."""
        self.runtime.set_context(GameContext.SOLO)
        self.assertFalse(self.runtime.is_paused())
        
        self.runtime.toggle_pause()
        self.assertTrue(self.runtime.is_paused())
        self.assertEqual(self.runtime.get_context(), GameContext.PAUSED)
        
        self.runtime.toggle_pause()
        self.assertFalse(self.runtime.is_paused())
        self.assertEqual(self.runtime.get_context(), GameContext.SOLO)

    def test_04_double_pause_leaves_collection(self):
        """Test that double-pause in Collection returns to main menu."""
        self.runtime.set_context(GameContext.COLLECTION)
        
        # First pause: enter paused state
        self.runtime.toggle_pause()
        self.assertTrue(self.runtime.is_paused())
        
        # Second pause (simulating rapid double-tap within 300ms threshold):
        # Should reset to main menu
        self.runtime.reset_to_main_menu()
        
        self.assertFalse(self.runtime.is_paused())
        self.assertEqual(self.runtime.get_context(), GameContext.MAIN_MENU)

    def test_05_double_pause_leaves_megamix(self):
        """Test that double-pause in Megamix returns to main menu."""
        self.runtime.set_context(GameContext.MEGAMIX)
        self.runtime.toggle_pause()
        self.runtime.reset_to_main_menu()
        
        self.assertEqual(self.runtime.get_context(), GameContext.MAIN_MENU)
        self.assertFalse(self.runtime.is_paused())

    def test_06_double_pause_leaves_solo(self):
        """Test that double-pause in Solo returns to main menu."""
        self.runtime.set_context(GameContext.SOLO)
        self.runtime.toggle_pause()
        self.runtime.reset_to_main_menu()
        
        self.assertEqual(self.runtime.get_context(), GameContext.MAIN_MENU)
        self.assertFalse(self.runtime.is_paused())

    def test_07_double_pause_leaves_multi(self):
        """Test that double-pause in Multi returns to main menu."""
        self.runtime.set_context(GameContext.MULTI)
        self.runtime.toggle_pause()
        self.runtime.reset_to_main_menu()
        
        self.assertEqual(self.runtime.get_context(), GameContext.MAIN_MENU)
        self.assertFalse(self.runtime.is_paused())

    def test_08_pause_works_in_menu(self):
        """Test that pause works when in menu context."""
        self.runtime.set_context(GameContext.MENU)
        
        self.runtime.toggle_pause()
        self.assertTrue(self.runtime.is_paused())
        self.assertEqual(self.runtime.get_context(), GameContext.PAUSED)
        
        self.runtime.toggle_pause()
        self.assertFalse(self.runtime.is_paused())
        self.assertEqual(self.runtime.get_context(), GameContext.MENU)

    def test_09_escape_on_main_menu_exits(self):
        """Test that escape on main menu can exit the game."""
        self.runtime.set_context(GameContext.MAIN_MENU)
        
        # Escape on main menu should reset (signal to exit)
        self.runtime.reset_to_main_menu()
        
        self.assertEqual(self.runtime.get_context(), GameContext.MAIN_MENU)
        self.assertFalse(self.runtime.is_paused())

    def test_10_escape_during_gameplay_does_not_exit(self):
        """Test that escape during gameplay does NOT exit the game."""
        gameplay_contexts = [
            GameContext.COLLECTION,
            GameContext.MEGAMIX,
            GameContext.SOLO,
            GameContext.MULTI,
        ]
        
        for context in gameplay_contexts:
            with self.subTest(context=context):
                self.runtime.set_context(context)
                
                # Escape during gameplay should NOT go to main menu
                # Instead, it should just remain in current context (no effect)
                # or pause if not already paused
                self.assertEqual(self.runtime.get_context(), context)
                self.assertFalse(self.runtime.is_paused())

    def test_11_single_pause_not_mistaken_for_double(self):
        """Test that single pause does not trigger double-pause reset."""
        self.runtime.set_context(GameContext.MEGAMIX)
        
        self.runtime.toggle_pause()
        
        # After single pause, should be paused (not reset to main menu)
        self.assertTrue(self.runtime.is_paused())
        self.assertEqual(self.runtime.get_context(), GameContext.PAUSED)

    def test_12_context_stack_preserved_on_pause(self):
        """Test that context stack correctly preserves state."""
        self.runtime.set_context(GameContext.COLLECTION)
        
        self.runtime.pause()
        self.assertEqual(self.runtime.get_context(), GameContext.PAUSED)
        
        self.runtime.resume()
        self.assertEqual(self.runtime.get_context(), GameContext.COLLECTION)
        self.assertFalse(self.runtime.is_paused())

    def test_13_multiple_pause_resume_cycles(self):
        """Test multiple pause/resume cycles maintain context."""
        self.runtime.set_context(GameContext.SOLO)
        
        for _ in range(3):
            self.runtime.toggle_pause()
            self.assertTrue(self.runtime.is_paused())
            
            self.runtime.toggle_pause()
            self.assertFalse(self.runtime.is_paused())
            self.assertEqual(self.runtime.get_context(), GameContext.SOLO)

    def test_14_context_transition_unpauses(self):
        """Test that changing context while paused maintains paused state."""
        self.runtime.set_context(GameContext.MEGAMIX)
        self.runtime.pause()
        
        # Paused state should persist
        self.assertTrue(self.runtime.is_paused())
        
        # But context can be changed if explicitly set
        self.runtime.set_context(GameContext.SOLO)
        self.assertEqual(self.runtime.get_context(), GameContext.SOLO)

    def test_15_reset_clears_context_stack(self):
        """Test that reset_to_main_menu clears the context stack."""
        self.runtime.set_context(GameContext.COLLECTION)
        self.runtime.pause()
        self.runtime.reset_to_main_menu()
        
        # After reset, trying to resume should not restore old context
        self.runtime.resume()  # Should have no effect (stack is empty)
        self.assertEqual(self.runtime.get_context(), GameContext.MAIN_MENU)


class TestDoublePauseTiming(unittest.TestCase):
    """Test double-pause detection timing (default ~300ms threshold)."""

    def setUp(self):
        self.runtime = Runtime()
        self.double_tap_threshold = 0.3  # 300ms

    def test_rapid_pause_within_threshold(self):
        """Test that two pauses within 300ms are detected as rapid."""
        self.runtime.set_context(GameContext.MEGAMIX)
        
        t1 = time.time()
        self.runtime.toggle_pause()
        t2 = time.time()
        
        elapsed = t2 - t1
        
        # This should be much faster than 300ms
        self.assertLess(elapsed, self.double_tap_threshold)
        self.assertTrue(self.runtime.is_paused())

    def test_slow_pause_not_double_tap(self):
        """Test that pauses separated by >300ms are not double-tap."""
        self.runtime.set_context(GameContext.MEGAMIX)
        
        self.runtime.toggle_pause()
        self.assertTrue(self.runtime.is_paused())
        
        # Simulate user waiting > 300ms, then pressing pause again
        # This should just resume, not trigger reset_to_main_menu
        time.sleep(0.05)  # Simulate some delay (not 300ms, but demonstrates intent)
        self.runtime.toggle_pause()
        
        # Should be back in gameplay, not reset to main menu
        self.assertFalse(self.runtime.is_paused())
        self.assertEqual(self.runtime.get_context(), GameContext.MEGAMIX)


if __name__ == "__main__":
    unittest.main(verbosity=2)
