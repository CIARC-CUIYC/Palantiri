from flask import Blueprint, request, jsonify, Response
from werkzeug.exceptions import BadRequest

bp = Blueprint("palantiri", __name__, url_prefix="/palantiri")

QUOTE_RESPONSES: dict[str, str] = {
    "The Beacons of Minas Tirith! The Beacons are lit! Gondor calls for aid.":
        "And Rohan will answer!",
    "You shall not pass!": "Fly, you fools!",
    "What about second breakfast?": "I don’t think he knows about second breakfast, Pip.",
}


@bp.route("/", methods=["POST"])
def palantiri_reply() -> Response:
    """
    Respond to a known Tolkien quote with a matching reply.

    Request JSON must include:
        {
            "quote": "<a known Tolkien quote>"
        }

    Returns:
        Response: A JSON reply with a key "reply".
    """
    data = request.get_json()
    if not data or "quote" not in data:
        raise BadRequest("Missing 'quote' in request body.")

    quote = data["quote"].strip()
    reply = QUOTE_RESPONSES.get(quote)

    if reply:
        return jsonify({"reply": reply})
    else:
        return jsonify({
            "reply": "The halls of memory are silent... I know not that line."
        })
