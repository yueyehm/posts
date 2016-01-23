import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from posts import app
from .database import session

# @app.route("/api/posts", methods=["GET"])
# @decorators.accept("application/json")
# def posts_get():
#     """ Get a list of posts """

#     # Get the posts from the database
#     posts = session.query(models.Post).order_by(models.Post.id)

#     # Convert the posts to JSON and return a response
#     data = json.dumps([post.as_dictionary() for post in posts])
#     return Response(data, 200, mimetype="application/json")
    
@app.route("/api/posts", methods=["GET"])
@decorators.accept("application/json")
def posts_get():
    """ Get a list of posts """
    # Get the querystring arguments
    title_like = request.args.get("title_like")
    body_like = request.args.get("body_like")

    # Get and filter the posts from the database
    posts = session.query(models.Post)
    if title_like:
        posts = posts.filter(models.Post.title.contains(title_like))
    if body_like:
        posts = posts.filter(models.Post.body.contains(body_like))
    posts = posts.order_by(models.Post.id)

    # Convert the posts to JSON and return a response
    data = json.dumps([post.as_dictionary() for post in posts])
    return Response(data, 200, mimetype="application/json")

    
@app.route("/api/posts/<int:id>", methods=["GET"])
def post_get(id):
    """ Single post endpoint """
    # Get the post from the database
    post = session.query(models.Post).get(id)

    # Check whether the post exists
    # If not return a 404 with a helpful message
    if not post:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Return the post as JSON
    data = json.dumps(post.as_dictionary())
    return Response(data, 200, mimetype="application/json")    
    
@app.route("/api/posts/<int:id>", methods=["DELETE"])
def post_delete(id):
    """ Single post endpoint """
    # Get the post from the database
    post = session.query(models.Post).get(id)

    # Check whether the post exists
    # If not return a 404 with a helpful message
    if not post:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Delete the post
    session.delete(post)
    session.commit()
    message = "Post id {} deleted.".format(id)
    data = json.dumps({"message":message})
    return Response(data, 200, mimetype="application/json")

@app.route("/api/posts", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def posts_post():
    """ Add a new post """
    data = request.json
    
    # Try to validate data
    try:
        validate(data, post_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    # Add the post to the database
    post = models.Post(title=data["title"], body=data["body"])
    session.add(post)
    session.commit()

    # Return a 201 Created, containing the post as JSON and with the
    # Location header set to the location of the post
    data = json.dumps(post.as_dictionary())
    headers = {"Location": url_for("post_get", id=post.id)}
    return Response(data, 201, headers=headers,
                    mimetype="application/json")

@app.route("/api/posts/<int:id>", methods=["PUT"])
@decorators.accept("application/json")
@decorators.require("application/json")
def post_put(id):
    """ Construct the post """
    data = request.json
    
    """ Try to validate data """
    try:
        validate(data, post_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
    
    post = models.Post(id=id, title=data["title"], body=data["body"])
    
    """ Single post endpoint """
    # Get the post from the database
    postInDB = session.query(models.Post).get(id)

    # Check whether the post exists
    # If not return a 404 with a helpful message
    if not postInDB:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Update the post
    postInDB.title = post.title
    postInDB.body = post.body
    session.commit()
    
    # Return a 202 Accepted, containing the post as JSON and with the
    # Location header set to the location of the post
    data = json.dumps(post.as_dictionary())
    headers = {"Location": url_for("post_get", id=post.id)}
    return Response(data, 202, headers=headers,
                    mimetype="application/json")
    


post_schema = {
    "properties": {
        "title" : {"type" : "string"},
        "body": {"type": "string"}
    },
    "required": ["title", "body"]
}