from django.shortcuts import render_to_response

# Render template passing simple dict with our message
def index(request):
	message = "Hello, Udacity!"
	d=dict(message=message)
	return render_to_response("1_appengine/index.html", d)

