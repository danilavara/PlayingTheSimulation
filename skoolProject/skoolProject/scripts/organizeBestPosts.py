import json
from datetime import datetime, timedelta
from dateutil import parser

def load_and_process_data(file_path):
    # Load data from the JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Get current date and calculate the date 7 days ago
    current_date = datetime.now()
    date_limit = current_date - timedelta(days=7)

    # Define category codes to exclude || Categories excluded: 'Anuncios' and 'Fianzas'
    exclude_categories = {'0c6a5f92ba594ba39b64fe26180f1f4b', '065dfd698bc94fe28c941b047eee1ffc'}

    # Exclude posts with 'Mejores posts de la semana' in the title
    exclude_title_phrase = 'Mejores posts de la semana'

    # Category mapping
    category_mapping = {
        'f02b7bac3b22490492fb6cac6fa2510e': 'Wins',
        '9aeac4f45ffd43e6a9ffb99856017ff0': 'La Oficina',
        '0c909393bcb444b089199a8b64f2d14a': 'Afterwork',
        '2cc5a56747d74862b6587e948cfa8679': 'Intros',
        '7842417fd94b49eab92e7525aa8e131c': 'Retos',
        '91060358bc544315bf63d4079c15054a': 'Elevator Pitch',
        '5875bca6326c4f4d9e7833674e1f21f3': 'Trabajo'
    }

    # Filter posts within the last 7 days and not in excluded categories
    recent_posts = [
        post for post in data
        if make_naive(parser.parse(post['created'])) >= date_limit
        and post.get('categoria') not in exclude_categories
        and exclude_title_phrase not in post.get('titulo', '')
    ]

    # Transform the categoria field using the mapping
    for post in recent_posts:
        post['categoria'] = category_mapping.get(post['categoria'], post['categoria'])


    # Sort the posts by 'likes' in descending order
    sorted_posts = sorted(recent_posts, key=lambda x: x['likes'], reverse=True)

    # Return the top 10 posts with the most likes
    return sorted_posts[:10]

def make_naive(dt):
    # Convert an aware datetime to naive. Assumes the datetime is in local time.
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        return dt.replace(tzinfo=None)
    return dt

def save_to_file(data, output_file):
    # Save the data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Usage
file_path = 'output.json'  # Adjust the path if needed
output_file = 'top_posts.json'  # Output file for the top posts
top_posts = load_and_process_data(file_path)
save_to_file(top_posts, output_file)
print(f"Top posts saved to {output_file}.")
