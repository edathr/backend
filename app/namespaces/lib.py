from app.models import LiveReview, OldReview


def get_average_rating(asin):
    """Get avg_rating from SQL as the source of truth"""

    old_sum, old_count = OldReview.get_sum_count_rating(asin)
    new_sum, new_count = LiveReview.get_sum_count_rating(asin)

    if old_count + new_count == 0:
        return 0

    return round((old_sum + new_sum) / (old_count + new_count), 1)

# TODO: code this shit



def sanitize(e):

    if not e.get("author", None):
        e["author"] = "Author not found"

    if not e.get("title", None):
        e["title"] = "Title not found"

    if not e.get("description", None):
        e["description"] = "Description does not exist"

    if not e.get("genres", None):
        e["genres"] = ["Genres data does not exist"]

    e["avg_rating"] = get_average_rating(e["asin"])


    return e


def parse_gbook(book_obj):
    output = dict()
    try:
        for e in book_obj["volumeInfo"]["industryIdentifiers"]:
            print("e", e)
            if e["type"] == "ISBN_10":
                output["asin"] = e["identifier"]

    except Exception as e:
        print(e)
        hash_obj = hash(str(book_obj["volumeInfo"]))
        artificial_asin = str(max(hash_obj, -hash_obj))[:10]
        print("Created Artificial Asin", artificial_asin)
        output["asin"] = artificial_asin

    try:

        output["title"] = book_obj["volumeInfo"]["title"]

    except Exception as e:
        print(e)
        output["title"] = None

    try:
        output["description"] = book_obj["volumeInfo"]["description"]

    except Exception as e:
        print(e)
        output["description"] = None

    try:
        output["imUrl"] = book_obj["volumeInfo"]["imageLinks"]["thumbnail"]

    except Exception as e:
        print(e)
        output["imUrl"] = None

    try:
        output["author"] = book_obj["volumeInfo"]["authors"][0]

    except Exception as e:
        print(e)
        output["author"] = None

    try:
        output["genres"] = book_obj["volumeInfo"]["categories"]

    except Exception as e:
        print(e)
        output["genres"] = None


    return output




PROJECTION = {"asin": 1, "title": 1, "description": 1, "imUrl": 1, "genres": 1, "pricing": 1}
