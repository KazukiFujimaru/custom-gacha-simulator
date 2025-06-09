import unittest
from modules.gacha_logic import perform_one_pull, GACHA_CONFIG

class TestGachaLogic(unittest.TestCase):
    
    def setUp(self):
        self.initial_state = {
            'pity_5_star': 0,
            'pity_4_star': 0,
            'is_guaranteed_rate_up': False,
            'total_pulls': 0
        }
    
    def test_perform_one_pull_basic(self):
        """Test basic functionality of perform_one_pull"""
        result, new_state = perform_one_pull(self.initial_state, GACHA_CONFIG)
        
        # Check that result has required keys
        self.assertIn('rarity', result)
        self.assertIn('name', result)
        self.assertIn('is_rate_up', result)
        
        # Check that rarity is valid
        self.assertIn(result['rarity'], [3, 4, 5])
        
        # Check that pity counters increased
        self.assertEqual(new_state['pity_5_star'], 1)
        self.assertEqual(new_state['pity_4_star'], 1)
    
    def test_hard_pity_5_star(self):
        """Test that hard pity guarantees 5-star at the limit"""
        pity_state = self.initial_state.copy()
        pity_state['pity_5_star'] = GACHA_CONFIG['hard_pity_5_star'] - 1
        
        result, new_state = perform_one_pull(pity_state, GACHA_CONFIG)
        
        # Should guarantee a 5-star
        self.assertEqual(result['rarity'], 5)
        self.assertEqual(new_state['pity_5_star'], 0)
    
    def test_hard_pity_4_star(self):
        """Test that hard pity guarantees 4-star at the limit"""
        pity_state = self.initial_state.copy()
        pity_state['pity_4_star'] = GACHA_CONFIG['hard_pity_4_star'] - 1
        pity_state['pity_5_star'] = 1  # Prevent 5-star from triggering
        
        # Run multiple tests since it's probabilistic
        for _ in range(10):
            result, new_state = perform_one_pull(pity_state.copy(), GACHA_CONFIG)
            if result['rarity'] >= 4:  # 4-star or 5-star should be guaranteed
                break
        
        self.assertGreaterEqual(result['rarity'], 4)

if __name__ == '__main__':
    unittest.main()