import aclib

# Save the current window as a new View Map item, then read its settings back.
result = aclib.RunTapirCommand (
    'CreateView', {
        'name': 'TapirTestView',
        'saveZoom': True
    })
print(result)

navigatorItemId = result['navigatorItemId']
viewSettings = aclib.RunTapirCommand ('GetViewSettings', {'navigatorItemIds': [{'navigatorItemId': navigatorItemId}]})
print(viewSettings)
