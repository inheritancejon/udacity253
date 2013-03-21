from django.shortcuts import render

# View: Render template passing simple dict with our message
def index(request):

	# Create message
	message = "Hello, Udacity!"

	# Create a dictionary of data to be passed
	d=dict(message=message)

	# Render the template, passing along the dictionary of data
	return render(request, "1_appengine/index.html", d)

