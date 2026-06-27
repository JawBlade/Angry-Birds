import math
import pytest
from project import distance, snap_check, grab


# ── Tests for distance() ──────────────────────────────────────────────────────

def test_distance_zero():
    """Same point should give distance 0."""
    assert distance((0, 0), (0, 0)) == 0

def test_distance_horizontal():
    assert distance((0, 0), (5, 0)) == 5

def test_distance_vertical():
    assert distance((0, 0), (0, 3)) == 3

def test_distance_diagonal():
    # 3-4-5 right triangle
    assert distance((0, 0), (3, 4)) == 5

def test_distance_negative_coords():
    assert distance((-1, -1), (2, 3)) == pytest.approx(5.0)


# ── Tests for snap_check() ────────────────────────────────────────────────────

class FakeBody:
    """Minimal stand-in for a pymunk body so we don't need pygame/pymunk."""
    def __init__(self, x, y):
        self.position = (x, y)
        self.velocity = (100, 100)


def test_snap_check_not_released():
    """If released=False, nothing should change and False is returned."""
    body = FakeBody(225, 410)
    result = snap_check(body, released=False)
    assert result == False

def test_snap_check_within_radius():
    """Bird inside snap radius while released → snapped back, returns False."""
    body = FakeBody(230, 415)          # close to (225, 410)
    result = snap_check(body, released=True, SLINGSHOT_POS=(225, 410))
    assert result == False
    assert body.position == (225, 410)
    assert body.velocity == (0, 0)

def test_snap_check_outside_radius():
    """Bird outside snap radius while released → still released, returns True."""
    body = FakeBody(400, 200)          # far from (225, 410)
    result = snap_check(body, released=True, SLINGSHOT_POS=(225, 410))
    assert result == True


# ── Tests for grab() ──────────────────────────────────────────────────────────

def test_grab_close_enough():
    """Mouse within grab radius and bird not released/launched → True."""
    body = FakeBody(100, 100)
    result = grab((110, 110), body, released=False, launch=False)
    assert result == True

def test_grab_too_far():
    """Mouse too far away → False."""
    body = FakeBody(100, 100)
    result = grab((300, 300), body, released=False, launch=False)
    assert result == False

def test_grab_already_released():
    """Can't grab a bird that's already released."""
    body = FakeBody(100, 100)
    result = grab((101, 101), body, released=True, launch=False)
    assert result == False

def test_grab_already_launched():
    """Can't grab a bird that's already launched."""
    body = FakeBody(100, 100)
    result = grab((101, 101), body, released=False, launch=True)
    assert result == False