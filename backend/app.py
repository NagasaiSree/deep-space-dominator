# backend/app.py - Railway Deployment Ready Version

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from segment_tree import SegmentTree
import traceback
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for both local development and production
# Allow all origins during development, restrict in production
CORS(app, origins=[
    'http://localhost:5500',
    'http://127.0.0.1:5500',
    'http://localhost:5000',
    'http://127.0.0.1:5000',
    'https://your-frontend-domain.com',  # Replace with your frontend URL
    'https://deep-space-dominator.vercel.app',  # Example Vercel frontend
    'https://deep-space-dominator.netlify.app',  # Example Netlify frontend
    '*'  # Remove this in production - allows all origins (temporary)
])

# Initialize with cosmic signal data
initial_array = [5.2, 2.7, 7.1, 3.8, 9.4, 1.3, 8.6, 4.2, 6.5, 2.9]
initial_array = [float(x) for x in initial_array]

# Create segment tree
try:
    seg_tree = SegmentTree(initial_array)
    print("✅ Segment tree created successfully")
except Exception as e:
    print(f"❌ Error creating segment tree: {e}")
    seg_tree = None

# Get port from environment variable (Railway sets this automatically)
port = int(os.environ.get('PORT', 5000))

print("\n" + "="*60)
print("🚀 DEEP SPACE DOMINATOR 3000 - BACKEND")
print("="*60)
print(f"📡 Receivers: {len(initial_array)}")
print(f"📊 Values: {initial_array}")
print(f"🌐 Server: http://0.0.0.0:{port}")
print(f"🔧 Environment: {'Production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Development'}")
print("="*60 + "\n")

@app.after_request
def after_request(response):
    """Add CORS headers to every response (additional security)"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    """API home endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'status': 'online',
        'mission': 'Deep Space Dominator 3000',
        'data_structure': 'Segment Tree',
        'receivers': len(initial_array),
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'development'),
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'GET /': 'This information',
            'GET /array': 'Current receiver values',
            'POST /update': 'Update receiver frequency',
            'GET /query': 'Query range statistics',
            'GET /stats': 'Full array statistics',
            'POST /resize': 'Change number of receivers',
            'GET /health': 'Health check'
        }
    })

@app.route('/array', methods=['GET', 'OPTIONS'])
def get_array():
    """Return current array values"""
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'array': [float(x) for x in initial_array],
        'size': len(initial_array),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/update', methods=['POST', 'OPTIONS'])
def update():
    """Update value at specific index"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if 'index' not in data:
            return jsonify({'error': 'Missing index parameter'}), 400
        
        if 'value' not in data:
            return jsonify({'error': 'Missing value parameter'}), 400
        
        idx = int(data['index'])
        value = float(data['value'])
        
        if idx < 0 or idx >= len(initial_array):
            return jsonify({
                'error': f'Index must be between 0 and {len(initial_array)-1}'
            }), 400
        
        # Store old value
        old_value = initial_array[idx]
        
        # Update array and segment tree
        initial_array[idx] = value
        
        if seg_tree:
            seg_tree.update(idx, value)
        
        print(f"✅ Updated [{idx}]: {old_value:.2f} → {value:.2f}")
        
        return jsonify({
            'success': True,
            'message': 'Update successful',
            'index': idx,
            'old_value': float(old_value),
            'new_value': float(value),
            'array': [float(x) for x in initial_array],
            'size': len(initial_array),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        print(f"❌ Error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/query', methods=['GET', 'OPTIONS'])
def query():
    """Query statistics for range [L, R]"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        L = request.args.get('L')
        R = request.args.get('R')
        
        if L is None:
            return jsonify({'error': 'Missing L parameter'}), 400
        
        if R is None:
            return jsonify({'error': 'Missing R parameter'}), 400
        
        L = int(L)
        R = int(R)
        
        if L < 0:
            return jsonify({'error': 'L cannot be negative'}), 400
        
        if R >= len(initial_array):
            return jsonify({
                'error': f'R must be less than {len(initial_array)}'
            }), 400
        
        if L > R:
            return jsonify({'error': 'L must be less than or equal to R'}), 400
        
        # Get statistics from segment tree
        if seg_tree:
            stats = seg_tree.get_stats(L, R)
        else:
            # Fallback to direct calculation
            subset = initial_array[L:R+1]
            min_val = min(subset)
            max_val = max(subset)
            mean_val = sum(subset) / len(subset)
            sum_sq = sum(x*x for x in subset)
            variance = (sum_sq/len(subset)) - (mean_val*mean_val)
            stats = {
                'min': round(float(min_val), 4),
                'max': round(float(max_val), 4),
                'mean': round(float(mean_val), 4),
                'variance': round(float(abs(variance)), 4)
            }
        
        # Add range information
        stats['range'] = {'L': L, 'R': R}
        stats['length'] = R - L + 1
        stats['total_receivers'] = len(initial_array)
        stats['timestamp'] = datetime.utcnow().isoformat()
        
        return jsonify(stats)
        
    except ValueError as e:
        return jsonify({'error': f'L and R must be integers: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/resize', methods=['POST', 'OPTIONS'])
def resize():
    """Change the number of receivers"""
    if request.method == 'OPTIONS':
        return '', 200
    
    global seg_tree, initial_array
    
    try:
        data = request.get_json()
        
        if not data or 'size' not in data:
            return jsonify({'error': 'Missing size parameter'}), 400
        
        new_size = int(data['size'])
        default_value = float(data.get('default_value', 0.0))
        
        if new_size < 1 or new_size > 100:
            return jsonify({'error': 'Size must be between 1 and 100'}), 400
        
        old_size = len(initial_array)
        
        if seg_tree:
            initial_array = seg_tree.resize(new_size, default_value)
        else:
            if new_size > old_size:
                initial_array.extend([default_value] * (new_size - old_size))
            else:
                initial_array = initial_array[:new_size]
            seg_tree = SegmentTree(initial_array)
        
        print(f"📏 Resized from {old_size} to {new_size} receivers")
        
        return jsonify({
            'success': True,
            'message': f'Array resized from {old_size} to {new_size}',
            'old_size': old_size,
            'new_size': new_size,
            'array': [float(x) for x in initial_array],
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET', 'OPTIONS'])
def full_stats():
    """Get statistics for entire array"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if seg_tree:
            stats = seg_tree.get_stats(0, len(initial_array) - 1)
        else:
            subset = initial_array
            min_val = min(subset)
            max_val = max(subset)
            mean_val = sum(subset) / len(subset)
            sum_sq = sum(x*x for x in subset)
            variance = (sum_sq/len(subset)) - (mean_val*mean_val)
            stats = {
                'min': round(float(min_val), 4),
                'max': round(float(max_val), 4),
                'mean': round(float(mean_val), 4),
                'variance': round(float(abs(variance)), 4)
            }
        
        stats['array_size'] = len(initial_array)
        stats['full_array'] = True
        stats['timestamp'] = datetime.utcnow().isoformat()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    """Health check endpoint - Railway uses this to verify app is running"""
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'receivers': len(initial_array),
        'segment_tree_working': seg_tree is not None,
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'development')
    })

@app.route('/debug', methods=['GET', 'OPTIONS'])
def debug():
    """Debug endpoint - shows internal state"""
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'array': [float(x) for x in initial_array],
        'size': len(initial_array),
        'types': [type(x).__name__ for x in initial_array],
        'segment_tree_exists': seg_tree is not None,
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'development')
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    # Run the app on all available interfaces
    app.run(
        host='0.0.0.0',  # Important: Listen on all interfaces
        port=port,
        debug=False      # Always False in production
    )