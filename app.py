from flask import Flask, request, jsonifyfrom flask import Flask, request, jsonify

import kociembaimport kociemba



app = Flask(__name__)app = Flask(__name__)



@app.route("/solve", methods=["POST"])@app.route("/solve", methods=["POST"])

def solve_cube():def solve_cube():

    """    """

    Expects JSON payload:    Solve a Rubik's cube given its current state

    {    

        "cube": "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"    Expected JSON payload:

    }    {

    """        "state": "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

    data = request.get_json()    }

    

    if not data or "cube" not in data:    Returns:

        return jsonify({"error": "Missing 'cube' in request body"}), 400    {

        "success": true,

    cube_state = data["cube"]        "solution": "R U R' U' R' F R2 U' R' U' R U R' F'",

        "moves": 14,

    # Validate cube string length        "state": "original_state"

    if len(cube_state) != 54:    }

        return jsonify({"error": "Cube state must be 54 characters long"}), 400    """

    try:

    try:        # Get JSON data from request

        solution = kociemba.solve(cube_state)        data = request.get_json()

        return jsonify({"solution": solution})        print(f"📨 Received request data: {data}")

    except Exception as e:        

        return jsonify({"error": str(e)}), 400        if not data:

            print("❌ No JSON data provided")

            return jsonify({

@app.route("/", methods=["GET"])                "success": False,

def home():                "error": "No JSON data provided"

    return jsonify({            }), 400

        "message": "Rubik's Cube Solver API",        

        "usage": {        # Extract cube state

            "endpoint": "/solve",        cube_state = data.get('state', '').strip().upper()

            "method": "POST",        print(f"🧊 Cube state: {cube_state}")

            "body": {        print(f"📏 Cube state length: {len(cube_state)}")

                "cube": "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"        

            }        # Validate cube state

        }        if not cube_state:

    })            print("❌ No cube state provided")

            return jsonify({

                "success": False,

if __name__ == "__main__":                "error": "No cube state provided"

    app.run(host="0.0.0.0", port=5000, debug=True)            }), 400
        
        if len(cube_state) != 54:
            print(f"❌ Invalid length: expected 54, got {len(cube_state)}")
            return jsonify({
                "success": False,
                "error": f"Invalid cube state length. Expected 54 characters, got {len(cube_state)}"
            }), 400
        
        # Check if state contains only valid characters
        valid_chars = set('URFDLB')
        invalid_chars = [c for c in cube_state if c not in valid_chars]
        if invalid_chars:
            print(f"❌ Invalid characters found: {set(invalid_chars)}")
            return jsonify({
                "success": False,
                "error": f"Invalid characters in cube state: {', '.join(set(invalid_chars))}. Only U, R, F, D, L, B are allowed"
            }), 400
        
        # Validate color distribution (9 of each color)
        color_counts = {color: cube_state.count(color) for color in valid_chars}
        print(f"🎨 Color distribution: {color_counts}")
        invalid_colors = [color for color, count in color_counts.items() if count != 9]
        
        if invalid_colors:
            print(f"❌ Invalid color distribution: {invalid_colors}")
            return jsonify({
                "success": False,
                "error": f"Invalid color distribution. Each color must appear exactly 9 times. Issues with: {', '.join(invalid_colors)}",
                "color_counts": color_counts
            }), 400
        
        # Check center pieces (positions 4, 13, 22, 31, 40, 49)
        expected_centers = {
            4: 'U',   # U face center
            13: 'R',  # R face center  
            22: 'F',  # F face center
            31: 'D',  # D face center
            40: 'L',  # L face center
            49: 'B'   # B face center
        }
        
        center_errors = []
        for pos, expected in expected_centers.items():
            if cube_state[pos] != expected:
                center_errors.append(f"Position {pos} should be {expected}, got {cube_state[pos]}")
        
        if center_errors:
            print(f"❌ Center piece errors: {center_errors}")
            return jsonify({
                "success": False,
                "error": "Invalid center pieces",
                "center_errors": center_errors
            }), 400
        
        print("✅ All validations passed, attempting to solve...")
        
        # Solve the cube using Kociemba algorithm
        try:
            print(f"🔍 Calling kociemba.solve() with state: {cube_state}")
            solution = kociemba.solve(cube_state)
            print(f"🎯 Kociemba returned: {solution}")
            
            # Count moves
            moves = solution.split() if solution else []
            move_count = len(moves)
            
            # Check if cube is already solved
            if not solution or solution == "":
                print("✅ Cube is already solved!")
                return jsonify({
                    "success": True,
                    "already_solved": True,
                    "message": "Cube is already in solved state!",
                    "solution": "",
                    "moves": 0,
                    "state": cube_state
                })
            
            print(f"✅ Solution found: {solution} ({move_count} moves)")
            return jsonify({
                "success": True,
                "solution": solution,
                "moves": move_count,
                "move_list": moves,
                "state": cube_state,
                "algorithm": "Kociemba Two-Phase Algorithm"
            })
            
        except Exception as solve_error:
            print(f"❌ Kociemba solve error: {solve_error}")
            print(f"❌ Error type: {type(solve_error)}")
            
            # Check if it's the common "invalid cubestring" error
            if "cubestring is invalid" in str(solve_error).lower() or "invalid" in str(solve_error).lower():
                return jsonify({
                    "success": False,
                    "error": "Invalid cube configuration",
                    "details": "The cube state represents an impossible configuration. This usually happens when colors are placed manually without following Rubik's cube constraints. Try using a scrambled solved cube or loading a valid cube state.",
                    "suggestion": "Use the 'Load Cube State' feature with a valid scrambled state, or start with a solved cube and apply valid moves."
                }), 400
            else:
                return jsonify({
                    "success": False,
                    "error": f"Failed to solve cube: {str(solve_error)}",
                    "details": "The cube state might be invalid or unsolvable"
                }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate_cube():
    """
    Validate a cube state without solving it
    
    Expected JSON payload:
    {
        "state": "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    }
    
    Returns validation results
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "valid": False,
                "error": "No JSON data provided"
            }), 400
        
        cube_state = data.get('state', '').strip().upper()
        
        validation_result = {
            "valid": True,
            "state": cube_state,
            "checks": {}
        }
        
        # Length check
        if len(cube_state) != 54:
            validation_result["valid"] = False
            validation_result["checks"]["length"] = {
                "passed": False,
                "expected": 54,
                "actual": len(cube_state)
            }
        else:
            validation_result["checks"]["length"] = {"passed": True}
        
        # Character check
        valid_chars = set('URFDLB')
        invalid_chars = [c for c in cube_state if c not in valid_chars]
        if invalid_chars:
            validation_result["valid"] = False
            validation_result["checks"]["characters"] = {
                "passed": False,
                "invalid_chars": invalid_chars
            }
        else:
            validation_result["checks"]["characters"] = {"passed": True}
        
        # Color distribution check
        color_counts = {color: cube_state.count(color) for color in valid_chars}
        invalid_counts = {color: count for color, count in color_counts.items() if count != 9}
        if invalid_counts:
            validation_result["valid"] = False
            validation_result["checks"]["color_distribution"] = {
                "passed": False,
                "invalid_counts": invalid_counts,
                "all_counts": color_counts
            }
        else:
            validation_result["checks"]["color_distribution"] = {"passed": True}
        
        # Center pieces check
        expected_centers = {4: 'U', 13: 'R', 22: 'F', 31: 'D', 40: 'L', 49: 'B'}
        center_errors = {}
        for pos, expected in expected_centers.items():
            if len(cube_state) > pos and cube_state[pos] != expected:
                center_errors[pos] = {"expected": expected, "actual": cube_state[pos]}
        
        if center_errors:
            validation_result["valid"] = False
            validation_result["checks"]["centers"] = {
                "passed": False,
                "errors": center_errors
            }
        else:
            validation_result["checks"]["centers"] = {"passed": True}
        
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({
            "valid": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Rubik's Cube Solver API",
        "algorithm": "Kociemba Two-Phase Algorithm"
    })

@app.route('/api/info', methods=['GET'])
def api_info():
    """Get API information and usage"""
    return jsonify({
        "service": "Rubik's Cube Solver API",
        "version": "1.0.0",
        "algorithm": "Kociemba Two-Phase Algorithm",
        "endpoints": {
            "/api/solve": {
                "method": "POST",
                "description": "Solve a Rubik's cube",
                "payload": {"state": "54-character cube state string"}
            },
            "/api/validate": {
                "method": "POST", 
                "description": "Validate a cube state",
                "payload": {"state": "54-character cube state string"}
            },
            "/api/health": {
                "method": "GET",
                "description": "Health check"
            },
            "/api/info": {
                "method": "GET",
                "description": "API information"
            }
        },
        "cube_notation": {
            "format": "UFRBLD order (54 characters)",
            "faces": {
                "U": "Up (White) - positions 0-8",
                "R": "Right (Red) - positions 9-17", 
                "F": "Front (Green) - positions 18-26",
                "D": "Down (Yellow) - positions 27-35",
                "L": "Left (Orange) - positions 36-44",
                "B": "Back (Blue) - positions 45-53"
            },
            "centers": "Positions 4, 13, 22, 31, 40, 49 must be U, R, F, D, L, B respectively"
        }
    })

if __name__ == '__main__':
    print("🧩 Rubik's Cube Solver API Starting...")
    print("📡 Endpoints:")
    print("   POST /api/solve - Solve a cube")
    print("   POST /api/validate - Validate cube state")
    print("   GET  /api/health - Health check")
    print("   GET  /api/info - API information")
    print("🌐 CORS enabled for all origins")
    print("🚀 Server running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)