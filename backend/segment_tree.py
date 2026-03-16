# backend/segment_tree.py

class Node:
    """Node structure for Segment Tree storing statistical data"""
    def __init__(self, min_val=float('inf'), max_val=float('-inf'), 
                 sum_val=0, sum_sq=0, count=0):
        self.min = min_val
        self.max = max_val
        self.sum = sum_val
        self.sum_sq = sum_sq
        self.count = count

class SegmentTree:
    """Segment Tree for range queries with updates"""
    
    def __init__(self, arr):
        """Initialize segment tree with given array"""
        self.arr = arr.copy()
        self.n = len(arr)
        self.tree = [None] * (4 * self.n)
        self._build(1, 0, self.n - 1)
        print(f"✅ Segment Tree built for {self.n} receivers")
    
    def _build(self, node, left, right):
        """Build tree recursively"""
        if left == right:
            val = self.arr[left]
            self.tree[node] = Node(val, val, val, val * val, 1)
            return
        
        mid = (left + right) // 2
        self._build(node * 2, left, mid)
        self._build(node * 2 + 1, mid + 1, right)
        
        # Merge children
        self.tree[node] = self._merge(
            self.tree[node * 2],
            self.tree[node * 2 + 1]
        )
    
    def _merge(self, left, right):
        """Merge two nodes to compute parent statistics"""
        if left is None:
            return right
        if right is None:
            return left
        
        return Node(
            min(left.min, right.min),
            max(left.max, right.max),
            left.sum + right.sum,
            left.sum_sq + right.sum_sq,
            left.count + right.count
        )
    
    def update(self, idx, value, node=1, left=0, right=None):
        """Update value at given index"""
        if right is None:
            right = self.n - 1
        
        if left == right:
            self.arr[idx] = value
            self.tree[node] = Node(value, value, value, value * value, 1)
            return
        
        mid = (left + right) // 2
        if idx <= mid:
            self.update(idx, value, node * 2, left, mid)
        else:
            self.update(idx, value, node * 2 + 1, mid + 1, right)
        
        # Recompute after update
        self.tree[node] = self._merge(
            self.tree[node * 2],
            self.tree[node * 2 + 1]
        )
    
    def query(self, L, R, node=1, left=0, right=None):
        """Query range [L, R]"""
        if right is None:
            right = self.n - 1
        
        # No overlap
        if R < left or L > right:
            return None
        
        # Total overlap
        if L <= left and right <= R:
            return self.tree[node]
        
        # Partial overlap
        mid = (left + right) // 2
        left_res = self.query(L, R, node * 2, left, mid)
        right_res = self.query(L, R, node * 2 + 1, mid + 1, right)
        
        return self._merge(left_res, right_res)
    
    def get_stats(self, L, R):
        """Get statistics for range [L, R]"""
        result = self.query(L, R)
        
        if result is None or result.count == 0:
            return {
                'min': 0.0,
                'max': 0.0,
                'mean': 0.0,
                'variance': 0.0
            }
        
        # Calculate statistics
        mean = result.sum / result.count
        variance = (result.sum_sq / result.count) - (mean * mean)
        
        # Handle floating point errors
        if variance < 0 and variance > -0.000001:
            variance = 0.0
        
        return {
            'min': round(float(result.min), 4),
            'max': round(float(result.max), 4),
            'mean': round(float(mean), 4),
            'variance': round(float(abs(variance)), 4)
        }
    
    def resize(self, new_size, default_value=0.0):
        """Resize the array and rebuild tree"""
        if new_size == self.n:
            return self.arr.copy()
        
        # Create new array
        if new_size > self.n:
            new_arr = self.arr.copy() + [default_value] * (new_size - self.n)
        else:
            new_arr = self.arr[:new_size]
        
        # Update instance variables
        self.arr = new_arr
        self.n = new_size
        self.tree = [None] * (4 * self.n)
        self._build(1, 0, self.n - 1)
        print(f"📏 Tree resized to {self.n} receivers")
        
        return new_arr