from point import p
from segment import s
from shape import shape
from polygon import polygon

def test_point(): assert p(42) == 42
def test_segment(): assert s(10, 25) == 15
def test_segment_order(): assert s(25, 10) == s(10, 25)
def test_segment_zero(): assert s(10, 10) == 0
def test_shape(): assert shape([1, 2, 3]) == 3
def test_shape_empty(): assert shape([]) == 0
def test_polygon(): assert polygon([1, 2, 3]) == 3
def test_polygon_empty(): assert polygon([]) == 0
