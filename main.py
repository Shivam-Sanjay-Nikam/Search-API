from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

API_URL = 'https://app.ylytic.com/ylytic/test'


def format_date(date_str, input_format, output_format):
    date_obj = datetime.strptime(date_str, input_format)
    return date_obj.strftime(output_format)


def convert_month_to_number(month_str):
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_num = str(month_names.index(month_str) + 1).zfill(2)
    return month_num


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route("/search", methods=['GET'])
def search():
    response = requests.get(API_URL)
    comments = response.json()

    search_params = {
        'search_author': request.args.get('search_author'),
        'at_from': request.args.get('at_from'),
        'at_to': request.args.get('at_to'),
        'like_from': request.args.get('like_from'),
        'like_to': request.args.get('like_to'),
        'reply_from': request.args.get('reply_from'),
        'reply_to': request.args.get('reply_to'),
        'search_text': request.args.get('search_text')
    }

    common_output_format = "%d%m%Y %H:%M:%S"

    # Format and convert at_from and at_to dates into common format
    if search_params["at_from"]:
        formatted_at_from = format_date(search_params["at_from"], "%Y-%d-%b", common_output_format)
        search_params["at_from"] = formatted_at_from

    if search_params["at_to"]:
        formatted_at_to = format_date(search_params["at_to"], "%Y-%d-%b", common_output_format)
        search_params["at_to"] = formatted_at_to

    filtered_comments = filter_comments(comments['comments'], search_params)

    return jsonify(filtered_comments)


def filter_comments(comments, search_params):
    filtered_comments = []

    for comment in comments:
        # Filter by author name
        if search_params["search_author"] and search_params["search_author"] not in comment['author']:
            continue

        # Filter by date range
        if search_params["at_from"]:
            at_from = datetime.strptime(search_params["at_from"], "%d%m%Y %H:%M:%S")
            comment_date = datetime.strptime(comment['at'], "%a, %d %b %Y %H:%M:%S %Z")
            if comment_date < at_from:
                continue

        if search_params["at_to"]:
            at_to = datetime.strptime(search_params["at_to"], "%d%m%Y %H:%M:%S")
            comment_date = datetime.strptime(comment['at'], "%a, %d %b %Y %H:%M:%S %Z")
            if comment_date > at_to:
                continue

        # Filter by like count range
        if search_params["like_from"] and comment['like'] < int(search_params["like_from"]):
            continue

        if search_params["like_to"] and comment['like'] > int(search_params["like_to"]):
            continue

        # Filter by reply count range
        if search_params["reply_from"] and comment['reply'] < int(search_params["reply_from"]):
            continue
        if search_params["reply_to"] and comment['reply'] > int(search_params["reply_to"]):
            continue

        # Filter by search text
        if search_params["search_text"] and search_params["search_text"].lower() not in comment['text'].lower():
            continue

        filtered_comments.append(comment)

    return filtered_comments


if __name__ == '__main__':
    app.run(debug=True)
