import aclib

# Switch to a perspective view looking at the origin from an elevated corner.
# Requires a 3D window to be available.
result = aclib.RunTapirCommand (
    'Set3DProjection', {
        'cameraPosition': {'x': -30.0, 'y': -30.0, 'z': 20.0},
        'targetPosition': {'x': 0.0,   'y': 0.0,   'z': 0.0},
        'viewCone': 1.0
    })
print(result)
