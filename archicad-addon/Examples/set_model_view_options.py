import aclib

# Apply a Model View Options set by name. Uses the first available MVO from the
# project so the example is self-contained; prints the result either way.
available = aclib.RunTapirCommand ('GetModelViewOptions', {})['modelViewOptions']
print('Available Model View Options:', [mvo['name'] for mvo in available])

if available:
    result = aclib.RunTapirCommand ('SetModelViewOptions', {'modelViewOptionsName': available[0]['name']})
    print(result)
else:
    print('No Model View Options in this project to apply.')
