import aclib

# Chain create-then-open so the example doesn't depend on a pre-existing view.
created = aclib.RunTapirCommand (
    'CreateView', {
        'name': 'TapirOpenViewTest',
        'saveZoom': True
    })
navigatorItemId = created['navigatorItemId']

result = aclib.RunTapirCommand ('OpenView', {'navigatorItemId': navigatorItemId})
print(result)
