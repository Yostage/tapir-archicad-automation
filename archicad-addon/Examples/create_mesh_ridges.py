import aclib

# A mesh that displays only user-defined ridges (contour level lines),
# the drawing-set look — no triangulation. Exercises the new ridges/showLines fields.
aclib.RunTapirCommand (
    'CreateMeshes', {
        'meshesData': [
            {
                'level': 0.0,
                'skirtType': 'SolidBodyWithSkirt',
                'skirtLevel': 5.0,
                'ridges': 'UserDefined',
                'showLines': True,
                'polygonCoordinates': [
                    {'x': 0.0,  'y': 0.0,  'z': 0.0},
                    {'x': 20.0, 'y': 0.0,  'z': 0.0},
                    {'x': 20.0, 'y': 15.0, 'z': 0.0},
                    {'x': 0.0,  'y': 15.0, 'z': 0.0}
                ],
                'sublines': [
                    {'coordinates': [{'x': x, 'y': y, 'z': y * 0.2} for x in range(0, 21, 4)]}
                    for y in range(0, 16, 3)
                ]
            }
        ]
    })
