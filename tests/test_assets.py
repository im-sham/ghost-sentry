"""Unit tests for asset assignment."""
from ghost_sentry.core import assets

def test_asset_assignment_proximity():
    """Test that the closest available asset is assigned to a target."""
    # Target near drone-alpha (33.94, -118.41)
    target_loc = (33.941, -118.411)
    
    available = assets.get_available_assets()
    assigned = assets.assign_asset(target_loc, available)
    
    assert assigned is not None
    assert assigned.id == "drone-alpha"


def test_asset_assignment_empty_fleet():
    """Test handling of empty asset list."""
    target_loc = (33.94, -118.41)
    assigned = assets.assign_asset(target_loc, [])
    assert assigned is None

def test_score_priority_battery():
    """Test that battery life impacts scoring (farther drone with more battery wins)."""
    # Create two assets
    # Asset A: Close (dist 0.01), low battery (0.1)
    # Asset B: Far (dist 0.03), high battery (1.0)
    asset_a = assets.Asset("low-bat", "UAV", (33.94, -118.41), battery=0.1, signal=1.0)
    asset_b = assets.Asset("high-bat", "UAV", (33.95, -118.42), battery=1.0, signal=1.0)
    
    target = (33.94, -118.41)
    
    score_a = assets.score_asset(asset_a, assets.Point(target))
    score_b = assets.score_asset(asset_b, assets.Point(target))
    
    # Even though A is closer, B should have a higher score due to battery (30% weight)
    assert score_b > score_a

def test_score_priority_signal():
    """Test that signal strength impacts scoring."""
    # Asset A: Perfect signal (1.0), Asset B: Weak signal (0.3)
    # Both same distance
    asset_a = assets.Asset("good-sig", "UAV", (33.94, -118.41), battery=1.0, signal=1.0)
    asset_b = assets.Asset("bad-sig", "UAV", (33.94, -118.41), battery=1.0, signal=0.3)
    
    target = (33.94, -118.41)
    
    score_a = assets.score_asset(asset_a, assets.Point(target))
    score_b = assets.score_asset(asset_b, assets.Point(target))
    
    assert score_a > score_b
