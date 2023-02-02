from django.shortcuts import render
from .models import Picture
from .forms import PictureForm
from django.views.decorators.csrf import csrf_protect


# Create your views here.
def index(request):
    pictures = Picture.objects.all()
    ctx = {'pictures': pictures}
    return render(request, 'pictures/index.html', ctx)


@csrf_protect
def loadPicture(request):
    context = dict(form=PictureForm())
    if request.method == 'POST':
        form = PictureForm(request.POST, request.FILES)
        context['posted'] = form.instance
        if form.is_valid():
            form.save()

    return render(request, 'pictures/load.html', context)
