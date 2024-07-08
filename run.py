from api_handler import create_handler


# Create handler
handler = create_handler(name="opentriviadb")
# Get categories
cats, ids = handler.get_categories(return_ids=True)
print("opentriviadb")
print(ids)
print(cats)

# Create handler
handler = create_handler(name="thetriviaapi")
# Get categories
cats, ids = handler.get_categories(return_ids=True)
print("thetriviaapi")
print(ids)
print(cats)